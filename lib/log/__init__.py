import datetime
import inspect
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# write log.log alongside the executable when frozen or in the project root
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    # prefer the repository root if available, otherwise CWD
    base_dir = os.getcwd()

_log_file_path = os.path.join(base_dir, 'log.log')
_log_file = open(_log_file_path, 'a+', encoding="utf-8")
_lock = threading.Lock()
_server_lock = threading.Lock()
_shared_log_server = None
_shared_log_server_thread = None


def _now():
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def get_log_file_path():
    return _log_file_path


class _LogShareRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')

    def _read_log_contents(self) -> str:
        with _lock:
            try:
                _log_file.flush()
            except Exception:
                pass

        try:
            with open(_log_file_path, 'r', encoding='utf-8') as log_file:
                return log_file.read()
        except Exception as error:
            return f'Unable to read log file: {error}'

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path in {'/', '/log', '/log.log', '/api/log'}:
            payload = self._read_log_contents()
            encoded_payload = payload.encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded_payload)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(encoded_payload)
            return

        if parsed_path.path == '/meta':
            body = json.dumps({'logFile': _log_file_path}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_shared_log_server(host='127.0.0.1', port=0):
    global _shared_log_server
    global _shared_log_server_thread

    with _server_lock:
        if _shared_log_server is not None:
            return _shared_log_server

        server = ThreadingHTTPServer((host, port), _LogShareRequestHandler)
        server.daemon_threads = True
        server_url = f'http://{server.server_address[0]}:{server.server_address[1]}'

        thread = threading.Thread(target=server.serve_forever, name='LogShareServer', daemon=True)
        thread.start()

        server.server_url = server_url  # type: ignore[attr-defined]
        _shared_log_server = server
        _shared_log_server_thread = thread
        return server


def get_shared_log_server_url():
    if _shared_log_server is None:
        return ''
    return getattr(_shared_log_server, 'server_url', '')


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