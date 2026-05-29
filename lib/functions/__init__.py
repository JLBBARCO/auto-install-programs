import subprocess, os, re
import sys
import ctypes
from ctypes import wintypes
from pathlib import Path

from lib import system, log


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

    return filtered_output


def dark_mode():
    if system.nameSO() == 'Windows':
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

def bios_shortcut() -> str:
    if system.nameSO() != 'Windows':
        return 'BIOS shortcut is currently supported only on Windows.'

    from lib.find_folders import get_StartMenu_Programs_folder
    bios_shortcut_ink = get_StartMenu_Programs_folder() / 'BIOS Shortcut.lnk'

    if bios_shortcut_ink.exists():
        return 'BIOS shortcut already exists in Start Menu.'

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
        shortcut_path = os.path.join(start_menu_programs, 'BIOS Shortcut.lnk')

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

        return 'BIOS shortcut created in Start Menu.'
    except Exception as error:
        return f'Failed to create BIOS shortcut: {error}'


def _restart_windows_explorer() -> None:
    if system.nameSO() != 'Windows':
        return

    try:
        subprocess.run(
            ["taskkill", "/f", "/im", "explorer.exe"],
            capture_output=True,
            text=True,
            shell=False,
        )
    except Exception:
        pass

    try:
        subprocess.Popen(
            ["explorer.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
        log.log('Windows Explorer restarted to apply system changes.', 'INFO')
    except Exception as error:
        log.log(f'Failed to restart Windows Explorer: {error}', 'ERROR')


def _resolve_notification_icon_path() -> Path | None:
    candidate_paths = []

    try:
        source_root = Path(__file__).resolve().parents[3]
        candidate_paths.extend([
            source_root / 'src' / 'assets' / 'icon' / 'icon.ico',
            source_root / 'program' / 'src' / 'assets' / 'icon' / 'icon.ico',
        ])
    except Exception:
        pass

    executable_path = Path(sys.executable).resolve()
    candidate_paths.extend([
        executable_path.with_name('icon.ico'),
        executable_path.parent / 'icon.ico',
        Path.cwd() / 'icon.ico',
        Path.cwd() / 'src' / 'assets' / 'icon' / 'icon.ico',
    ])

    bundled_root_value = getattr(sys, '_MEIPASS', None)
    if bundled_root_value:
        bundled_root = Path(bundled_root_value)
        candidate_paths.extend([
            bundled_root / 'icon.ico',
            bundled_root / 'src' / 'assets' / 'icon' / 'icon.ico',
        ])

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    return None


def _show_windows_notification(title: str, message: str) -> bool:
    user32 = ctypes.windll.user32
    shell32 = ctypes.windll.shell32
    kernel32 = ctypes.windll.kernel32

    WM_USER = 0x0400
    NIM_ADD = 0x00000000
    NIM_MODIFY = 0x00000001
    NIF_MESSAGE = 0x00000001
    NIF_ICON = 0x00000002
    NIF_TIP = 0x00000004
    NIF_INFO = 0x00000010
    NIIF_INFO = 0x00000001
    IMAGE_ICON = 1
    LR_LOADFROMFILE = 0x00000010
    LR_DEFAULTSIZE = 0x00000040

    class NOTIFYICONDATAW(ctypes.Structure):
        _fields_ = [
            ('cbSize', wintypes.DWORD),
            ('hWnd', wintypes.HWND),
            ('uID', wintypes.UINT),
            ('uFlags', wintypes.UINT),
            ('uCallbackMessage', wintypes.UINT),
            ('hIcon', wintypes.HICON),
            ('szTip', wintypes.WCHAR * 128),
            ('dwState', wintypes.DWORD),
            ('dwStateMask', wintypes.DWORD),
            ('szInfo', wintypes.WCHAR * 256),
            ('uTimeoutOrVersion', wintypes.UINT),
            ('szInfoTitle', wintypes.WCHAR * 64),
            ('dwInfoFlags', wintypes.DWORD),
            ('guidItem', ctypes.c_byte * 16),
            ('hBalloonIcon', wintypes.HICON),
        ]

    h_instance = kernel32.GetModuleHandleW(None)
    hwnd = user32.CreateWindowExW(0, 'STATIC', title, 0, 0, 0, 0, 0, 0, 0, h_instance, None)
    if not hwnd:
        return False

    icon_handle = None
    icon_path = _resolve_notification_icon_path()
    if icon_path is not None:
        icon_handle = user32.LoadImageW(
            None,
            str(icon_path),
            IMAGE_ICON,
            0,
            0,
            LR_LOADFROMFILE | LR_DEFAULTSIZE,
        )

    nid = NOTIFYICONDATAW()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
    nid.hWnd = hwnd
    nid.uID = 1
    nid.uFlags = NIF_MESSAGE | NIF_ICON | NIF_TIP
    nid.uCallbackMessage = WM_USER + 1
    nid.hIcon = icon_handle or 0
    nid.szTip = title

    if not shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid)):
        return False

    nid.uFlags = NIF_INFO
    nid.szInfo = message
    nid.szInfoTitle = title
    nid.dwInfoFlags = NIIF_INFO
    nid.uTimeoutOrVersion = 10000

    result = bool(shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid)))
    return result


def functions(functions_list):
    try:
        for item in functions_list:
            func = item['id']
            func = globals().get(func)
            if callable(func):
                func()
            log.log(f"Executed function: {item['name']}", 'INFO')
        _restart_windows_explorer()
    except Exception as error:
        log.log(f"Error executing functions: {error}", 'ERROR')


def finalize_notification():
    title = 'Programs Manager'
    message = 'Todas as instalações, desinstalações, atualizações e funções foram finalizadas.'

    try:
        current_system = system.nameSO()

        if current_system == 'Windows':
            if not _show_windows_notification(title, message):
                raise RuntimeError('could not create Windows notification')

        elif current_system == 'MacOS':
            process = subprocess.run(
                ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
                capture_output=True,
                text=True,
                shell=False,
            )
            if process.returncode != 0:
                raise RuntimeError((process.stderr or process.stdout or '').strip() or 'unknown error')

        elif current_system == 'Linux':
            process = subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                text=True,
                shell=False,
            )
            if process.returncode != 0:
                raise RuntimeError((process.stderr or process.stdout or '').strip() or 'unknown error')

        log.log('Final system notification sent successfully.', 'INFO')
    except Exception as error:
        log.log(f'Failed to send final system notification: {error}', 'ERROR')

