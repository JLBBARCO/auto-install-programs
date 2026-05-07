import re
import subprocess
import shutil

try:
	from lib import json, log, system
	from lib.package_manager import list_installed_packages
except ModuleNotFoundError:
	from lib import json, log, system
	from lib.package_manager import list_installed_packages


WINDOWS_ADMIN_REQUIRED_IDS = {
	"adobe.acrobat.reader.64-bit",
}


def list_uninstallable_programs() -> list[dict]:
	os_name = system.nameSO()
	if os_name != 'Windows':
		return []

	try:
		return list_installed_packages()
	except Exception as error:
		log.log(f'Failed to list uninstallable programs: {error}', level='ERROR')
		return []


def _uninstall_program_id(program_id: str) -> str:
	if not program_id:
		return 'Skipped empty uninstall id'

	os_name = system.nameSO()
	if os_name == 'Windows':
		winget_args = [
			'uninstall',
			'--id',
			program_id,
			'-e',
			'--accept-source-agreements',
		]

		if program_id.lower() in WINDOWS_ADMIN_REQUIRED_IDS:
			return _run_winget_with_admin(winget_args)

		process = subprocess.run(
			['winget', *winget_args],
			capture_output=True,
			text=True,
			encoding='utf-8',
			errors='ignore',
			shell=False,
		)
		output = (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')

		if process.returncode != 0 and _looks_like_admin_error(output):
			log.log(f'Admin privileges required to uninstall {program_id}; retrying with elevation.', level='WARNING')
			return _run_winget_with_admin(winget_args)

		return output.strip()

	if os_name == 'Linux':
		installer = _resolve_linux_installer()
		if installer == 'apt':
			return _run_command(f'sudo apt-get remove -y "{program_id}"')
		if installer == 'dnf':
			return _run_command(f'sudo dnf remove -y "{program_id}"')
		if installer == 'pacman':
			return _run_command(f'sudo pacman -R --noconfirm "{program_id}"')
		return f'No supported Linux package manager detected for uninstall ({program_id}).'
	if os_name == 'MacOS':
		output = _run_command(f'brew uninstall --cask "{program_id}"')
		lowered = output.lower()
		if 'no cask' in lowered or 'error:' in lowered:
			return _run_command(f'brew uninstall "{program_id}"')
		return output
	return f'Unsupported OS: {os_name}'


def _resolve_linux_installer() -> str:
	if shutil.which('apt'):
		return 'apt'
	if shutil.which('dnf'):
		return 'dnf'
	if shutil.which('pacman'):
		return 'pacman'
	return ''


def _run_command(command: str) -> str:
	process = subprocess.run(command, capture_output=True, text=True, shell=True)
	output = (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')
	return output.strip()


def _looks_like_admin_error(output: str) -> bool:
	lowered = str(output or '').lower()
	return any(
		token in lowered
		for token in (
			'administrator',
			'admin',
			'access is denied',
			'0x8a15000f',
			'0x80070005',
		)
	)


def _run_winget_with_admin(winget_args: list[str]) -> str:
	escaped_args = ' '.join(
		[f'\"{arg}\"' if ' ' in arg or '"' in arg else arg for arg in winget_args]
	)
	ps_script = (
		"$process = Start-Process -FilePath 'winget' "
		f"-ArgumentList '{escaped_args}' "
		"-Verb RunAs -PassThru -Wait; "
		"Write-Output ('ExitCode=' + $process.ExitCode)"
	)

	process = subprocess.run(
		['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
		capture_output=True,
		text=True,
		encoding='utf-8',
		errors='ignore',
		shell=False,
	)
	output = (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')
	return output.strip() or 'Elevated winget uninstall completed.'


def uninstall_programs(selected_program_entries=None):
	data = json.read_json('user_uninstall')
	programs = data.get('programs', []) if isinstance(data, dict) else []

	selected_ids = None
	if selected_program_entries is not None:
		selected_ids = {
			str(entry.get('id', '')).strip()
			for entry in selected_program_entries
			if isinstance(entry, dict)
		}

	outputs = []
	removed_count = 0

	for program_entry in programs:
		if not isinstance(program_entry, dict):
			continue

		name = str(program_entry.get('name', '')).strip()
		program_id = str(program_entry.get('id', '')).strip()
		if not program_id:
			continue

		if selected_ids is not None and program_id not in selected_ids:
			continue

		log.log(f'Uninstalling {name} ({program_id})', level='INFO')
		output = _uninstall_program_id(program_id)
		outputs.append(f'{name}: {output}')
		removed_count += 1

	if removed_count == 0:
		message = 'No selected programs to uninstall.'
		log.log(message, level='INFO')
		return message

	summary = f'Uninstalled {removed_count} program(s).'
	log.log(summary, level='INFO')
	return '\n'.join([summary] + outputs)


def user(selected_program_entries=None):
	return uninstall_programs(selected_program_entries)
