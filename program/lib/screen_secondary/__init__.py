import json
import re
import shutil
import subprocess
import threading
from typing import cast

import customtkinter as ctk

from lib import json as json_data
from lib import log, system, screen_other


GRID_PADDING_X = 20
GRID_PADDING_Y = 5
PROGRAM_TAB_ROW = 10
DEFAULT_USER_DESCRIPTION = "User data generated after execution of write system"


class ScreenSecondary(ctk.CTk):
    def __init__(self, operational_system: str, theme: str, title: str, files_array):
        super().__init__()
        ctk.set_appearance_mode(theme)
        self.title(title)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.operational_system = operational_system
        self.files_array = self._normalize_file_list(files_array)
        self.json_data: list[dict[str, object]] = []
        self.file_payloads_by_key: dict[str, dict[str, object]] = {}
        self.file_key_by_tab_label: dict[str, str] = {}
        self.tab_label_by_file_key: dict[str, str] = {}
        self.entry_vars_by_file_key: dict[str, list[tuple[dict[str, object], ctk.BooleanVar]]] = {}
        self.tool_windows: list[ctk.CTkToplevel] = []
        self.selected_result: dict[str, list[dict[str, object]]] = {}
        self.current_file_key = ""
        self.loading = True
        self._tabview_ready = False

        self.main_title = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        self.main_title.grid(pady=GRID_PADDING_Y, row=0, column=0, sticky="ew")

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=GRID_PADDING_X, pady=GRID_PADDING_Y)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=GRID_PADDING_X, pady=(0, GRID_PADDING_Y), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=0)
        self.button_frame.grid_columnconfigure(1, weight=0)
        self.button_frame.grid_columnconfigure(2, weight=0)
        self.button_frame.grid_columnconfigure(3, weight=1)

        self.button_toggle_all = ctk.CTkButton(self.button_frame, text="Select all", command=self.toggle_all_options, state="disabled")
        self.button_toggle_all.grid(row=0, column=0, padx=(10, 8), pady=10, sticky="w")

        self.button_install_programs = ctk.CTkButton(self.button_frame, text="Install Programs", command=self.install_programs)
        self.button_install_programs.grid(row=0, column=1, padx=8, pady=10, sticky="w")

        self.button_uninstall_programs = ctk.CTkButton(self.button_frame, text="Uninstall Programs", command=self.uninstall_programs)
        self.button_uninstall_programs.grid(row=0, column=2, padx=8, pady=10, sticky="w")

        self.button_run = ctk.CTkButton(self.button_frame, text="RUN", command=self.run)
        self.button_run.grid(row=0, column=3, padx=(8, 10), pady=10, sticky="e")

        self.status_label = ctk.CTkLabel(self, text="Loading JSON files...", anchor="w")
        self.status_label.grid(row=3, column=0, padx=GRID_PADDING_X, pady=(0, GRID_PADDING_Y), sticky="ew")

        self._show_loading_skeleton("Loading JSON files...")
        self.after(50, self._start_loading_worker)

    def _normalize_file_list(self, files_array) -> list[str]:
        normalized_files: list[str] = []
        for file_name in files_array or []:
            normalized = self._normalize_file_name(file_name)
            if normalized and normalized not in normalized_files:
                normalized_files.append(normalized)

        if 'user' not in normalized_files:
            normalized_files.append('user')

        return normalized_files

    def _normalize_file_name(self, file_name) -> str:
        normalized = str(file_name or '').strip()
        if not normalized:
            return ''

        normalized = normalized.replace('\\', '/').rsplit('/', 1)[-1]
        if normalized.lower().endswith('.json'):
            normalized = normalized[:-5]
        return normalized.strip()

    def _show_loading_skeleton(self, message: str):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.loading_frame = ctk.CTkFrame(self.content_frame)
        self.loading_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self.loading_frame.grid_columnconfigure(0, weight=1)

        self.loading_label = ctk.CTkLabel(self.loading_frame, text=message, anchor="w", font=ctk.CTkFont(size=14, weight="bold"))
        self.loading_label.grid(row=0, column=0, padx=14, pady=(14, 10), sticky="ew")

        for index in range(4):
            bar = ctk.CTkFrame(self.loading_frame, height=16)
            bar.grid(row=index + 1, column=0, padx=14, pady=8, sticky="ew")
            bar.grid_propagate(False)

        self.loading_hint = ctk.CTkLabel(self.loading_frame, text="Preparing file tabs and content...", anchor="w")
        self.loading_hint.grid(row=5, column=0, padx=14, pady=(10, 14), sticky="ew")

    def _start_loading_worker(self):
        loader = threading.Thread(target=self._load_files_worker, name="ProgramsManagerJsonLoader", daemon=True)
        loader.start()

    def _load_files_worker(self):
        loaded_records: list[dict[str, object]] = []

        try:
            for file_name in self.files_array:
                payload = self.read_json(file_name)
                if not payload:
                    continue

                file_key = self._normalize_file_name(file_name)
                display_name = str(payload.get('name', '')).strip() or self._display_name_from_file_key(file_key)
                loaded_records.append(
                    {
                        'file_key': file_key,
                        'tab_label': display_name,
                        'payload': payload,
                    }
                )

            loaded_records.sort(key=lambda record: str(record['tab_label']).lower())
            unique_records = self._deduplicate_tab_labels(loaded_records)
            self.after(0, self._build_tabs, unique_records)
        except Exception as error:
            self.after(0, self._show_error, f'Failed to load JSON files: {error}')

    def _deduplicate_tab_labels(self, loaded_records: list[dict[str, object]]) -> list[dict[str, object]]:
        seen_labels: set[str] = set()
        for record in loaded_records:
            base_label = str(record.get('tab_label', '')).strip() or 'File'
            label = base_label
            suffix = 2
            while label in seen_labels:
                label = f'{base_label} ({suffix})'
                suffix += 1
            seen_labels.add(label)
            record['tab_label'] = label
        return loaded_records

    def _display_name_from_file_key(self, file_key: str) -> str:
        if not file_key:
            return 'File'
        return file_key.replace('_', ' ').strip().title()

    def _normalize_payload(self, payload: dict, fallback_name: str) -> dict[str, object]:
        payload_name = str(payload.get('name', '')).strip() or self._display_name_from_file_key(fallback_name)
        description = str(payload.get('description', payload.get('description', ''))).strip()
        raw_entries = payload.get('data', [])
        normalized_entries: list[dict[str, object]] = []

        if isinstance(raw_entries, list):
            for entry in raw_entries:
                normalized_entry = self._normalize_entry(entry)
                if normalized_entry is not None:
                    normalized_entries.append(normalized_entry)

        return {
            'name': payload_name,
            'description': description,
            'data': normalized_entries,
        }

    def _normalize_entry(self, entry) -> dict[str, object] | None:
        if not isinstance(entry, dict):
            return None

        name = str(entry.get('name', '')).strip()
        entry_type = str(entry.get('type', '')).strip()
        item_id = str(entry.get('id', '')).strip()
        if not name or not entry_type:
            return None

        return {
            'name': name,
            'type': entry_type,
            'id': item_id,
            'checkbox': bool(entry.get('checkbox', False)),
        }

    def read_json(self, file_name: str):
        normalized_name = self._normalize_file_name(file_name)
        if not normalized_name:
            return None

        if normalized_name == 'user':
            payload = json_data.read_internal_json('user')
        else:
            payload = json_data.read_external_json(normalized_name)

        if not isinstance(payload, dict):
            log.log(f'Failed to read {normalized_name}.json', level='ERROR')
            return None

        normalized_payload = self._normalize_payload(payload, normalized_name)
        log.log(f'Read {normalized_name}.json successfully', level='INFO')
        return normalized_payload

    def _build_tabs(self, loaded_records: list[dict[str, object]]):
        self.loading = False
        self.json_data = []
        for record in loaded_records:
            payload = record.get('payload')
            if isinstance(payload, dict):
                self.json_data.append(payload)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if not loaded_records:
            self._show_error('No JSON files could be loaded.')
            self.button_toggle_all.configure(state='disabled', text='Select all')
            return

        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.content_title = ctk.CTkLabel(self.content_frame, text='Select a tab to view its programs', anchor='w', font=ctk.CTkFont(size=14, weight='bold'))
        self.content_title.grid(row=0, column=0, padx=12, pady=(12, 6), sticky='ew')

        self.tabview = ctk.CTkTabview(self.content_frame, height=320, command=self._on_tab_changed)
        self.tabview.grid(row=1, column=0, padx=12, pady=(0, 12), sticky='nsew')
        self._tabview_ready = True

        self.file_payloads_by_key.clear()
        self.file_key_by_tab_label.clear()
        self.tab_label_by_file_key.clear()
        self.entry_vars_by_file_key.clear()

        for record in loaded_records:
            file_key = str(record.get('file_key', '')).strip()
            tab_label = str(record.get('tab_label', '')).strip()
            payload = record.get('payload')
            if not file_key or not tab_label or not isinstance(payload, dict):
                continue

            self.file_payloads_by_key[file_key] = payload
            self.file_key_by_tab_label[tab_label] = file_key
            self.tab_label_by_file_key[file_key] = tab_label
            self.entry_vars_by_file_key[file_key] = []

            self.tabview.add(tab_label)
            tab_page = self.tabview.tab(tab_label)
            tab_page.grid_columnconfigure(0, weight=1)
            tab_page.grid_rowconfigure(1, weight=1)

            file_heading = ctk.CTkLabel(tab_page, text=str(payload.get('name', tab_label)), anchor='w', font=ctk.CTkFont(size=13, weight='bold'))
            file_heading.grid(row=0, column=0, padx=10, pady=(10, 6), sticky='ew')

            scroll_frame = ctk.CTkScrollableFrame(tab_page)
            scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='nsew')
            scroll_frame.grid_columnconfigure(1, weight=1)
            scroll_frame.grid_columnconfigure(2, weight=0)

            self._render_entries(file_key, payload, scroll_frame)

        first_record = loaded_records[0]
        first_tab_label = str(first_record.get('tab_label', '')).strip()
        self.current_file_key = str(first_record.get('file_key', '')).strip()
        if first_tab_label:
            self.tabview.set(first_tab_label)
            self.content_title.configure(text=first_tab_label)

        self.button_toggle_all.configure(state='normal')
        self._update_toggle_button_text()
        self.status_label.configure(text=f'Loaded {len(loaded_records)} file(s). Use the tabs to switch lists.')

    def _render_entries(self, file_key: str, payload: dict[str, object], container):
        raw_entries = payload.get('data', []) if isinstance(payload, dict) else []
        entries = raw_entries if isinstance(raw_entries, list) else []
        sorted_entries = sorted(
            [cast(dict[str, object], entry) for entry in entries if isinstance(entry, dict)],
            key=lambda entry: (
                str(entry.get('name', '')).strip().lower(),
                str(entry.get('type', '')).strip().lower(),
                str(entry.get('id', '')).strip().lower(),
            ),
        )

        header_frame = ctk.CTkFrame(container)
        header_frame.grid(row=0, column=0, padx=6, pady=(6, 8), sticky='ew')
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)

        checkbox_header = ctk.CTkLabel(header_frame, text='', width=20)
        checkbox_header.grid(row=0, column=0, padx=(10, 6), pady=8, sticky='w')

        name_header = ctk.CTkLabel(header_frame, text='Name', anchor='w', font=ctk.CTkFont(size=12, weight='bold'))
        name_header.grid(row=0, column=1, padx=6, pady=8, sticky='ew')

        type_header = ctk.CTkLabel(header_frame, text='Type', anchor='w', font=ctk.CTkFont(size=12, weight='bold'))
        type_header.grid(row=0, column=2, padx=(6, 12), pady=8, sticky='w')

        if not sorted_entries:
            empty_label = ctk.CTkLabel(container, text='No entries found for this file.', anchor='w')
            empty_label.grid(row=1, column=0, padx=12, pady=12, sticky='w')
            return

        row_index = 1
        for entry in sorted_entries:
            name = str(entry.get('name', '')).strip()
            entry_type = str(entry.get('type', '')).strip()
            if not name or not entry_type:
                continue

            entry_var = ctk.BooleanVar(value=bool(entry.get('checkbox', False)))
            entry['_var'] = entry_var
            self.entry_vars_by_file_key[file_key].append((entry, entry_var))

            row_frame = ctk.CTkFrame(container)
            row_frame.grid(row=row_index, column=0, padx=6, pady=4, sticky='ew')
            row_frame.grid_columnconfigure(0, weight=0)
            row_frame.grid_columnconfigure(1, weight=1)
            row_frame.grid_columnconfigure(2, weight=0)

            checkbox = ctk.CTkCheckBox(
                row_frame,
                text='',
                variable=entry_var,
                onvalue=True,
                offvalue=False,
                command=lambda item=entry, variable=entry_var: self._sync_entry_checkbox(item, variable),
            )
            checkbox.grid(row=0, column=0, padx=(10, 6), pady=8, sticky='w')

            name_label = ctk.CTkLabel(row_frame, text=name, anchor='w')
            name_label.grid(row=0, column=1, padx=6, pady=8, sticky='ew')

            type_label = ctk.CTkLabel(row_frame, text=entry_type.capitalize(), anchor='w')
            type_label.grid(row=0, column=2, padx=(6, 12), pady=8, sticky='w')

            row_index += 1

    def _sync_entry_checkbox(self, entry: dict[str, object], variable: ctk.BooleanVar):
        entry['checkbox'] = bool(variable.get())
        if self._current_tab_label() == self.tab_label_by_file_key.get(self.current_file_key, ''):
            self._update_toggle_button_text()

    def _current_tab_label(self) -> str:
        if not self._tabview_ready:
            return ''
        try:
            return str(self.tabview.get())
        except Exception:
            return self.tab_label_by_file_key.get(self.current_file_key, '')

    def _current_file_key_from_tab(self) -> str:
        tab_label = self._current_tab_label()
        if not tab_label:
            return self.current_file_key
        return self.file_key_by_tab_label.get(tab_label, self.current_file_key)

    def _on_tab_changed(self, *_args):
        self.current_file_key = self._current_file_key_from_tab()
        self._update_toggle_button_text()

    def _update_toggle_button_text(self):
        file_key = self._current_file_key_from_tab()
        entries = self.entry_vars_by_file_key.get(file_key, [])
        if not entries:
            self.button_toggle_all.configure(text='Select all', state='disabled')
            return

        should_unselect = all(bool(variable.get()) for _, variable in entries)
        self.button_toggle_all.configure(
            text='Unselect all' if should_unselect else 'Select all',
            state='normal',
        )

    def toggle_all_options(self):
        file_key = self._current_file_key_from_tab()
        entries = self.entry_vars_by_file_key.get(file_key, [])
        if not entries:
            return

        should_select = not all(bool(variable.get()) for _, variable in entries)
        for entry, variable in entries:
            variable.set(should_select)
            entry['checkbox'] = should_select

        self._update_toggle_button_text()

    def _collect_selected_by_type(self) -> dict[str, list[dict[str, object]]]:
        grouped_entries: dict[str, list[dict[str, object]]] = {'install': [], 'uninstall': [], 'function': []}

        for payload in self.file_payloads_by_key.values():
            entries = payload.get('data', []) if isinstance(payload, dict) else []
            if not isinstance(entries, list):
                continue

            for entry in entries:
                if not isinstance(entry, dict):
                    continue

                if not bool(entry.get('checkbox', False)):
                    continue

                entry_type = str(entry.get('type', '')).strip().lower()
                if entry_type not in grouped_entries:
                    continue

                grouped_entries[entry_type].append(self._public_entry(entry))

        return {key: value for key, value in grouped_entries.items() if value}

    def _public_entry(self, entry: dict[str, object]) -> dict[str, object]:
        public_entry = {
            'name': str(entry.get('name', '')).strip(),
            'type': str(entry.get('type', '')).strip(),
            'id': str(entry.get('id', '')).strip(),
            'checkbox': bool(entry.get('checkbox', False)),
        }
        return public_entry

    def run(self):
        self.selected_result = self._collect_selected_by_type()
        self._close_all_windows()

    def _close_all_windows(self):
        for tool_window in list(self.tool_windows):
            try:
                if tool_window.winfo_exists():
                    tool_window.destroy()
            except Exception:
                continue

        self.tool_windows.clear()

        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass

    def install_programs(self):
        dialog = ctk.CTkInputDialog(title='Add Program', text='Type a program name to search with winget:')
        query = str(dialog.get_input() or '').strip()
        if not query:
            self.status_label.configure(text='No search query provided.')
            return

        results = self._search_remote_programs(query)
        if not results:
            self.status_label.configure(text=f'No search results found for {system.nameSO()}.')
            return

        self._open_selection_dialog('Add Programs', results, 'install')

    def uninstall_programs(self):
        results = self._list_installed_programs()
        if not results:
            self.status_label.configure(text=f'No installed programs found for {system.nameSO()}.')
            return

        self._open_selection_dialog('Remove Programs', results, 'uninstall')

    def _open_selection_dialog(self, title: str, items: list[dict[str, str]], entry_type: str):
        if not items:
            return

        dialog = screen_other._ProgramSelectionDialog(
            self,
            title=title,
            items=items,
            on_submit=lambda selected_items: self._save_user_entries(selected_items, entry_type),
            default_selected=False,
        )
        self.tool_windows.append(dialog)

    def _save_user_entries(self, selected_items: list[dict[str, str]], entry_type: str):
        if not selected_items:
            self.status_label.configure(text=f'No program selected for {entry_type}.')
            return

        user_payload = self.file_payloads_by_key.get('user')
        if not isinstance(user_payload, dict):
            user_payload = {
                'name': 'User',
                'description': DEFAULT_USER_DESCRIPTION,
                'data': [],
            }

        existing_entries: list[dict[str, object]] = []
        raw_entries = user_payload.get('data', []) if isinstance(user_payload, dict) else []
        if isinstance(raw_entries, list):
            for entry in raw_entries:
                normalized_entry = self._normalize_entry(entry)
                if normalized_entry is not None:
                    existing_entries.append(normalized_entry)

        entry_lookup: dict[tuple[str, str, str], dict[str, object]] = {}
        for entry in existing_entries:
            key = (
                str(entry.get('name', '')).strip().lower(),
                str(entry.get('type', '')).strip().lower(),
                str(entry.get('id', '')).strip().lower(),
            )
            entry_lookup[key] = entry

        for item in selected_items:
            normalized_name, normalized_id = self._normalize_selected_program(item)
            if not normalized_name or not normalized_id:
                continue

            new_entry = {
                'name': normalized_name,
                'type': entry_type,
                'id': normalized_id,
                'checkbox': True,
            }
            key = (normalized_name.lower(), entry_type.lower(), normalized_id.lower())
            entry_lookup[key] = new_entry

        merged_entries = sorted(entry_lookup.values(), key=lambda entry: str(entry.get('name', '')).lower())
        user_payload['name'] = 'User'
        user_payload['description'] = DEFAULT_USER_DESCRIPTION
        user_payload['data'] = merged_entries

        json_data.write_json(user_payload)
        self.status_label.configure(text=f'Saved {len(merged_entries)} program(s) in user.json.')
        self._reload_all_entries()

    def _normalize_selected_program(self, item: dict[str, str]) -> tuple[str, str]:
        normalized_name = str(item.get('name', '')).strip()
        normalized_id = str(item.get('id', '')).strip()

        if self._is_winget_source(normalized_id):
            extracted_name, extracted_id = self._extract_winget_name_and_id(normalized_name)
            if extracted_name and extracted_id:
                normalized_name = extracted_name
                normalized_id = extracted_id
            else:
                normalized_id = ''

        if normalized_name.endswith(')') and '(' in normalized_name:
            base_name, extracted_id = normalized_name.rsplit('(', 1)
            extracted_name = base_name.strip()
            extracted_id = extracted_id[:-1].strip()
            if extracted_name and extracted_id and not normalized_id:
                normalized_name = extracted_name
                normalized_id = extracted_id

        return normalized_name, normalized_id

    def _is_winget_source(self, value: str) -> bool:
        return value.strip().lower() in {'winget', 'msstore'}

    def _looks_like_winget_version(self, value: str) -> bool:
        token = value.strip().lower()
        if not token:
            return False
        if token in {'unknown', 'installed', 'available', 'latest'}:
            return True
        return bool(re.fullmatch(r'[0-9]+(?:\.[0-9a-z]+)*', token))

    def _looks_like_winget_id(self, value: str) -> bool:
        token = value.strip()
        if not token or self._is_winget_source(token):
            return False
        if self._looks_like_winget_version(token):
            return False
        return bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', token))

    def _extract_winget_name_and_id(self, label: str) -> tuple[str, str]:
        tokens = [token for token in label.split() if token.strip()]
        if len(tokens) < 2:
            return label.strip(), ''

        for index, token in enumerate(tokens):
            if not self._looks_like_winget_id(token):
                continue

            next_token = tokens[index + 1] if index + 1 < len(tokens) else ''
            if index + 1 >= len(tokens) or self._looks_like_winget_version(next_token) or self._is_winget_source(next_token):
                extracted_name = ' '.join(tokens[:index]).strip()
                if extracted_name:
                    return extracted_name, token.strip()

        if len(tokens) >= 2 and self._looks_like_winget_version(tokens[-1]):
            candidate_id = tokens[-2].strip()
            extracted_name = ' '.join(tokens[:-2]).strip()
            if extracted_name and self._looks_like_winget_id(candidate_id):
                return extracted_name, candidate_id

        return label.strip(), ''

    def _search_remote_programs(self, query: str) -> list[dict[str, str]]:
        system_name = system.nameSO()

        if system_name == 'Windows':
            return self._run_and_parse_packages(['winget', 'search', '--query', query, '--accept-source-agreements'])

        if system_name == 'MacOS' and shutil.which('brew'):
            return self._parse_simple_package_output(self._run_command(['brew', 'search', query]))

        if system_name == 'Linux':
            if shutil.which('apt-cache'):
                return self._parse_apt_search_output(self._run_command(['apt-cache', 'search', query]))
            if shutil.which('pacman'):
                return self._parse_pacman_search_output(self._run_command(['pacman', '-Ss', query]))
            if shutil.which('dnf'):
                return self._parse_dnf_search_output(self._run_command(['dnf', 'search', query]))

        return []

    def _list_installed_programs(self) -> list[dict[str, str]]:
        system_name = system.nameSO()

        if system_name == 'Windows':
            return self._run_and_parse_packages(['winget', 'list', '--accept-source-agreements'])

        if system_name == 'MacOS' and shutil.which('brew'):
            installed_items = self._parse_simple_package_output(self._run_command(['brew', 'list', '--formula']))
            installed_items.extend(self._parse_simple_package_output(self._run_command(['brew', 'list', '--cask'])))
            return self._deduplicate_packages(installed_items)

        if system_name == 'Linux':
            if shutil.which('dpkg-query'):
                return self._parse_dpkg_list_output(self._run_command(['dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n']))
            if shutil.which('pacman'):
                return self._parse_simple_package_output(self._run_command(['pacman', '-Qq']))
            if shutil.which('rpm'):
                return self._parse_rpm_list_output(self._run_command(['rpm', '-qa', '--qf', '%{NAME}\t%{VERSION}\n']))
            if shutil.which('dnf'):
                return self._parse_dnf_list_output(self._run_command(['dnf', 'list', 'installed']))

        return []

    def _run_and_parse_packages(self, args: list[str]) -> list[dict[str, str]]:
        output = self._run_command(args)
        return self._parse_winget_rows(output)

    def _run_command(self, args: list[str]) -> str:
        process = subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=False,
        )
        return (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')

    def _parse_simple_package_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw:
                continue
            lowered = raw.lower()
            if lowered.startswith('warning:') or lowered.startswith('error:'):
                continue
            if lowered.startswith('==>') or set(raw) <= {'-', '='}:
                continue

            name = raw.split()[0].strip()
            if not name:
                continue

            key = name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': name, 'id': name})

        return sorted(results, key=lambda item: item['name'].lower())

    def _parse_apt_search_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw or ' - ' not in raw:
                continue

            name = raw.split(' - ', 1)[0].strip()
            if not name:
                continue

            key = name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': name, 'id': name})

        return sorted(results, key=lambda item: item['name'].lower())

    def _parse_pacman_search_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw or raw.startswith(' '):
                continue
            if raw.startswith('::') or set(raw) <= {'-', '='}:
                continue
            if '/' not in raw:
                continue

            package_token = raw.split()[0].strip()
            if '/' in package_token:
                name = package_token.split('/', 1)[1].strip()
            else:
                name = package_token

            if not name:
                continue

            key = name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': name, 'id': name})

        return sorted(results, key=lambda item: item['name'].lower())

    def _parse_dnf_search_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw:
                continue
            lowered = raw.lower()
            if lowered.startswith('last metadata') or lowered.startswith('no matches'):
                continue
            if set(raw) <= {'-', '='}:
                continue

            token = raw.split(':', 1)[0].split()[0].strip()
            if not token:
                continue

            key = token.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': token, 'id': token})

        return sorted(results, key=lambda item: item['name'].lower())

    def _parse_dpkg_list_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw:
                continue

            package_name = raw.split('\t', 1)[0].strip()
            if not package_name or package_name.lower() == 'package':
                continue

            key = package_name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': package_name, 'id': package_name})

        return sorted(results, key=lambda item: item['name'].lower())

    def _parse_rpm_list_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw:
                continue

            package_name = raw.split('\t', 1)[0].strip()
            if not package_name:
                continue

            key = package_name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': package_name, 'id': package_name})

        return sorted(results, key=lambda item: item['name'].lower())

    def _parse_dnf_list_output(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw or raw.startswith('Installed Packages') or raw.startswith('Available Packages'):
                continue
            if set(raw) <= {'-', '='}:
                continue

            token = raw.split()[0].strip()
            if '.' in token:
                token = token.split('.', 1)[0]

            if not token:
                continue

            key = token.lower()
            if key in seen_names:
                continue
            seen_names.add(key)
            results.append({'name': token, 'id': token})

        return sorted(results, key=lambda item: item['name'].lower())

    def _deduplicate_packages(self, packages: list[dict[str, str]]) -> list[dict[str, str]]:
        unique_packages: dict[str, dict[str, str]] = {}
        for package in packages:
            if not isinstance(package, dict):
                continue
            name = str(package.get('name', '')).strip()
            if not name:
                continue
            unique_packages[name.lower()] = {'name': name, 'id': str(package.get('id', name)).strip() or name}

        return sorted(unique_packages.values(), key=lambda item: item['name'].lower())
        installed_items: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for source in ('winget', 'msstore'):
            process = subprocess.run(
                ['winget', 'list', '--source', source, '--accept-source-agreements'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                shell=False,
            )
            combined = (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')
            for item in self._parse_winget_rows(combined):
                item_id = str(item.get('id', '')).strip().lower()
                if not item_id or item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                installed_items.append(item)

        return sorted(installed_items, key=lambda item: str(item.get('name', '')).lower())

    def _parse_winget_rows(self, output: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for line in output.splitlines():
            raw = line.strip()
            if not raw:
                continue

            lowered = raw.lower()
            if lowered.startswith('name') or lowered.startswith('nome'):
                if 'id' in lowered or 'fonte' in lowered or 'source' in lowered:
                    continue
            if lowered in {'name', 'nome', 'id', 'fonte', 'source'}:
                continue
            if set(raw) <= {'-', ' '}:
                continue
            if re.search(r'\b\d{1,3}%\b', raw):
                continue

            parts = re.split(r'\s{2,}', raw)
            if len(parts) < 2:
                extracted_name, item_id = self._extract_winget_name_and_id(raw)
                name = extracted_name
            else:
                name = str(parts[0]).strip()
                item_id = str(parts[1]).strip()

            if not name or not item_id:
                extracted_name, extracted_id = self._extract_winget_name_and_id(raw)
                name = name or extracted_name
                item_id = item_id or extracted_id

            if not name or not item_id:
                continue
            if name.lower() in {'name', 'nome'}:
                continue
            if self._is_winget_source(item_id) or item_id.lower() in {'id', 'id.'}:
                extracted_name, extracted_id = self._extract_winget_name_and_id(raw)
                if extracted_name and extracted_id:
                    name = extracted_name
                    item_id = extracted_id
                else:
                    continue

            key = item_id.lower()
            if key in seen_ids:
                continue

            seen_ids.add(key)
            results.append({'name': name, 'id': item_id})

        return sorted(results, key=lambda item: item['name'].lower())

    def _reload_all_entries(self):
        self.loading = True
        self._tabview_ready = False
        self.button_toggle_all.configure(state='disabled', text='Select all')
        self._show_loading_skeleton('Reloading JSON files...')
        self.after(50, self._start_loading_worker)

    def _show_error(self, message: str):
        self.status_label.configure(text=message)

    def ScreenSecondaryReturn(self):
        if self.selected_result:
            return self.selected_result
        return self._collect_selected_by_type()

