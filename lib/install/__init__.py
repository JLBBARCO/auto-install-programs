import os
import subprocess
import re
import shutil
import time
import importlib
import sys
try:
    from lib.json import _resource_path, ensure_repo_file, read_json
    from lib import log, system
except ModuleNotFoundError:
    from lib.json import _resource_path, ensure_repo_file, read_json
    from lib import log, system

try:
    import psutil
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
    try:
        psutil = importlib.import_module('psutil')
    except Exception:
        psutil = None

# PyInstaller packages data files into a temporary folder during execution.
# Use this helper to get the absolute path to bundled resources whether the
# application is running from source or from a PyInstaller-built executable.

OFFICE_SETUP_REPO_PATH = "install/windows/office/setup.exe"
OFFICE_SETTINGS_REPO_PATH = "install/windows/office/settings.xml"

WINDOWS_ADMIN_REQUIRED_IDS = {
    "adobe.acrobat.reader.64-bit",
}

def update():
    system_name = system.nameSO()
    if system_name == 'Windows':
        try:
            _run_command('winget update Microsoft.AppInstaller --accept-source-agreements --accept-package-agreements >nul 2>&1')
        except Exception as error:
            return log.log(f'Failed of update Microsoft.AppInstaller: {error}', level='ERROR')
        return log.log('Successfully of update Microsoft.AppInstaller', 'INFO')
    elif system_name == 'Linux':
        installer = _resolve_linux_installer()
        if installer == 'apt':
            try:
                _run_command('sudo apt update')
            except Exception as error:
                return log.log(f'Failed of update apt: {error}', level='ERROR')
            return log.log('Successfully of update apt', 'INFO')
        elif installer == 'dnf':
            try:
                _run_command('sudo dnf check-update')
            except Exception as error:
                return log.log(f'Failed of update dnf: {error}', level='ERROR')
            return log.log('Successfully of update dnf', 'INFO')
        elif installer == 'pacman':
            try:
                _run_command('sudo pacman -Sy')
            except Exception as error:
                return log.log(f'Failed of update pacman: {error}', level='ERROR')
            return log.log('Successfully of update pacman', 'INFO')
    elif system_name == 'MacOS':
            try:
                _run_command('brew upgrade --quiet')
            except Exception as error:
                return log.log(f'Failed of update brew: {error}', level='ERROR')
            return log.log('Successfully of update brew', 'INFO')

def _filter_install_output(output: str) -> str:
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    clean = ansi_escape.sub('', output)
    lines = clean.splitlines()
    kept_lines = []
    removed_count = 0
    progress_re = re.compile(r'\b\d{1,3}%\b')

    for line in lines:
        if progress_re.search(line) and len(line.strip()) < 120:
            removed_count += 1
            continue
        if len(line.strip()) > 0 and set(line.strip()) <= set('.-') and len(line.strip()) < 40:
            removed_count += 1
            continue
        kept_lines.append(line)

    if removed_count:
        kept_lines.append(f"[{removed_count} progress updates suppressed]")

    return "\n".join(kept_lines).strip()


def _run_command(command: str) -> str:
    process = subprocess.run(command, capture_output=True, text=True, shell=True)
    raw_output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
    filtered_output = _filter_install_output(raw_output)

    if process.returncode != 0:
        log.log(f'Command failed [{process.returncode}]: {command}', level="ERROR")
        log.log(filtered_output or f"(raw output suppressed; {len(raw_output)} bytes)", level="ERROR")
    else:
        log.log(f'Command completed: {command}', level="INFO")
        if filtered_output:
            log.log(filtered_output, level="INFO")

    return filtered_output


def _resolve_linux_installer() -> str:
    if shutil.which("apt"):
        return "apt"
    if shutil.which("dnf"):
        return "dnf"
    if shutil.which("pacman"):
        return "pacman"
    return ""


def _tokenize_program_signature(program_name: str, program_id: str):
    signature = f"{program_name} {program_id}".strip().lower()
    if not signature:
        return []

    raw_tokens = re.findall(r"[a-z0-9]+", signature)
    ignored = {
        "microsoft", "windows", "desktop", "installer", "install", "stable",
        "program", "programs", "tool", "tools", "reader", "runtime", "environment",
        "soft", "open", "community", "edition", "official", "app", "apps",
    }

    tokens = []
    for token in raw_tokens:
        if len(token) < 4:
            continue
        if token in ignored:
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens


def _detect_running_program_instances(program_name: str, program_id: str) -> int:
    """Count matching running processes without terminating user applications."""
    if system.nameSO() != "Windows":
        return 0
    if psutil is None:
        log.log('psutil is unavailable; skipping running-process check.', level="WARNING")
        return 0

    tokens = _tokenize_program_signature(program_name, program_id)
    if not tokens:
        return 0

    matched_count = 0
    own_pid = os.getpid()

    for process in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            pid = process.info.get("pid")
            if pid in (None, own_pid):
                continue

            name = (process.info.get("name") or "").lower()
            exe = (process.info.get("exe") or "").lower()
            cmdline = " ".join(process.info.get("cmdline") or []).lower()
            process_signature = f"{name} {exe} {cmdline}"

            # Require at least one strong token hit to avoid matching unrelated apps.
            if not any(token in process_signature for token in tokens):
                continue

            matched_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as error:
            log.log(f'Error while checking running process state: {error}', level="WARNING")

    return matched_count


