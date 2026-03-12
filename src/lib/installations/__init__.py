import os, subprocess, re, shutil
import urllib.request
import time
try:
    from src.lib.json import _resource_path, read_json
    from src.lib import log, system
except ModuleNotFoundError:
    from lib.json import _resource_path, read_json
    from lib import log, system

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


def _install_program_id(program_id: str) -> str:
    if not program_id:
        return "Skipped empty program id"

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
        output = _install_program_id(program_id)
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
            output = _install_program_id(program_id)

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
        return "Customization is only supported on Windows."

    if not selected_program_ids:
        message = "Customization niche enabled but no active program selected; skipping customization checklist."
        log.log(message, level="INFO")
        return message
    
    try:
        import src.lib.customizations as custom
    except ModuleNotFoundError:
        import lib.customizations as custom
    log.log('Starting customization flow', level="INFO")

    # 1) Run customization installers
    installProgramsMessage = install_program("customization", selected_program_ids)
    log.log('Customization installers output captured', level="INFO")

    # 2) Disable all startup programs
    disableStartupMessage = custom.disable_startup_programs()
    log.log(f'Disable startup: {disableStartupMessage}', level="INFO")

    # 3) Save current startup keys to programs.log (overwrite)
    # write the startup key dump next to the executable rather than into
    # whatever directory the caller is currently in
    save_path = _resource_path('programs.log')
    saveKeysMessage = custom.save_startup_keys(save_path)
    log.log(saveKeysMessage, level="INFO")

    # 4) Reactivate entries listed in the repository whitelist.
    whitelist_url = "https://raw.githubusercontent.com/JLBBARCO/auto-install-programs/main/install/windows/white_list.txt"
    enableStartupMessage = custom.enable_startup_whitelist(whitelist_url)
    log.log(enableStartupMessage, level="INFO")

    # 5) Disable mouse precision (enhance pointer precision)
    mousePrecisionMessage = custom.disable_mouse_precision()
    log.log(mousePrecisionMessage, level="INFO")

    # 6) Configure power behavior for AC/DC and battery saver threshold
    powerBehaviorMessage = custom.configure_power_behavior()
    log.log(powerBehaviorMessage, level="INFO")

    # 7) Apply dark mode and restart explorer to apply visual changes
    darkModeMessage = custom.dark_mode()
    log.log(darkModeMessage, level="INFO")
    subprocess.run("taskkill /f /im explorer.exe", shell=True)
    subprocess.run("start explorer.exe", shell=True)

    log.log('Customization flow completed', level="INFO")
    return f"{installProgramsMessage}\n{disableStartupMessage}\n{saveKeysMessage}\n{enableStartupMessage}\n{mousePrecisionMessage}\n{powerBehaviorMessage}\n{darkModeMessage}"