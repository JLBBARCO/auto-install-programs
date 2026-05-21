import os
import re
import shutil
import sys
import ctypes
import urllib.request
import tempfile
from pathlib import Path
import winreg
try:
    from program.lib import log
except ModuleNotFoundError:
    from program.lib import log


GITHUB_REPO_RAW_URL = "https://raw.githubusercontent.com/JLBBARCO/programs-manager/main"


def _fetch_github_file(relative_path: str, timeout: int = 30) -> bytes:
    """Fetch a file from GitHub RAW and return its bytes."""
    url = f"{GITHUB_REPO_RAW_URL}/{relative_path}"
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def _resource_path(relative_path: str) -> str:
    """Return absolute path for WRITABLE user data (logs, cache, etc).
    
    NOT for bundled application resources - those must be fetched from GitHub.
    """
    if os.path.isabs(relative_path):
        return relative_path

    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.getcwd()
    return os.path.join(base, relative_path)


REG_PATHS = {
    "HKCU_RUN": (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKLM_RUN": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    "HKLM_WOW64": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
}


APPROVED_PATHS = {
    "HKCU_RUN": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKLM_RUN": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run",
    "HKLM_WOW64": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32",
}


LEGACY_WHITELIST_TERMS = {
    "onedrive": {"microsoftonedrive"},
    "nearby": {"nearbyshare"},
    "camo": {"camostudio"},
    "msedge": {"microsoftedgeautolaunch"},
    "nvidia": {"nvbackend", "nvcontainer", "nvidiageforceexperience", "nvidiaapp"},
    "nvinitialize": {"nvcontainer"},
    "igfxpers": {"persistence"},
    "igfxhk": {"hotkeyscmds"},
    "intelgraphics": {"intelgraphicscommandcenter"},
    "amd": {"radeonsoftware"},
    "radeon": {"radeonsoftware"},
    "lively": {"livelywpf"},
    "pcmanager": {"microsoftpcmanager"},
}


VISION_CURSOR_FILES = {
    'pointer': 'pointer.cur',
    'help': 'help.cur',
    'work': 'work.ani',
    'busy': 'busy.ani',
    'cross': 'cross.cur',
    'text': 'text.cur',
    'hand': 'handwriting.cur',
    'unavailiable': 'unavailiable.cur',
    'vert': 'vert.cur',
    'horz': 'horz.cur',
    'dgn1': 'dgn1.cur',
    'dgn2': 'dgn2.cur',
    'move': 'move.cur',
    'alternate': 'alternate.cur',
    'link': 'link.cur',
    'person': 'pin.cur',
    'pin': 'person.cur',
}


VISION_CURSOR_REGISTRY_VALUES = {
    'AppStarting': 'work.ani',
    'Arrow': 'pointer.cur',
    'Crosshair': 'cross.cur',
    'Hand': 'link.cur',
    'Help': 'help.cur',
    'IBeam': 'text.cur',
    'No': 'unavailiable.cur',
    'NWPen': 'handwriting.cur',
    'SizeAll': 'move.cur',
    'SizeNESW': 'dgn2.cur',
    'SizeNS': 'vert.cur',
    'SizeNWSE': 'dgn1.cur',
    'SizeWE': 'horz.cur',
    'UpArrow': 'alternate.cur',
    'Wait': 'busy.ani',
    'Person': 'pin.cur',
    'Pin': 'person.cur',
}


def _vision_cursor_install_path() -> Path:
    base_dir = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')))
    return base_dir / 'Programs Manager' / 'Vision Cursor Black'


def _apply_windows_cursor_scheme(target_directory: Path):
    """Apply the Vision Cursor Black scheme to Windows registry."""
    cursor_values = {key: str(target_directory / file_name) for key, file_name in VISION_CURSOR_REGISTRY_VALUES.items()}
    scheme_text = ','.join(str(target_directory / file_name) for file_name in VISION_CURSOR_REGISTRY_VALUES.values())

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Control Panel\Cursors') as cursor_key:
        winreg.SetValueEx(cursor_key, '', 0, winreg.REG_SZ, 'Vision Cursor Black')
        for value_name, file_path in cursor_values.items():
            winreg.SetValueEx(cursor_key, value_name, 0, winreg.REG_SZ, file_path)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Control Panel\Cursors\Schemes') as schemes_key:
        winreg.SetValueEx(schemes_key, 'Vision Cursor Black', 0, winreg.REG_SZ, scheme_text)

    try:
        ctypes.windll.user32.SystemParametersInfoW(0x0057, 0, None, 0x01 | 0x02)
    except Exception:
        pass


def _download_vision_cursor_files(destination_directory: Path):
    """Download Vision Cursor files from GitHub RAW."""
    destination_directory.mkdir(parents=True, exist_ok=True)
    
    base_cursor_path = "system/windows/install/vision-cursor-black"
    
    for file_name in set(VISION_CURSOR_FILES.values()):
        try:
            file_data = _fetch_github_file(f"{base_cursor_path}/{file_name}")
            dest_file = destination_directory / file_name
            dest_file.write_bytes(file_data)
        except Exception as error:
            raise FileNotFoundError(f'Failed to download cursor asset {file_name}: {error}')


def apply_vision_cursor_black():
    if sys.platform != 'win32':
        return 'Vision Cursor Black is supported only on Windows.'

    destination_directory = _vision_cursor_install_path()
    try:
        _download_vision_cursor_files(destination_directory)
        _apply_windows_cursor_scheme(destination_directory)
        log.log(f'Vision Cursor Black applied from {destination_directory}.', level='INFO')
        return f'Vision Cursor Black applied from {destination_directory}.'
    except Exception as error:
        log.log(f'Failed to apply Vision Cursor Black: {error}', level='ERROR')
        return f'Failed to apply Vision Cursor Black: {error}'


def _normalize_startup_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _load_whitelist_terms(whitelist_content: str):
    """Parse whitelist content and return set of normalized terms."""
    whitelist = set()
    for raw_line in whitelist_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        normalized = _normalize_startup_name(line)
        if not normalized:
            continue

        whitelist.add(normalized)
        whitelist.update(LEGACY_WHITELIST_TERMS.get(normalized, set()))

    return whitelist


def _is_whitelisted(entry_name: str, whitelist_terms) -> bool:
    return _normalize_startup_name(entry_name) in whitelist_terms


def disable_startup_programs():
    """Disable startup entries that are not present in the GitHub whitelist."""
    try:
        whitelist_content = _fetch_github_file('system/windows/install/white_list.txt').decode('utf-8')
        whitelist_terms = _load_whitelist_terms(whitelist_content)
    except Exception as error:
        return f"Startup disable aborted. Failed to load whitelist from GitHub: {error}"

    if not whitelist_terms:
        return "Startup disable aborted. Whitelist is empty."

    disabled_count = 0
    preserved_count = 0
    disabled_value = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for label, (root, path) in REG_PATHS.items():
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                entry_names = []
                index = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(run_key, index)
                        entry_names.append(name)
                        index += 1
                    except OSError:
                        break

                app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                app_path = APPROVED_PATHS[label]

                with winreg.CreateKey(app_root, app_path) as approved_key:
                    for name in entry_names:
                        if _is_whitelisted(name, whitelist_terms):
                            preserved_count += 1
                            log.log(f'Preserved startup entry [{label}]: {name}', level="INFO")
                            continue

                        winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, disabled_value)
                        log.log(f'Disabled startup entry [{label}]: {name}', level="INFO")
                        disabled_count += 1
        except Exception as error:
            log.log(f"Skipping {label}, key not found or inaccessible: {error}", level="INFO")

    return (
        f"Scan complete. {disabled_count} startup entries were disabled and "
        f"{preserved_count} whitelist entries were preserved."
    )


