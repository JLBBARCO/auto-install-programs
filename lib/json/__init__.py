import sys
import os
import json
import urllib.request
from typing import List, Dict
try:
    from lib import log, system
except ModuleNotFoundError:
    from lib import log, system

GITHUB_REPOSITORY_BASE_URL = "https://raw.githubusercontent.com/jlbbarco/auto-install-programs/main"
GITHUB_INSTALL_BASE_URL = f"{GITHUB_REPOSITORY_BASE_URL}/install"

def _resource_path(relative_path: str) -> str:
    """Return the absolute path to *relative_path* next to the executable.

    Used exclusively for writable user data (e.g. user.json, programs.log).
    When running normally it resolves relative to the current working directory.
    When running as a frozen PyInstaller app it resolves next to the executable
    so that files written at runtime persist across runs (not in _MEIPASS, which
    is a temporary extraction folder that is deleted on every launch).
    """
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.getcwd()
    return os.path.join(base, relative_path)


def _normalize_json_payload(installer_data: Dict) -> Dict:
    name = installer_data.get('name', '')
    description = installer_data.get('description', '')
    programs = installer_data.get('programs', [])
    if not isinstance(programs, list):
        programs = []
    return {
        'name': name,
        'description': description,
        'programs': programs,
    }


def _default_payload(name: str) -> Dict:
    return {
        'name': name,
        'description': '',
        'programs': [],
    }


def _normalize_program_entry(program: Dict) -> Dict:
    return {
        'name': str(program.get('name', '')).strip(),
        'id': str(program.get('id', '')).strip(),
        'function': str(program.get('function', '')).strip(),
    }


def _entry_unique_key(program: Dict) -> str:
    normalized = _normalize_program_entry(program)
    if normalized['id']:
        return f"id::{normalized['id'].lower()}"
    if normalized['function']:
        return f"function::{normalized['function'].lower()}"
    return f"name::{normalized['name'].lower()}"


def read_local_json_file(file_name: str) -> Dict:
    file_stem = str(file_name).strip().replace('.json', '')
    target_path = _resource_path(f"{file_stem}.json")
    if not os.path.exists(target_path):
        return _default_payload(file_stem.replace('_', ' ').title())

    with open(target_path, 'r', encoding='utf-8') as target_file:
        raw = target_file.read().strip()
        payload = json.loads(raw) if raw else {}

    if not isinstance(payload, dict):
        return _default_payload(file_stem.replace('_', ' ').title())

    normalized_payload = _normalize_json_payload(payload)
    normalized_programs = []
    for program in normalized_payload.get('programs', []):
        if not isinstance(program, dict):
            continue
        normalized_program = _normalize_program_entry(program)
        if not normalized_program['name']:
            continue
        if not normalized_program['id'] and not normalized_program['function']:
            continue
        program_output = {'name': normalized_program['name']}
        if normalized_program['id']:
            program_output['id'] = normalized_program['id']
        if normalized_program['function']:
            program_output['function'] = normalized_program['function']
        normalized_programs.append(program_output)

    normalized_payload['programs'] = normalized_programs
    return normalized_payload


def save_local_json_file(file_name: str, programs: List[Dict], description: str = '') -> int:
    file_stem = str(file_name).strip().replace('.json', '')
    target_path = _resource_path(f"{file_stem}.json")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    current_payload = read_local_json_file(file_stem)
    existing_programs = current_payload.get('programs', []) if isinstance(current_payload, dict) else []
    if not isinstance(existing_programs, list):
        existing_programs = []

    merged_programs = []
    seen_keys = set()

    for source_program in [*existing_programs, *programs]:
        if not isinstance(source_program, dict):
            continue
        normalized_program = _normalize_program_entry(source_program)
        if not normalized_program['name']:
            continue
        if not normalized_program['id'] and not normalized_program['function']:
            continue

        unique_key = _entry_unique_key(normalized_program)
        if unique_key in seen_keys:
            continue
        seen_keys.add(unique_key)

        output_program = {'name': normalized_program['name']}
        if normalized_program['id']:
            output_program['id'] = normalized_program['id']
        if normalized_program['function']:
            output_program['function'] = normalized_program['function']
        merged_programs.append(output_program)

    payload = {
        'name': file_stem.replace('_', ' ').title(),
        'description': description,
        'programs': merged_programs,
    }

    with open(target_path, 'w', encoding='utf-8') as target_file:
        json.dump(payload, target_file, indent=2, ensure_ascii=False)

    return len(merged_programs)


def _build_repo_raw_url(relative_repo_path: str) -> str:
    normalized_path = str(relative_repo_path).replace('\\', '/').lstrip('/')
    return f"{GITHUB_REPOSITORY_BASE_URL}/{normalized_path}"


def fetch_repo_bytes(relative_repo_path: str, timeout: int = 30) -> bytes:
    url = _build_repo_raw_url(relative_repo_path)
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def fetch_repo_text(relative_repo_path: str, timeout: int = 12, encoding: str = 'utf-8') -> str:
    payload = fetch_repo_bytes(relative_repo_path, timeout=timeout)
    return payload.decode(encoding, errors='ignore')


