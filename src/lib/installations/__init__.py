import os, subprocess, re, shutil
import urllib.request
import time
import importlib
import sys
try:
    from src.lib.json import _resource_path, read_json
    from src.lib import log, system
except ModuleNotFoundError:
    from lib.json import _resource_path, read_json
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

OFFICE_RAW_BASE_URL = "https://raw.githubusercontent.com/jlbbarco/auto-install-programs/main/install/windows/office"
OFFICE_SETUP_URLS = [
    f"{OFFICE_RAW_BASE_URL}/setup.exe",
    "https://officecdn.microsoft.com/pr/wsus/setup.exe",
]
OFFICE_SETTINGS_URL = f"{OFFICE_RAW_BASE_URL}/settings.xml"

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


def _close_running_program_instances(program_name: str, program_id: str) -> int:
    """Close running app processes before installation to avoid locked files."""
    if system.nameSO() != "Windows":
        return 0
    if psutil is None:
        log.log('psutil is unavailable; skipping running-process check.', level="WARNING")
        return 0

    tokens = _tokenize_program_signature(program_name, program_id)
    if not tokens:
        return 0

    killed_count = 0
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

            # Require at least one strong token hit to avoid killing unrelated apps.
            if not any(token in process_signature for token in tokens):
                continue

            process.terminate()
            try:
                process.wait(timeout=3)
            except psutil.TimeoutExpired:
                process.kill()

            killed_count += 1
            log.log(
                f'Closed running process before reinstall: PID={pid}, NAME={process.info.get("name")}',
                level="WARNING",
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as error:
            log.log(f'Error while trying to close running process: {error}', level="WARNING")

    return killed_count


def _install_program_id(program_id: str, program_name: str = "") -> str:
    if not program_id:
        return "Skipped empty program id"

    closed_instances = _close_running_program_instances(program_name, program_id)
    if closed_instances:
        log.log(
            f'Closed {closed_instances} running instance(s) for {program_name or program_id}.',
            level="INFO",
        )

    os_name = system.nameSO()
    if os_name == "Windows":
        command = f'winget install --id "{program_id}" -e --accept-source-agreements --accept-package-agreements >nul 2>&1'
        return _run_command(command)

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


def _download_file(url: str, destination_path: str) -> None:
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = response.read()
    with open(destination_path, 'wb') as output_file:
        output_file.write(payload)


def _install_office_ltsc() -> str:
    if system.nameSO() != "Windows":
        return "Office LTSC installer is only supported on Windows."

    office_dir = _resource_path(os.path.join("install", "windows", "office"))
    setup_path = os.path.join(office_dir, "setup.exe")
    settings_path = os.path.join(office_dir, "settings.xml")

    setup_downloaded = False
    last_setup_error = ""
    for setup_url in OFFICE_SETUP_URLS:
        try:
            _download_file(setup_url, setup_path)
            log.log(f"Office setup downloaded from: {setup_url}", level="INFO")
            setup_downloaded = True
            break
        except Exception as error:
            last_setup_error = str(error)
            log.log(f"Failed to download Office setup from {setup_url}: {error}", level="WARNING")

    if not setup_downloaded:
        return f"Failed to download Office setup.exe. Last error: {last_setup_error}"

    try:
        _download_file(OFFICE_SETTINGS_URL, settings_path)
        log.log(f"Office settings downloaded from: {OFFICE_SETTINGS_URL}", level="INFO")
    except Exception as error:
        return f"Failed to download Office settings.xml. Error: {error}"

    # Equivalent to: setup.exe /configure settings.xml
    command = f'"{setup_path}" /configure "{settings_path}"'
    output = _run_command(command)
    return output or "Office LTSC setup command executed."


def install_program(program, selected_program_ids=None):
    data = read_json(program)
    programs = data.get('programs', []) if data else []

    # None means "install all entries in this category" (legacy behavior).
    selected_set = None if selected_program_ids is None else set(selected_program_ids)

    if not programs:
        return f"No programs found for category {program}."

    outputs = []
    installed_count = 0

    for program_entry in programs:
        if not isinstance(program_entry, dict):
            continue
        name = str(program_entry.get("name", "")).strip()
        program_id = str(program_entry.get("id", "")).strip()

        if selected_set is not None and program_id not in selected_set:
            continue

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

        if program_id.lower() == "microsoft.office":
            output = _install_office_ltsc()
        else:
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
    if system.nameSO() != 'Windows':
        return "Startup management is only supported on Windows."
    
    try:
        import src.lib.customizations as custom
    except ModuleNotFoundError:
        import lib.customizations as custom
    log.log('Starting startup management flow', level="INFO")

    whitelist_path = _resource_path('install/windows/white_list.txt')
    disableStartupMessage = custom.disable_startup_programs(whitelist_path)
    log.log(f'Disable startup: {disableStartupMessage}', level="INFO")

    save_path = _resource_path('programs.log')
    saveKeysMessage = custom.save_startup_keys(save_path)
    log.log(saveKeysMessage, level="INFO")

    enableStartupMessage = custom.enable_startup_whitelist(whitelist_path)
    log.log(enableStartupMessage, level="INFO")

    log.log('Startup management flow completed', level="INFO")
    return f"{disableStartupMessage}\n{saveKeysMessage}\n{enableStartupMessage}"