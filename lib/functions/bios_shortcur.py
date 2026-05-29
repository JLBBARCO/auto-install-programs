import os
import subprocess

from lib import system


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

