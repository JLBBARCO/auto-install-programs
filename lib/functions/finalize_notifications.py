import ctypes
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path

from lib import system


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

		return True
	except Exception:
		return False
