import sys, os, threading, datetime, inspect

# write log.log alongside the executable when frozen or in the project root
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    # prefer the repository root if available, otherwise CWD
    base_dir = os.getcwd()

_log_file_path = os.path.join(base_dir, 'log.log')
_log_file = open(_log_file_path, 'a+', encoding="utf-8")
_lock = threading.Lock()


def _now():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def log(message, level="INFO"):
    """Write a timestamped log entry with level, PID, thread name and caller.

    Usage: log('message', level='ERROR')

    Level variables:
    level='INFO';
    level='WARRING';
    level='ERROR';
    """
    try:
        caller = inspect.stack()[1].function
    except Exception:
        caller = "<unknown>"

    now = _now()
    pid = os.getpid()
    thread_name = threading.current_thread().name

    with _lock:
        _log_file.write(f'[{now}] [{level}] [pid:{pid}] [thread:{thread_name}] [caller:{caller}] {message}\n')
        _log_file.flush()


# initial separator for new run
with _lock:
    _log_file.write('\n')
    _log_file.flush()