def save_startup_keys(output_path="programs.log"):
    """Save the current startup registry state for audit/debugging."""
    try:
        lines = []
        for label, (root, path) in REG_PATHS.items():
            try:
                with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for index in range(count):
                        name, value, _ = winreg.EnumValue(key, index)
                        lines.append(f"{label}::{name}::{value}")
            except Exception:
                lines.append(f"{label}::(inaccessible)")

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write("\n".join(lines))
        return f"Startup keys saved to {output_path}."
    except Exception as error:
        return f"Error saving keys: {error}"


def enable_startup_whitelist():
    """Re-enable whitelisted startup entries from GitHub."""
    try:
        whitelist_content = _fetch_github_file('system/windows/install/white_list.txt').decode('utf-8')
        whitelist_terms = _load_whitelist_terms(whitelist_content)
    except Exception as error:
        return f"Whitelist re-enable failed. Error: {error}"

    if not whitelist_terms:
        return "Whitelist is empty; nothing to re-enable."

    activated_count = 0
    enabled_value = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    for label, (root, path) in REG_PATHS.items():
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as run_key:
                app_root = winreg.HKEY_CURRENT_USER if "HKCU" in label else winreg.HKEY_LOCAL_MACHINE
                app_path = APPROVED_PATHS[label]

                with winreg.CreateKey(app_root, app_path) as approved_key:
                    index = 0
                    while True:
                        try:
                            name, _, _ = winreg.EnumValue(run_key, index)
                            if _is_whitelisted(name, whitelist_terms):
                                winreg.SetValueEx(approved_key, name, 0, winreg.REG_BINARY, enabled_value)
                                log.log(f'Re-enabled from whitelist: {name}', level="INFO")
                                activated_count += 1
                            index += 1
                        except OSError:
                            break
        except Exception:
            continue

    return f"Success: {activated_count} startup entries re-enabled from whitelist."