def _install_program_id(program_id: str, program_name: str = "") -> str:
    if not program_id:
        return "Skipped empty program id"

    running_instances = _detect_running_program_instances(program_name, program_id)
    if running_instances:
        log.log(
            f'Found {running_instances} running instance(s) for {program_name or program_id}; continuing without closing them.',
            level="WARNING",
        )

    os_name = system.nameSO()
    if os_name == "Windows":
        winget_args = [
            "install",
            "--id",
            program_id,
            "-e",
            "--accept-source-agreements",
            "--accept-package-agreements",
        ]

        requires_admin = program_id.lower() in WINDOWS_ADMIN_REQUIRED_IDS
        if requires_admin:
            return _run_winget_with_admin(winget_args)

        process = subprocess.run(
            ["winget", *winget_args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            shell=False,
        )
        output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
        normalized_output = _filter_install_output(output)

        if process.returncode != 0 and _looks_like_admin_error(output):
            log.log(f'Admin privileges required for {program_id}; retrying with elevation.', level="WARNING")
            return _run_winget_with_admin(winget_args)

        return normalized_output

    if os_name == "Linux":
        installer = _resolve_linux_installer()
        if installer == "apt":
            return _run_command(f'sudo apt-get install -y "{program_id}"')
        if installer == "dnf":
            return _run_command(f'sudo dnf install -y "{program_id}"')
        if installer == "pacman":
            return _run_command(f'sudo pacman -S --noconfirm "{program_id}"')
        return "No supported Linux package manager detected (apt/dnf/pacman)."

    if os_name == "MacOS":
        output = _run_command(f'brew install --cask "{program_id}"')
        # Fallback for formula-only packages.
        if "No Cask" in output or "Error:" in output:
            return _run_command(f'brew install "{program_id}" --quiet')
        return output

    return f"Unsupported OS: {os_name}"


def _looks_like_admin_error(output: str) -> bool:
    lowered = str(output or "").lower()
    return any(
        token in lowered
        for token in (
            "administrator",
            "admin",
            "access is denied",
            "0x8a15000f",
            "0x80070005",
        )
    )


def _run_winget_with_admin(winget_args: list[str]) -> str:
    escaped_args = " ".join(
        [f'\"{arg}\"' if " " in arg or '"' in arg else arg for arg in winget_args]
    )
    ps_script = (
        "$process = Start-Process -FilePath 'winget' "
        f"-ArgumentList '{escaped_args}' "
        "-Verb RunAs -PassThru -Wait; "
        "Write-Output ('ExitCode=' + $process.ExitCode)"
    )

    process = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        shell=False,
    )

    output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
    normalized_output = _filter_install_output(output)
    if not normalized_output:
        return "Elevated winget process completed."
    return normalized_output


def _create_bios_shortcut() -> str:
    if system.nameSO() != 'Windows':
        return 'BIOS shortcut is currently supported only on Windows.'

    try:
        start_menu_programs = os.path.join(
            os.environ.get('APPDATA', ''),
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
        )
        if not start_menu_programs:
            return 'Could not resolve Start Menu path.'

        os.makedirs(start_menu_programs, exist_ok=True)
        shortcut_path = os.path.join(start_menu_programs, 'Path to BIOS.lnk')

        ps_script = (
            "$shell = New-Object -ComObject WScript.Shell; "
            f"$shortcut = $shell.CreateShortcut('{shortcut_path}'); "
            "$shortcut.TargetPath = \"$env:SystemRoot\\System32\\shutdown.exe\"; "
            "$shortcut.Arguments = '/r /fw /t 1'; "
            "$shortcut.WorkingDirectory = \"$env:SystemRoot\\System32\"; "
            "$shortcut.IconLocation = \"$env:SystemRoot\\System32\\shell32.dll,27\"; "
            "$shortcut.Save();"
        )

        process = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            shell=False,
        )

        if process.returncode != 0:
            stderr = (process.stderr or '').strip()
            return f'Failed to create BIOS shortcut: {stderr or "unknown error"}'

        return 'Path to BIOS shortcut created in Start Menu.'
    except Exception as error:
        return f'Failed to create BIOS shortcut: {error}'


def _run_custom_function(function_key: str) -> str:
    normalized_key = str(function_key).strip().lower()
    if not normalized_key:
        return "Skipped empty function key"

    if normalized_key == 'dark-mode':
        if system.nameSO() != 'Windows':
            return 'Dark mode function is currently supported only on Windows.'
        try:
            _run_command(
                'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
                '/v AppsUseLightTheme /t REG_DWORD /d 0 /f >nul 2>&1'
            )
            _run_command(
                'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" '
                '/v SystemUsesLightTheme /t REG_DWORD /d 0 /f >nul 2>&1'
            )
            return 'Dark mode applied successfully.'
        except Exception as error:
            return f'Failed to apply dark mode: {error}'

    if normalized_key == 'path-to-bios':
        return _create_bios_shortcut()

    return f'Unsupported custom function: {normalized_key}'


