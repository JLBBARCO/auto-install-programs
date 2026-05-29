import ctypes
import os
import re
import sys
import urllib.request
import winreg
from pathlib import Path

from lib import log, system


GITHUB_REPO_RAW_URL = "https://raw.githubusercontent.com/JLBBARCO/programs-manager/main"
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


def _fetch_github_file(relative_path: str, timeout: int = 30) -> bytes:
	url = f"{GITHUB_REPO_RAW_URL}/{relative_path}"
	with urllib.request.urlopen(url, timeout=timeout) as response:
		return response.read()


def _download_vision_cursor_files(destination_directory: Path):
	destination_directory.mkdir(parents=True, exist_ok=True)

	base_cursor_path = "system/windows/install/vision-cursor-black"

	for file_name in set(VISION_CURSOR_FILES.values()):
		try:
			file_data = _fetch_github_file(f"{base_cursor_path}/{file_name}")
			dest_file = destination_directory / file_name
			dest_file.write_bytes(file_data)
		except Exception as error:
			raise FileNotFoundError(f'Failed to download cursor asset {file_name}: {error}')


def _apply_windows_cursor_scheme(target_directory: Path):
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


def _normalize_startup_name(value: str) -> str:
	return re.sub(r"[^a-z0-9]+", "", value.casefold())


def vision_cursor_black():
	if system.nameSO() != 'Windows':
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

