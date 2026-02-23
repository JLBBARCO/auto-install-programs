from datetime import datetime
import threading

_log_file = open('log.log', 'a+', encoding="utf-8")
_lock = threading.Lock()

def log(message):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with _lock:
        _log_file.write(f'[{now}] {message}\n')
        _log_file.flush()

# initial separator for new run
with _lock:
    _log_file.write('\n')
    _log_file.flush()