def install_program(program, selected_program_ids=None):
    data = read_json(program)
    programs = data.get('programs', []) if data else []

    # None means "execute all entries in this category" (legacy behavior).
    selected_id_set = None
    selected_function_set = None

    if selected_program_ids is not None:
        selected_id_set = set()
        selected_function_set = set()

        for selected_entry in selected_program_ids:
            if isinstance(selected_entry, dict):
                selected_id = str(selected_entry.get('id', '')).strip()
                selected_function = str(selected_entry.get('function', '')).strip()
                if selected_id:
                    selected_id_set.add(selected_id)
                if selected_function:
                    selected_function_set.add(selected_function)
            else:
                selected_id = str(selected_entry).strip()
                if selected_id:
                    selected_id_set.add(selected_id)

    if not programs:
        return f"No programs found for category {program}."

    outputs = []
    installed_count = 0

    for program_entry in programs:
        if not isinstance(program_entry, dict):
            continue

        name = str(program_entry.get("name", "")).strip()
        program_id = str(program_entry.get("id", "")).strip()
        program_function = str(program_entry.get("function", "")).strip()

        if selected_id_set is not None or selected_function_set is not None:
            id_selected = bool(program_id and selected_id_set is not None and program_id in selected_id_set)
            function_selected = bool(
                program_function and selected_function_set is not None and program_function in selected_function_set
            )
            if not id_selected and not function_selected:
                continue

        if not program_id and not program_function:
            continue

        if program_id.lower() == 'path-to-bios' and not program_function:
            program_function = 'path-to-bios'

        if program_function:
            log.log(f'Executing function [{program}] {name} ({program_function})', level="INFO")
            output = _run_custom_function(program_function)
        else:
            log.log(f'Installing [{program}] {name} ({program_id})', level="INFO")
            output = _install_program_id(program_id, name)

        outputs.append(f"{name}: {output}")
        installed_count += 1

        time.sleep(3)

    if installed_count == 0:
        message = f"No active selected programs to install for category {program}."
        log.log(message, level="INFO")
        return message

    summary = f"Installed {installed_count} program(s) for category {program}."
    log.log(summary, level="INFO")
    return "\n".join([summary] + outputs)

def drivers(selected_program_ids=None):
    return install_program("drivers", selected_program_ids)

def essentials(selected_program_ids=None):
    return install_program("essentials", selected_program_ids)

def server(selected_program_ids=None):
    return install_program("server", selected_program_ids)

def office(selected_program_ids=None):
    data = read_json("office")
    programs = data.get('programs', []) if data else []
    selected_set = None if selected_program_ids is None else set(selected_program_ids)

    if not programs:
        return "No programs found for category office."

    outputs = []
    installed_count = 0

    for program_entry in programs:
        if not isinstance(program_entry, dict):
            continue

        name = str(program_entry.get("name", "")).strip()
        program_id = str(program_entry.get("id", "")).strip()

        if selected_set is not None and program_id not in selected_set:
            continue

        log.log(f'Installing [office] {name} ({program_id})', level="INFO")

        output = _install_program_id(program_id, name)

        outputs.append(f"{name}: {output}")
        installed_count += 1
        time.sleep(3)

    if installed_count == 0:
        message = "No active selected programs to install for category office."
        log.log(message, level="INFO")
        return message

    summary = f"Installed {installed_count} program(s) for category office."
    log.log(summary, level="INFO")
    return "\n".join([summary] + outputs)

def development(selected_program_ids=None):
    return install_program("development", selected_program_ids)

def games(selected_program_ids=None):
    return install_program("games", selected_program_ids)

def screen(selected_program_ids=None):
    return install_program("screen", selected_program_ids)

def user(selected_program_ids=None):
    return install_program('user', selected_program_ids)

def customization(selected_program_ids=None):
    execution_summary = install_program('customization', selected_program_ids)

    if system.nameSO() != 'Windows':
        return execution_summary
    
    try:
        import lib.customizations as custom
    except ModuleNotFoundError:
        import lib.customizations as custom
    log.log('Starting startup management flow', level="INFO")

    try:
        whitelist_path = ensure_repo_file('install/windows/white_list.txt')
        log.log('Startup whitelist downloaded from repository.', level="INFO")
    except Exception as error:
        whitelist_path = _resource_path('install/windows/white_list.txt')
        log.log(f'Failed to download startup whitelist from repository; using local fallback. Error: {error}', level="WARNING")

    disableStartupMessage = custom.disable_startup_programs(whitelist_path)
    log.log(f'Disable startup: {disableStartupMessage}', level="INFO")

    save_path = _resource_path('programs.log')
    saveKeysMessage = custom.save_startup_keys(save_path)
    log.log(saveKeysMessage, level="INFO")

    enableStartupMessage = custom.enable_startup_whitelist(whitelist_path)
    log.log(enableStartupMessage, level="INFO")

    log.log('Startup management flow completed', level="INFO")
    return f"{execution_summary}\n{disableStartupMessage}\n{saveKeysMessage}\n{enableStartupMessage}"