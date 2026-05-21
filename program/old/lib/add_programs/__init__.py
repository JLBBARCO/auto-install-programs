try:
    from program.lib import system
    from program.old.lib.package_manager import search_packages
except ModuleNotFoundError:
    from program.lib import system
    from program.old.lib.package_manager import search_packages
import customtkinter as ctk

from program.lib import json

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

        self.searchInput = ctk.CTkEntry(self, placeholder_text='Enter a program name to search in winget')
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

    def _is_already_added(self, program):
        current_user = json.read_json('user_install') or {}
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
            self.statusLabel.configure(text=f"'{program['name']}' is already in the user install list.")
            return

        self.pending_programs.append({'name': program['name'], 'id': program['id']})
        self.statusLabel.configure(text=f"Queued for save: {program['name']} ({program['id']})")
        self.search()

    def _render_search_results(self, programs):
        self._clear_results()
        if not programs:
            ctk.CTkLabel(self.containerShow, text='No results found.').grid(row=1, column=1, padx=8, pady=8, sticky='w')
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
            self.statusLabel.configure(text='Type a name to search.')
            self._clear_results()
            return

        system_name = system.nameSO()
        if system_name == "Windows":
            try:
                results = search_packages(query)
                self._render_search_results(results)
                self.statusLabel.configure(text=f'{len(results)} result(s) for "{query}".')
            except Exception as error:
                self._clear_results()
                self.statusLabel.configure(text=f'Error searching winget: {error}')
        else:
            self._clear_results()
            self.statusLabel.configure(text=f'Search is not available on {system_name}.')

    def cancel(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

    def submit(self):
        if self.pending_programs:
            inserted = json.append_programs('user', self.pending_programs)
            self.statusLabel.configure(text=f'{inserted} program(s) saved to user_install.json.')
        if callable(self.on_submit):
            self.on_submit()
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()