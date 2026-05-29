import os
from pathlib import Path

from lib import system


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


def get_StartMenu_Programs_folder():
    if system.nameSO() == "Windows":
        start_menu_programs = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs'
        start_menu_programs.mkdir(parents=True, exist_ok=True)
        return start_menu_programs
    else:
        raise NotImplementedError("Start Menu Programs folder is only supported on Windows.")