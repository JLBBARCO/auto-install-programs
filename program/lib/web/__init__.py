import json
import os
import secrets
import threading
import time
import webbrowser
from pathlib import Path

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from lib.find_folders import get_ProgramsManager_folder


_server_lock = threading.Lock()
_shared_log_server = None
_shared_log_server_thread = None
_shared_log_server_port_range = range(9900, 10000)
_log_file_path = get_ProgramsManager_folder() / 'log.log'
_programs_manager_site_url = os.getenv(
	'PROGRAMS_MANAGER_SITE_URL',
	'https://jlbbarco.github.io/programs-manager',
)
_programs_manager_site_fallback_url = os.getenv(
	'PROGRAMS_MANAGER_SITE_FALLBACK_URL',
	'https://passwords-manager-jlbbarco.vercel.app',
)
_internet_check_interval_seconds = 30
_internet_check_url = 'https://www.google.com/generate_204'
_internet_online_event = threading.Event()
_internet_monitor_stop_event = threading.Event()
_internet_monitor_thread = None


def _build_site_url(base_url: str, port: int) -> str:
	parsed_url = urlparse(base_url)
	query_items = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
	query_items['port'] = str(port)
	return urlunparse(parsed_url._replace(query=urlencode(query_items)))


def _iter_shared_log_server_ports(preferred_port: int | None = None):
	if preferred_port is not None:
		yield preferred_port
		return

	candidate_ports = list(_shared_log_server_port_range)
	secrets.SystemRandom().shuffle(candidate_ports)
	for candidate_port in candidate_ports:
		yield candidate_port


def _check_internet_connection(timeout_seconds: int = 5) -> bool:
	request = Request(_internet_check_url, headers={'User-Agent': 'ProgramsManager/1.0'})
	try:
		with urlopen(request, timeout=timeout_seconds) as response:
			return 200 <= getattr(response, 'status', 204) < 400
	except Exception:
		return False


def _internet_monitor_loop():
	while not _internet_monitor_stop_event.is_set():
		if _check_internet_connection():
			_internet_online_event.set()
		else:
			_internet_online_event.clear()

		if _internet_monitor_stop_event.wait(_internet_check_interval_seconds):
			break


def start_internet_monitor():
	global _internet_monitor_thread

	if _internet_monitor_thread is not None and _internet_monitor_thread.is_alive():
		return

	_internet_monitor_stop_event.clear()
	if _check_internet_connection():
		_internet_online_event.set()
	else:
		_internet_online_event.clear()

	_internet_monitor_thread = threading.Thread(
		target=_internet_monitor_loop,
		name='InternetMonitor',
		daemon=True,
	)
	_internet_monitor_thread.start()


def wait_for_internet_connection(poll_interval_seconds: float = 1.0):
	start_internet_monitor()
	while not _internet_online_event.is_set():
		print('Internet offline. Pausing execution until connection is restored...')
		if _internet_monitor_stop_event.wait(poll_interval_seconds):
			break


def stop_internet_monitor():
	global _internet_monitor_thread

	_internet_monitor_stop_event.set()
	if _internet_monitor_thread is not None and _internet_monitor_thread.is_alive():
		_internet_monitor_thread.join(timeout=1)
	_internet_monitor_thread = None


class _LogShareRequestHandler(BaseHTTPRequestHandler):
	def _send_cors_headers(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type')
		self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
		self.send_header('Pragma', 'no-cache')

	def _read_log_contents(self) -> str:
		try:
			_log_file_path.touch(exist_ok=True)
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
			body = json.dumps({'logFile': str(_log_file_path)}).encode('utf-8')
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


def start_shared_log_server(host='127.0.0.1', port=None):
	global _shared_log_server
	global _shared_log_server_thread

	with _server_lock:
		if _shared_log_server is not None:
			return _shared_log_server

		server = None
		last_error = None
		for candidate_port in _iter_shared_log_server_ports(port):
			if candidate_port not in _shared_log_server_port_range:
				raise ValueError(
					f'Unsupported shared log server port: {candidate_port}. '
					'Expected a port in the 99** range.'
				)

			try:
				server = ThreadingHTTPServer((host, candidate_port), _LogShareRequestHandler)
				break
			except OSError as error:
				last_error = error

		if server is None:
			raise RuntimeError(
				'No available port found in the 99** range for the shared log server.'
		) from last_error

		server.daemon_threads = True
		server_url = f'http://{server.server_address[0]}:{server.server_address[1]}'

		thread = threading.Thread(target=server.serve_forever, name='LogShareServer', daemon=True)
		thread.start()

		server.server_url = server_url  # type: ignore[attr-defined]
		_shared_log_server = server
		_shared_log_server_thread = thread
		print(f'Shared log server ready at {server_url}')
		return server


def stop_shared_log_server():
	global _shared_log_server
	global _shared_log_server_thread

	with _server_lock:
		if _shared_log_server is None:
			return

		server = _shared_log_server
		thread = _shared_log_server_thread
		_shared_log_server = None
		_shared_log_server_thread = None

	try:
		server.shutdown()
	finally:
		server.server_close()

	if thread is not None and thread.is_alive():
		thread.join(timeout=1)


def get_shared_log_server_url():
	if _shared_log_server is None:
		return ''
	return getattr(_shared_log_server, 'server_url', '')


def get_shared_log_server_port():
	if _shared_log_server is None:
		return 0
	return int(_shared_log_server.server_address[1])


def open_programs_manager_site(port=None):
	resolved_port = port if port is not None else get_shared_log_server_port()
	opened_url = ''

	for base_url in (_programs_manager_site_url, _programs_manager_site_fallback_url):
		opened_url = _build_site_url(base_url, resolved_port)
		try:
			if webbrowser.open(opened_url, new=2):
				return opened_url
		except Exception:
			continue

	return opened_url

