import subprocess
import re
try:
    from src.lib import system, installations, json
except ModuleNotFoundError:
    from lib import system, installations, json
import customtkinter as ctk

title = 'Add Programs'

class searchPrograms(ctk.CTkToplevel):
    def __init__(self, parent=None, on_submit=None):
        super().__init__(parent)
        self.title(title)
        self.geometry('900x560')
        self.on_submit = on_submit
        self.pending_programs = []

        # Make this window modal over the main app.
        if parent is not None:
            self.transient(parent)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.protocol('WM_DELETE_WINDOW', self.cancel)

        self.label = ctk.CTkLabel(self, text=title)
        self.label.grid(padx=10, pady=10, row=0, columnspan=10)

        self.searchInput = ctk.CTkEntry(self, placeholder_text='Digite o nome do programa para buscar no winget')
        self.searchInput.grid(padx=10, pady=10, row=1, column=0, columnspan=2, sticky='ew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.searchButton = ctk.CTkButton(self, text='Search', command=self.search)
        self.searchButton.grid(padx=10, pady=10, row=1, column=2)

        self.containerShow = ctk.CTkScrollableFrame(self, width=860, height=380)
        self.containerShow.grid(padx=10, pady=10, row=2, column=0, columnspan=3, sticky='nsew')
        self.grid_rowconfigure(2, weight=1)
        self.containerShow.grid_columnconfigure(0, weight=0)
        self.containerShow.grid_columnconfigure(1, weight=1)
        self.containerShow.grid_columnconfigure(2, weight=1)

        self.statusLabel = ctk.CTkLabel(self, text='')
        self.statusLabel.grid(padx=10, pady=(0, 10), row=3, column=0, columnspan=3, sticky='w')

        self.cancelButton = ctk.CTkButton(self, text='Cancel', command=self.cancel)
        self.cancelButton.grid(padx=10, pady=10, row=4, column=0, sticky='w')

        self.submitButton = ctk.CTkButton(self, text='Submit', command=self.submit)
        self.submitButton.grid(padx=10, pady=10, row=4, column=2, sticky='e')

        self._render_headers()

    def _render_headers(self):
        self._clear_results(keep_headers=False)
        ctk.CTkLabel(self.containerShow, text='Add', font=ctk.CTkFont(weight='bold')).grid(row=0, column=0, padx=8, pady=4, sticky='w')
        ctk.CTkLabel(self.containerShow, text='Name', font=ctk.CTkFont(weight='bold')).grid(row=0, column=1, padx=8, pady=4, sticky='w')
        ctk.CTkLabel(self.containerShow, text='Id', font=ctk.CTkFont(weight='bold')).grid(row=0, column=2, padx=8, pady=4, sticky='w')

    def _clear_results(self, keep_headers=True):
        for widget in self.containerShow.winfo_children():
            widget.destroy()
        if keep_headers:
            self._render_headers()

    def _parse_winget_search_output(self, output):
        results = []
        seen_ids = set()

        noise_patterns = (
            'agree',
            'agreements',
            'source',
            'msstore',
            'no package found',
            'no installed package found',
        )

        for line in output.splitlines():
            raw = line.strip()
            if not raw:
                continue

            lowered = raw.lower()

            # Ignore progress bars and transfer/status lines from winget.
            if re.search(r'\b\d{1,3}%\b', lowered):
                continue
            if any(char in raw for char in ('█', '▓', '▒', '▌', '▐', '■', '━', '─', '│')):
                continue
            if any(token in lowered for token in noise_patterns):
                continue

            # Ignore table headers and separators.
            if raw.lower().startswith('name') and 'id' in raw.lower():
                continue
            if set(raw) <= {'-', ' '}:
                continue
            if re.fullmatch(r'[-\s]{3,}', raw):
                continue

            # Winget prints columns separated by 2+ spaces.
            parts = re.split(r'\s{2,}', raw)
            if len(parts) < 2:
                continue

            name = parts[0].strip()
            program_id = parts[1].strip()

            if not name or not program_id:
                continue
            if ' ' in program_id:
                # IDs from winget should not contain spaces.
                continue
            if not re.search(r'[A-Za-z0-9]', program_id):
                continue

            key = program_id.lower()
            if key in seen_ids:
                continue
            seen_ids.add(key)
            results.append({'name': name, 'id': program_id})

        return results

    def _is_already_added(self, program):
        current_user = json.read_json('user') or {}
        current_programs = current_user.get('programs', []) if isinstance(current_user, dict) else []
        existing_ids = {
            str(item.get('id', '')).strip().lower()
            for item in current_programs
            if isinstance(item, dict)
        }
        pending_ids = {
            str(item.get('id', '')).strip().lower()
            for item in self.pending_programs
            if isinstance(item, dict)
        }
        pid = str(program.get('id', '')).strip().lower()
        return pid in existing_ids or pid in pending_ids

    def _add_program(self, program):
        if self._is_already_added(program):
            self.statusLabel.configure(text=f"'{program['name']}' ja esta na lista de User.")
            return

        self.pending_programs.append({'name': program['name'], 'id': program['id']})
        self.statusLabel.configure(text=f"Adicionado para salvar: {program['name']} ({program['id']})")
        self.search()

    def _render_search_results(self, programs):
        self._clear_results()
        if not programs:
            ctk.CTkLabel(self.containerShow, text='Nenhum resultado encontrado.').grid(row=1, column=1, padx=8, pady=8, sticky='w')
            return

        for index, program in enumerate(programs, start=1):
            already_added = self._is_already_added(program)
            add_button = ctk.CTkButton(
                self.containerShow,
                text='Add' if not already_added else 'Added',
                width=80,
                state='disabled' if already_added else 'normal',
                command=lambda p=program: self._add_program(p),
            )
            add_button.grid(row=index, column=0, padx=8, pady=4, sticky='w')

            ctk.CTkLabel(self.containerShow, text=program['name'], anchor='w', justify='left').grid(row=index, column=1, padx=8, pady=4, sticky='w')
            ctk.CTkLabel(self.containerShow, text=program['id'], anchor='w', justify='left').grid(row=index, column=2, padx=8, pady=4, sticky='w')

    def search(self):
        query = self.searchInput.get().strip()
        if not query:
            self.statusLabel.configure(text='Digite um nome para buscar.')
            self._clear_results()
            return

        system_name = system.nameSO()
        if system_name == "Windows":
            try:
                process = subprocess.run(
                    [
                        'winget',
                        'search',
                        '--query',
                        query,
                        '--accept-source-agreements',
                    ],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    shell=False,
                )
                combined = (process.stdout or '') + ("\n" + process.stderr if process.stderr else '')
                results = self._parse_winget_search_output(combined)
                self._render_search_results(results)
                self.statusLabel.configure(text=f'{len(results)} resultado(s) para "{query}".')
            except Exception as error:
                self._clear_results()
                self.statusLabel.configure(text=f'Erro ao buscar no winget: {error}')
        elif system_name == "Linux":
            installer = installations._resolve_linux_installer()
            if installer == 'apt':
                self.statusLabel.configure(text='Busca automatica ainda nao implementada para apt.')
            elif installer == 'dnf':
                self.statusLabel.configure(text='Busca automatica ainda nao implementada para dnf.')
            elif installer == 'pacman':
                self.statusLabel.configure(text='Busca automatica ainda nao implementada para pacman.')
        elif system_name == 'MacOS':
            self.statusLabel.configure(text='Busca automatica ainda nao implementada para MacOS.')

    def cancel(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def submit(self):
        if self.pending_programs:
            inserted = json.append_programs('user', self.pending_programs)
            self.statusLabel.configure(text=f'{inserted} programa(s) salvo(s) em user.json.')
        if callable(self.on_submit):
            self.on_submit()
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()