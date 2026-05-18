import json, os, sys
from lib import log


def read_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().strip()
        dictionary = json.loads(data) if data else {}
        return dictionary


def _user_data_dir() -> str:
    return os.path.join(os.path.expanduser("~"), "Downloads", "Programs Manager")


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


def _user_data_file_path(file_stem: str) -> str:
    """Return the storage path for user-managed JSON files.

    Always use the Downloads/Programs Manager folder so user-managed data is
    stable across source and packaged executions.
    """
    normalized = str(file_stem).strip().replace('.json', '')
    if normalized not in ('user_install', 'user_uninstall'):
        return _resource_path(f"{normalized}.json")

    return os.path.join(_user_data_dir(), f"{normalized}.json")


def _entry_unique_key(program) -> str:
    normalized = _normalize_program_entry(program)
    if normalized['id']:
        return f"id::{normalized['id'].lower()}"
    if normalized['function']:
        return f"function::{normalized['function'].lower()}"
    return f"name::{normalized['name'].lower()}"


def _normalize_json_payload(installer_data):
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


def _default_payload(name: str):
    return {
        'name': name,
        'description': '',
        'programs': [],
    }


def read_local_json_file(file_name: str):
    file_stem = str(file_name).strip().replace('.json', '')
    target_path = _user_data_file_path(file_stem)
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


def _normalize_program_entry(program):
    return {
        'name': str(program.get('name', '')).strip(),
        'id': str(program.get('id', '')).strip(),
        'function': str(program.get('function', '')).strip(),
    }


def save_local_json_file(file_name: str, programs, description: str = '') -> int:
    file_stem = str(file_name).strip().replace('.json', '')
    target_path = _user_data_file_path(file_stem)
    # Defer creating directories until we actually need to write a file.

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

    # If there are no valid programs to save, avoid creating an empty file.
    if not merged_programs:
        # If an existing file is present but now empty, remove it to avoid
        # leaving a useless placeholder on the user's Downloads folder.
        try:
            if os.path.exists(target_path):
                os.remove(target_path)
        except Exception:
            pass
        return 0

    payload = {
        'name': file_stem.replace('_', ' ').title(),
        'description': description,
        'programs': merged_programs,
    }

    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as target_file:
        json.dump(payload, target_file, indent=2, ensure_ascii=False)

    return len(merged_programs)


def write_json(path, data=None):
    payload = data if isinstance(data, dict) else {
        'name': os.path.basename(path),
        'description': '',
        'programs': [],
    }
    with open(f'{path}.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)