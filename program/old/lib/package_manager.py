import re
import subprocess

from program.lib import log

try:
	from program.lib import system
except ModuleNotFoundError:
	from program.lib import system


WINDOWS_NOISE_PATTERNS = (
	'agree',
	'agreements',
	'source',
	'no package found',
	'no installed package found',
	'upgrades available',
)


def _parse_winget_rows(output: str) -> list[dict]:
	items = []
	seen_ids = set()

	for line in output.splitlines():
		raw = line.strip()
		if not raw:
			continue

		lowered = raw.lower()
		if any(char in raw for char in ('█', '▓', '▒', '▌', '▐', '■', '━', '─', '│')):
			continue
		if any(token in lowered for token in WINDOWS_NOISE_PATTERNS):
			continue
		if lowered.startswith('name') and 'id' in lowered:
			continue
		if set(raw) <= {'-', ' '}:
			continue
		if re.search(r'\b\d{1,3}%\b', raw):
			continue

		parts = re.split(r'\s{2,}', raw)
		if len(parts) < 2:
			continue

		name = str(parts[0]).strip()
		item_id = str(parts[1]).strip()
		if not name or not item_id:
			continue
		if ' ' in item_id:
			continue
		if not re.search(r'[A-Za-z0-9]', item_id):
			continue

		key = item_id.lower()
		if key in seen_ids:
			continue
		seen_ids.add(key)
		items.append({'name': name, 'id': item_id})

	return sorted(items, key=lambda item: item['name'].lower())


def _run_winget_command(arguments: list[str]) -> str:
	process = subprocess.run(
		['winget', *arguments],
		capture_output=True,
		text=True,
		encoding='utf-8',
		errors='ignore',
		shell=False,
	)
	return (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')


def search_packages(query: str) -> list[dict]:
	if system.nameSO() != 'Windows':
		return []

	output = _run_winget_command(['search', '--query', query, '--accept-source-agreements'])
	return _parse_winget_rows(output)


def list_installed_packages() -> list[dict]:
	if system.nameSO() != 'Windows':
		return []

	merged = []
	seen_ids = set()

	for source in ('winget', 'msstore'):
		output = _run_winget_command(['list', '--source', source, '--accept-source-agreements'])
		for item in _parse_winget_rows(output):
			item_id = str(item.get('id', '')).strip().lower()
			if not item_id or item_id in seen_ids:
				continue
			seen_ids.add(item_id)
			merged.append(item)

	return sorted(merged, key=lambda item: str(item.get('name', '')).lower())