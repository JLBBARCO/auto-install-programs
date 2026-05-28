import datetime
import threading

from lib.find_folders import get_ProgramsManager_folder


_log_file_path = get_ProgramsManager_folder() / 'log.log'
_log_file = open(_log_file_path, 'a+', encoding='utf-8')
_lock = threading.Lock()


def _now():
    return datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def get_log_file_path():
    return _log_file_path


def log(message, level="INFO"):
    now = _now()

    with _lock:
        _log_file.write(f'[{now}] [{level}] {message}\n')
        _log_file.flush()


# initial separator for new run
with _lock:
    _log_file.write('\n')
    _log_file.flush()