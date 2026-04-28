import json
import re
import threading
import urllib.error
import urllib.request

import customtkinter as ctk

try:
	from lib import json as json_data
	from lib import screen, system, uninstall
except ModuleNotFoundError:
	from lib import json as json_data
	from lib import screen, system, uninstall


REPO_OWNER = "JLBBARCO"
REPO_NAME = "auto-programs"
REPO_BRANCH = "main"
INSTALL_PREFIX = "install/"

RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}"
TREE_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{REPO_BRANCH}?recursive=1"


class More(ctk.CTkToplevel):
	def __init__(self, parent=None, title: str = "Install Files", run_callback=None, menu_items: list[tuple[str, str]] | None = None):
		super().__init__(parent)
		self.title(title)

		self.run_callback = run_callback
		self.menu_items = [
			(str(key).strip(), str(label).strip())
			for key, label in (menu_items or [])
			if str(key).strip() and str(label).strip()
		]

		self.repo_path_by_category_key: dict[str, str] = {}
		self.tab_label_by_category_key: dict[str, str] = {}
		self.program_selection_vars: dict[str, dict[str, dict[str, object]]] = {}
		self.checkbox_containers: dict[str, ctk.CTkScrollableFrame] = {}
		self.loaded_paths: set[str] = set()
		self.loading_paths: set[str] = set()
		self.file_sources: dict[str, str] = {}
		self.tool_windows: list[ctk.CTkToplevel] = []

		if parent is not None:
			self.transient(parent)
			self.grab_set()

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)

		self.header_label = ctk.CTkLabel(
			self,
			text="Browse install files",
			font=ctk.CTkFont(size=18, weight="bold"),
		)
		self.header_label.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

		self.content_frame = ctk.CTkFrame(self)
		self.content_frame.grid(row=1, column=0, padx=12, pady=(6, 12), sticky="nsew")
		self.content_frame.grid_columnconfigure(0, weight=1)
		self.content_frame.grid_rowconfigure(1, weight=1)

		self.content_title = ctk.CTkLabel(
			self.content_frame,
			text="Select a tab to view its programs",
			anchor="w",
			font=ctk.CTkFont(size=14, weight="bold"),
		)
		self.content_title.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")

		self.options_frame = ctk.CTkFrame(self.content_frame)
		self.options_frame.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="nsew")
		self.options_frame.grid_columnconfigure(0, weight=1)
		self.options_frame.grid_rowconfigure(0, weight=1)

		self.tabview = ctk.CTkTabview(self.options_frame, height=320)
		self.tabview.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

		self.status_label = ctk.CTkLabel(self.content_frame, text="Loading file list...", anchor="w")
		self.status_label.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="ew")

		self.button_frame = ctk.CTkFrame(self)
		self.button_frame.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
		self.button_frame.grid_columnconfigure(0, weight=0)
		self.button_frame.grid_columnconfigure(1, weight=0)
		self.button_frame.grid_columnconfigure(2, weight=1)

		self.add_program_button = ctk.CTkButton(self.button_frame, text="Add Program", command=self._open_add_program_screen)
		self.add_program_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

		self.remove_program_button = ctk.CTkButton(
			self.button_frame,
			text="Remove Program",
			command=self._open_remove_program_screen,
		)
		self.remove_program_button.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="w")

		self.run_button = ctk.CTkButton(self.button_frame, text="Run", command=self._submit)
		self.run_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

		self._reload_all_entries()

	def _reload_all_entries(self):
		self.loaded_paths.clear()
		self.loading_paths.clear()

		base_entries = self._build_base_entries()
		local_entries = self._build_local_entries()
		self._populate_file_menu(base_entries + local_entries)

	def _build_base_entries(self) -> list[tuple[str, str, str, str]]:
		file_entries: list[tuple[str, str, str, str]] = []
		for key, label in self.menu_items:
			if str(key).strip().lower() == 'drivers':
				continue
			repo_path = self._default_repo_path(key)
			if self._is_hidden_repo_path(repo_path):
				continue
			category_key = self._category_key_from_repo_path(repo_path)
			file_entries.append((repo_path, category_key, label, 'remote'))
		return file_entries

	def _build_local_entries(self) -> list[tuple[str, str, str, str]]:
		entries: list[tuple[str, str, str, str]] = []

		user_install_data = json_data.read_local_json_file('user_install')
		if isinstance(user_install_data, dict) and user_install_data.get('programs'):
			entries.append(('user_install.json', 'user_install', 'User Install', 'local'))

		user_uninstall_data = json_data.read_local_json_file('user_uninstall')
		if isinstance(user_uninstall_data, dict) and user_uninstall_data.get('programs'):
			entries.append(('user_uninstall.json', 'user_uninstall', 'User Uninstall', 'local'))

		return entries

	def _default_repo_path(self, category_key: str) -> str:
		system_name = system.nameSO().lower()
		if category_key.lower().endswith('.json') or '/' in category_key:
			return category_key
		return f"{INSTALL_PREFIX}{system_name}/{category_key}.json"

	def _is_hidden_repo_path(self, repo_path: str) -> bool:
		return repo_path.rsplit('/', 1)[-1].lower() == 'drivers.json'

	def _populate_file_menu(self, file_entries: list[tuple[str, str, str, str]]):
		self.repo_path_by_category_key.clear()
		self.tab_label_by_category_key.clear()
		self.checkbox_containers.clear()
		self.program_selection_vars.clear()
		self.file_sources.clear()

		for widget in self.tabview.winfo_children():
			widget.destroy()

		if not file_entries:
			self.status_label.configure(text='No install files selected.')
			self.run_button.configure(state='disabled')
			return

		self.run_button.configure(state='normal')

		for repo_path, category_key, display_name, source in file_entries:
			unique_display_name = self._unique_display_name(display_name)
			self.repo_path_by_category_key[category_key] = repo_path
			self.tab_label_by_category_key[category_key] = unique_display_name
			self.file_sources[category_key] = source

			tab = self.tabview.add(unique_display_name)
			container = ctk.CTkScrollableFrame(tab)
			container.pack(fill='both', expand=True, padx=10, pady=10)
			container.grid_columnconfigure(0, weight=1)
			self.checkbox_containers[category_key] = container
			self.program_selection_vars[category_key] = {}
			self._ensure_file_loaded(category_key, repo_path, source)

		first_category_key = file_entries[0][1]
		first_label = self.tab_label_by_category_key[first_category_key]
		self.content_title.configure(text=first_label)
		self.tabview.set(first_label)
		self.status_label.configure(text=f"Loaded {len(file_entries)} file(s). Use the tabs to switch lists.")

	def _unique_display_name(self, base_name: str) -> str:
		candidate = base_name
		counter = 2
		while candidate in self.tab_label_by_category_key.values():
			candidate = f"{base_name} ({counter})"
			counter += 1
		return candidate

	def _ensure_file_loaded(self, category_key: str, repo_path: str, source: str):
		if repo_path in self.loaded_paths or repo_path in self.loading_paths:
			return

		self.loading_paths.add(repo_path)
		loader = threading.Thread(
			target=self._load_file_content_worker,
			args=(category_key, repo_path, source),
			daemon=True,
		)
		loader.start()

	def _load_file_content_worker(self, category_key: str, repo_path: str, source: str):
		try:
			if source == 'local':
				payload = self._extract_local_payload(category_key)
			else:
				raw_url = f"{RAW_BASE_URL}/{repo_path}"
				request = urllib.request.Request(raw_url, headers={"User-Agent": "auto-programs"})
				with urllib.request.urlopen(request, timeout=20) as response:
					content = response.read().decode('utf-8', errors='ignore')
				payload = self._extract_program_payload(content)

			self.after(0, self._update_content, category_key, repo_path, payload)
		except urllib.error.HTTPError as error:
			self.after(0, self._show_error, f"HTTP error loading {repo_path}: {error.code}")
		except urllib.error.URLError as error:
			self.after(0, self._show_error, f"Network error loading {repo_path}: {error.reason}")
		except Exception as error:
			self.after(0, self._show_error, f"Failed to load {repo_path}: {error}")
		finally:
			self.loading_paths.discard(repo_path)

	def _extract_local_payload(self, category_key: str) -> list[dict[str, str]]:
		payload = json_data.read_local_json_file(category_key)
		programs = payload.get('programs', []) if isinstance(payload, dict) else []
		return self._normalize_program_entries(programs)

	def _extract_program_payload(self, content: str) -> list[dict[str, str]]:
		try:
			parsed = json.loads(content)
		except json.JSONDecodeError:
			return []

		if not isinstance(parsed, dict):
			return []

		programs = parsed.get('programs', [])
		return self._normalize_program_entries(programs)

	def _normalize_program_entries(self, programs) -> list[dict[str, str]]:
		if not isinstance(programs, list):
			return []

		entries: list[dict[str, str]] = []
		for program in programs:
			if not isinstance(program, dict):
				continue

			name = str(program.get('name', '')).strip()
			item_id = str(program.get('id', '')).strip()
			function_name = str(program.get('function', '')).strip()
			if not name:
				continue
			if not item_id and not function_name:
				continue

			entry = {'name': name, 'id': item_id, 'function': function_name}
			entries.append(entry)

		return sorted(entries, key=lambda entry: entry['name'].lower())

	def _update_content(self, category_key: str, repo_path: str, programs: list[dict[str, str]]):
		container = self.checkbox_containers.get(category_key)
		if container is None:
			self.loaded_paths.add(repo_path)
			return

		for widget in container.winfo_children():
			widget.destroy()

		if not programs:
			empty_label = ctk.CTkLabel(container, text='No program names found for this file.', anchor='w')
			empty_label.grid(row=0, column=0, padx=8, pady=8, sticky='w')
		else:
			for index, program in enumerate(programs):
				program_name = program.get('name', '').strip()
				program_id = program.get('id', '').strip()
				program_function = program.get('function', '').strip()
				checkbox_var = ctk.BooleanVar(value=True)

				self.program_selection_vars[category_key][f"{program_name}::{program_id}::{program_function}"] = {
					'var': checkbox_var,
					'id': program_id,
					'function': program_function,
					'name': program_name,
				}

				item_text = program_name
				if program_id:
					item_text = f"{program_name} ({program_id})"
				elif program_function:
					item_text = f"{program_name} ({program_function})"

				checkbox = ctk.CTkCheckBox(
					container,
					text=item_text,
					variable=checkbox_var,
					onvalue=True,
					offvalue=False,
				)
				checkbox.grid(row=index, column=0, padx=8, pady=4, sticky='w')

		self.loaded_paths.add(repo_path)

	def _category_key_from_repo_path(self, repo_path: str) -> str:
		if repo_path.startswith(INSTALL_PREFIX):
			filename = repo_path[len(INSTALL_PREFIX):]
		else:
			filename = repo_path.rsplit('/', 1)[-1]
		return filename.rsplit('.', 1)[0]

	def _parse_winget_rows(self, output: str) -> list[dict]:
		results = []
		seen_ids = set()

		for line in output.splitlines():
			raw = line.strip()
			if not raw:
				continue
			lowered = raw.lower()

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

			key = item_id.lower()
			if key in seen_ids:
				continue
			seen_ids.add(key)
			results.append({'name': name, 'id': item_id})

		return sorted(results, key=lambda item: item['name'].lower())

	def _search_remote_programs(self, query: str) -> list[dict]:
		if system.nameSO() != 'Windows':
			return []

		import subprocess

		process = subprocess.run(
			['winget', 'search', '--query', query, '--accept-source-agreements'],
			capture_output=True,
			text=True,
			encoding='utf-8',
			errors='ignore',
			shell=False,
		)
		combined = (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')
		return self._parse_winget_rows(combined)

	def _open_add_program_screen(self):
		options = [
			{
				'key': 'search_results',
				'label': 'Search Results',
				'selection_type': 'button',
				'items': [],
				'search_target': True,
			}
		]

		tool_window = screen.Screen(
			parent=self,
			title='Add Programs',
			options=options,
			search_handler=self._search_remote_programs,
			submit_handler=self._on_submit_user_install,
			submit_text='Submit',
		)
		self.tool_windows.append(tool_window)

	def _open_remove_program_screen(self):
		uninstallable_items = uninstall.list_uninstallable_programs()
		options = [
			{
				'key': 'installed_programs',
				'label': 'Installed Programs',
				'selection_type': 'button',
				'items': uninstallable_items,
			}
		]

		tool_window = screen.Screen(
			parent=self,
			title='Remove Programs',
			options=options,
			submit_handler=self._on_submit_user_uninstall,
			submit_text='Submit',
		)
		self.tool_windows.append(tool_window)

	def _on_submit_user_install(self, selected_by_section: dict[str, list[dict]]):
		selected = selected_by_section.get('search_results', [])
		if not selected:
			self.status_label.configure(text='No program selected for user_install.json.')
			return

		total = json_data.save_local_json_file('user_install', selected)
		self.status_label.configure(text=f'Saved {total} program(s) in user_install.json.')
		self._reload_all_entries()

	def _on_submit_user_uninstall(self, selected_by_section: dict[str, list[dict]]):
		selected = selected_by_section.get('installed_programs', [])
		if not selected:
			self.status_label.configure(text='No program selected for user_uninstall.json.')
			return

		total = json_data.save_local_json_file('user_uninstall', selected)
		self.status_label.configure(text=f'Saved {total} program(s) in user_uninstall.json.')
		self._reload_all_entries()

	def _submit(self):
		if callable(self.run_callback):
			self.run_callback(self._collect_selected_programs())
		self.destroy()

	def _collect_selected_programs(self) -> dict[str, list[dict]]:
		selected_programs: dict[str, list[dict]] = {}

		for category_key, programs in self.program_selection_vars.items():
			selected_entries: list[dict] = []
			for program_data in programs.values():
				if not isinstance(program_data, dict):
					continue

				checkbox_var = program_data.get('var')
				if checkbox_var is None or not checkbox_var.get():
					continue

				name = str(program_data.get('name', '')).strip()
				item_id = str(program_data.get('id', '')).strip()
				function_name = str(program_data.get('function', '')).strip()
				if not name:
					continue
				if not item_id and not function_name:
					continue

				entry = {'name': name}
				if item_id:
					entry['id'] = item_id
				if function_name:
					entry['function'] = function_name
				selected_entries.append(entry)

			selected_programs[category_key] = selected_entries

		return selected_programs

	def _show_error(self, message: str):
		self.status_label.configure(text=message)

