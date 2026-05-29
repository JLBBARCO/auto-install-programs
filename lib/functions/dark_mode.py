import subprocess

from lib import system


def _run_command(command: str) -> str:
	process = subprocess.run(command, capture_output=True, text=True, shell=True)
	raw_output = (process.stdout or "") + ("\n" + process.stderr if process.stderr else "")
	return raw_output.strip()


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