def ensure_repo_file(relative_repo_path: str, local_relative_path: str = None, timeout: int = 30) -> str:
    target_relative_path = local_relative_path or relative_repo_path
    target_path = _resource_path(target_relative_path)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)

    payload = fetch_repo_bytes(relative_repo_path, timeout=timeout)
    with open(target_path, 'wb') as output_file:
        output_file.write(payload)

    return target_path


def _read_local_json(installer_path: str):
    if not os.path.exists(installer_path):
        return None
    with open(installer_path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
        installer_data = json.loads(raw) if raw else {}
    return _normalize_json_payload(installer_data)


def _fetch_remote_json(system_name: str, file_name: str):
    payload = fetch_repo_text(f"install/{system_name.lower()}/{file_name}.json", timeout=12)
    installer_data = json.loads(payload) if payload.strip() else {}
    return _normalize_json_payload(installer_data)


def _merge_programs(primary_programs: List[Dict], secondary_programs: List[Dict]) -> List[Dict]:
    merged = []
    seen_ids = set()

    for source in (primary_programs, secondary_programs):
        if not isinstance(source, list):
            continue
        for program in source:
            if not isinstance(program, dict):
                continue
            normalized = _normalize_program(program)
            if not normalized['name'] or not normalized['id']:
                continue
            pid_key = normalized['id'].lower()
            if pid_key in seen_ids:
                continue
            seen_ids.add(pid_key)
            merged.append(normalized)

    return merged

def read_json(file_name):
    """Return the program list for *file_name* category.

    * 'user' — read from the local file only (managed by append_programs).
    * all other categories — fetch exclusively from GitHub; no local fallback
      so that the installer does not need to bundle the install/ directory.
    """
    system_name = system.nameSO()

    # User-managed categories are local-only.
    if file_name in ('user', 'user_install', 'user_uninstall'):
        local_file = 'user_install' if file_name == 'user' else file_name
        try:
            return read_local_json_file(local_file)
        except Exception as error:
            log.log(f"Failed to read local {local_file}.json. Error: {error}", "WARNING")
            return _default_payload(local_file.replace('_', ' ').title())

    # All other categories are fetched exclusively from GitHub to keep the
    # installer small (install/ directory is not bundled).
    try:
        remote_data = _fetch_remote_json(system_name, file_name)
        log.log(f"Loaded JSON from repository for category '{file_name}'.", "INFO")
        return remote_data
    except Exception as error:
        log.log(f"Failed to load JSON from repository for '{file_name}'. Error: {error}", "ERROR")
        return None


def _normalize_program(program: Dict) -> Dict:
    normalized = _normalize_program_entry(program)
    return {
        'name': normalized['name'],
        'id': normalized['id'],
        'function': normalized['function'],
    }


def append_programs(file_name: str, programs_to_add: List[Dict]) -> int:
    if file_name in ('user', 'user_install', 'user_uninstall'):
        local_file = 'user_install' if file_name == 'user' else file_name
        try:
            return save_local_json_file(local_file, programs_to_add)
        except Exception as error:
            log.log(f'Failed to append programs to {local_file}.json. Error: {error}', level='ERROR')
            return 0

    system_name = system.nameSO().lower()
    target_path = _resource_path(os.path.join('install', system_name, f'{file_name}.json'))

    try:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        current_data = {'name': file_name.capitalize(), 'description': '', 'programs': []}
        if os.path.exists(target_path):
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    loaded = json.loads(content)
                    if isinstance(loaded, dict):
                        current_data = loaded

        existing_programs = current_data.get('programs', [])
        if not isinstance(existing_programs, list):
            existing_programs = []

        existing_keys = {
            _entry_unique_key(program)
            for program in existing_programs
            if isinstance(program, dict)
        }

        inserted = 0
        for program in programs_to_add:
            if not isinstance(program, dict):
                continue
            normalized = _normalize_program(program)
            if not normalized['name']:
                continue
            if not normalized['id'] and not normalized['function']:
                continue

            entry_key = _entry_unique_key(normalized)
            if entry_key in existing_keys:
                continue

            output_program = {'name': normalized['name']}
            if normalized['id']:
                output_program['id'] = normalized['id']
            if normalized['function']:
                output_program['function'] = normalized['function']

            existing_programs.append(output_program)
            existing_keys.add(entry_key)
            inserted += 1

        current_data['programs'] = existing_programs

        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(current_data, f, indent=2, ensure_ascii=False)

        log.log(f'Added {inserted} program(s) to {target_path}', level='INFO')
        return inserted
    except Exception as error:
        log.log(f'Failed to append programs to JSON. Error: {error}', level='ERROR')
        return 0


def write_json(path, data=None):
    payload = data if isinstance(data, dict) else {
        'name': os.path.basename(path),
        'description': '',
        'programs': [],
    }
    with open(f'{path}.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)