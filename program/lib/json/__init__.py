import json

from pathlib import Path

from lib import log, system


def get_user_documents_folder():
    if system.nameSO() == "Windows":
        import winreg
        chave_registro = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, chave_registro) as key:
                caminho_docs, _ = winreg.QueryValueEx(key, "Personal")
                return Path(winreg.ExpandEnvironmentStrings(caminho_docs))

        except Exception:
            return Path.home() / "Documents"

    return Path.home() / "Documents"


def get_ProgramsManager_folder():
    base_path = get_user_documents_folder() / "Programs Manager"
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().strip()
        dictionary = json.loads(data) if data else {}
        return dictionary


def read_internal_json(file):
    folder = get_ProgramsManager_folder()
    file_path = folder / f'{file}.json'
    if not file_path.exists():
        log.log(f'File {file}.json not found, creating default file.', level='WARNING')
        write_json()
    return read_json(file_path)


def read_external_json(file):
    url_path = f'https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/program/system/{system.nameSO().lower()}/json/{file}.json'
    try:
        import requests
        response = requests.get(url_path, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as fallback_error:
        log.log(f"Failed to fetch external JSON: {fallback_error}", level="ERROR")
    return None


def write_json(data=None):
    default_description = "User data generated after execution of write system"
    if isinstance(data, dict) and 'data' in data:
        payload = {
            "name": str(data.get('name', 'User')).strip() or 'User',
            "description": str(data.get('description', default_description)).strip() or default_description,
            "data": data.get('data', []),
        }
    else:
        payload = {
            "name": "User",
            "description": default_description,
            "data": [] if data is None else data,
        }


    folder = get_ProgramsManager_folder()
    with open(f'{folder}/user.json', 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

