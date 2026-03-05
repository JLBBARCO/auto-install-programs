from src.lib.externalLibs import sys, os, subprocess, re, shutil
from src.lib import log, system

# PyInstaller packages data files into a temporary folder during execution.
# Use this helper to get the absolute path to bundled resources whether the
# application is running from source or from a PyInstaller-built executable.

def _resource_path(relative_path: str) -> str:
    """Return the absolute path to *relative_path* inside the project.

    When running normally ``relative_path`` is resolved relative to the
    current working directory.  When running as a frozen app (PyInstaller)
    it resides inside ``sys._MEIPASS`` (or the equivalent extraction
    location).  This ensures that calls such as ``subprocess.run`` and
    ``shutil.copy`` can locate the files regardless of how the program is
    packaged.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.getcwd()
    return os.path.join(base, relative_path)

def install_program(program):
    # Build an absolute path to the installer script.  Use the packaging helper
    # so that the file can be found when the application is frozen by
    # PyInstaller (it ends up inside ``sys._MEIPASS``).
    bat_path = _resource_path(os.path.join('install', system.nameSO(), f"{program}.{system.installation()}"))
    log.log(f'Running installer: {bat_path}', level="INFO")

    if not os.path.exists(bat_path):
        # early exit if the file is missing; this mirrors the behaviour of the
        # shell while giving a clearer message to the log.
        msg = f'Installer not found: {bat_path}'
        log.log(msg, level="ERROR")
        return msg

    # On Windows we run the batch file via the shell.  Wrap the path in quotes
    # to ensure spaces in directory names don’t break the command.
    command = f'"{bat_path}"'
    process = subprocess.run(command, capture_output=True, text=True, shell=True)
    # Combine stdout and stderr
    raw_output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")

    # Filter out progress-like lines (e.g., repeated percent updates, ANSI escapes)
    def _filter_install_output(output: str) -> str:
        # remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        clean = ansi_escape.sub('', output)
        lines = clean.splitlines()
        kept_lines = []
        removed_count = 0
        progress_re = re.compile(r'\b\d{1,3}%\b')

        for line in lines:
            # skip lines that are simple progress indicators like '12%' or '12% downloaded'
            if progress_re.search(line) and len(line.strip()) < 120:
                removed_count += 1
                continue
            # skip very short lines with only dots or dashes that are likely progress markers
            if len(line.strip()) > 0 and set(line.strip()) <= set('.-') and len(line.strip()) < 40:
                removed_count += 1
                continue
            kept_lines.append(line)

        if removed_count:
            kept_lines.append(f"[{removed_count} progress updates suppressed]")

        return "\n".join(kept_lines).strip()

    filtered_output = _filter_install_output(raw_output)

    if process.returncode != 0:
        log.log(f'Installer {bat_path} returned code {process.returncode}', level="ERROR")
        log.log(filtered_output or f"(raw output suppressed; {len(raw_output)} bytes)", level="ERROR")
    else:
        log.log(f'Installer {bat_path} completed successfully', level="INFO")
        log.log(filtered_output or "(no meaningful output)", level="INFO")

    return filtered_output

def essentials():
    return install_program("essentials")

def server():
    return install_program("server")

def office():
    destinationPath = r"C:\Office"
    files = ['install/windows/office/settings.xml']

    os.makedirs(destinationPath, exist_ok=True)
    messages = []
    for file in files:
        # compute the real path to the file using our helper; without this the
        # file is not found when running from a PyInstaller bundle (it lives
        # under ``sys._MEIPASS/install/windows/...`` instead of the CWD).
        real_file = _resource_path(file)
        try:
            shutil.copy(real_file, destinationPath)
            messages.append(f"Successfully copied {file} to {destinationPath}")
        except Exception as error:
            messages.append(f"Failed to copy {file} to {destinationPath}. Error: {error}")
    
    result = install_program("office")
    messages.append(result)
    return "\n".join(messages)

def development():
    return install_program("development")

def games():
    return install_program("games")

def screen():
    return install_program("screen")

def customization():
    import src.lib.customizations as custom
    log.log('Starting customization flow', level="INFO")

    # 1) Run customization installers
    installProgramsMessage = install_program("customization")
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

    # 4) Reactivate entries that are in the whitelist.  When the application is
    # frozen the whitelist file is embedded in the bundle, so we must resolve
    # its real location before checking for existence.
    candidate = _resource_path(os.path.join('install','windows','white_list.txt'))
    if os.path.exists(candidate):
        whitelist_path = candidate
    else:
        # fall back to a top-level file (used during development)
        whitelist_path = _resource_path('white_list.txt')

    enableStartupMessage = custom.enable_startup_whitelist(whitelist_path)
    log.log(enableStartupMessage, level="INFO")

    # 5) Apply dark mode and restart explorer to apply visual changes
    darkModeMessage = custom.dark_mode()
    log.log(darkModeMessage, level="INFO")
    subprocess.run("taskkill /f /im explorer.exe", shell=True)
    subprocess.run("start explorer.exe", shell=True)

    log.log('Customization flow completed', level="INFO")
    return f"{installProgramsMessage}\n{disableStartupMessage}\n{saveKeysMessage}\n{enableStartupMessage}\n{darkModeMessage}"