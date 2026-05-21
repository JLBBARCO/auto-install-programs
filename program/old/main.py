import importlib
import os
import subprocess
import sys
import time
import webbrowser
from urllib.parse import urlencode

from program.old.lib import add_programs, install as install_module, more, screen, uninstall as uninstall_module

try:
    from old.lib import json, log, system
    from program.old.lib.install import single_instance
except ModuleNotFoundError:
    # Compatibility mode for executions where "src" is already the working root.
    from old.lib import json, log, system
    from program.old.lib.install import single_instance

try:
    import customtkinter as ctk
except ImportError:
    # try installing missing requirements and re-importing
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    try:
        ctk = importlib.import_module("customtkinter")
    except Exception:
        sys.exit("customtkinter is required. Install dependencies and run again.")

if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))

APP_TITLE_TEMPLATE = "{system_name} Programs Manager"

INSTALLATION_DELAY_SECONDS = 3


class App(ctk.CTk):  # type: ignore
    def __init__(self):
        super().__init__()

        self.system_name = system.nameSO()
        self.program_selection_vars = {}
        
        self.add_programs_window = None
        self.more_window = None
        self.program_tabview = None
        self.user_programs_container = None
        self._log_share_server = None
        self._support_site_opened = False

        ctk.set_appearance_mode("system")

        self._configure_window()
        self._build_header()
        self._build_options_frame()
        self._build_action_buttons()

    def _configure_window(self):
        self.title(APP_TITLE_TEMPLATE.format(system_name=self.system_name))
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _build_header(self):
        title = ctk.CTkLabel(
            self,
            text=f"Welcome to the {self.system_name} Programs Manager",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title.grid(pady=10, padx=10, columnspan=2, row=0)

        subtitle = ctk.CTkLabel(self, text="Select the programs you want to install:")
        subtitle.grid(pady=10, padx=10, columnspan=2, row=1)

    def _build_action_buttons(self):
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(pady=20, padx=10, row=5, column=0, sticky="e")

        self.toggleAllOptions = ctk.CTkButton(
            settings_frame,
            text="Toggle all options",
            command=self.toggle_all_options,
        )
        self.toggleAllOptions.grid(padx=5, pady=20, row=0, column=0)

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(pady=20, padx=10, row=5, column=1, sticky="e")

        run_button = ctk.CTkButton(button_frame, text="Next", command=self.run)
        run_button.grid(padx=5, pady=20, column=0, row=0)

    

    def _build_program_tab(self, config: CategoryConfig):
        if self.program_tabview is None:
            return

        tab = self.program_tabview.add(config.label.replace(" Programs", ""))
        container = ctk.CTkScrollableFrame(tab)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        if config.key == "user":
            self.user_programs_container = container
            self._render_user_program_controls()

        self.select_any_program(config.key, container)

    def _render_user_program_controls(self):
        if self.user_programs_container is None or not self.user_programs_container.winfo_exists():
            return

        add_button = ctk.CTkButton(
            self.user_programs_container,
            text="Add programs",
            command=self.add_programs,
        )
        add_button.pack(anchor="w", padx=10, pady=(0, 10))

    def _load_programs(self, category: str) -> list[dict]:
        payload = json.read_json(category)
        if not payload:
            return []

        programs = payload.get("programs", [])
        if not programs:
            return []

        return [program for program in programs if isinstance(program, dict)]

    def _build_program_checkboxes(self, category: str, container):
        self.program_selection_vars[category] = {}
        programs = sorted(
            self._load_programs(category),
            key=lambda program: str(program.get("name", "")).lower(),
        )

        for program in programs:
            program_name = str(program.get("name", "")).strip()
            program_id = str(program.get("id", "")).strip()
            program_function = str(program.get("function", "")).strip()
            if not program_name:
                continue
            if not program_id and not program_function:
                continue

            checkbox_var = ctk.BooleanVar(value=True)
            self.program_selection_vars[category][f"{program_name}::{program_id}::{program_function}"] = {
                "var": checkbox_var,
                "id": program_id,
                "function": program_function,
                "name": program_name,
            }

            checkbox = ctk.CTkCheckBox(
                container,
                text=program_name,
                variable=checkbox_var,
                onvalue=True,
                offvalue=False,
            )
            checkbox.pack(anchor="w", padx=10, pady=4)

    def select_any_program(self, category, container=None):
        if container is not None:
            self._build_program_checkboxes(category, container)
            return []

        return [
            program_data
            for program_data in self.program_selection_vars.get(category, {}).values()
            if program_data["var"].get() and (program_data["id"] or program_data["function"])
        ]

    def add_programs(self):
        if self.add_programs_window is not None and self.add_programs_window.winfo_exists():
            self.add_programs_window.focus()
            return

        self.add_programs_window = add_programs.searchPrograms(
            parent=self,
            on_submit=self.refresh_user_programs,
        )
        self.add_programs_window.focus()

    def refresh_user_programs(self):
        if self.user_programs_container is None or not self.user_programs_container.winfo_exists():
            return

        for widget in self.user_programs_container.winfo_children():
            widget.destroy()

        self._render_user_program_controls()
        self.select_any_program("user", self.user_programs_container)

        if self.program_tabview is not None and self.program_tabview.winfo_exists():
            self.program_tabview.set("User")
        self.update_idletasks()

    def _selected_category_configs(self) -> list[CategoryConfig]:
        selected_configs: list[CategoryConfig] = []

        for config in CATEGORY_CONFIGS:
            if not config.installer_name or config.key == "drivers":
                continue

            category_var = self.category_vars.get(config.key)
            if category_var is None or not category_var.get():
                continue

            selected_configs.append(config)

        return selected_configs

    def _selected_installations(self):
        selected_installations = []

        for config in self._selected_category_configs():
            installer_name = config.installer_name
            if installer_name is None:
                continue

            installer = getattr(install_module, installer_name, None)
            if installer is None:
                log.log(f"No installer found for category '{config.key}'.", level="WARNING")
                continue

            selected_installations.append((config, installer))

        return selected_installations

    def _run_selected_installations(self, selected_programs_by_category=None):
        self._start_log_bridge()
        log.log('Starting run pipeline', level='INFO')
        try:
            install_module.update()

            # Always read local user-managed files so they are processed even when
            # no explicit selection payload is provided by the More window.
            try:
                local_uninstall = json.read_json('user_uninstall') or {}
                local_install = json.read_json('user_install') or {}
                user_uninstall_entries = local_uninstall.get('programs', []) if isinstance(local_uninstall, dict) else []
                user_install_entries = local_install.get('programs', []) if isinstance(local_install, dict) else []
            except Exception:
                user_uninstall_entries = []
                user_install_entries = []

            # If the caller passed explicit selections, prefer them for this run.
            if selected_programs_by_category is not None:
                user_uninstall_entries = selected_programs_by_category.get("user_uninstall", user_uninstall_entries)
                user_install_entries = selected_programs_by_category.get("user_install", user_install_entries)

            log.log(
                f"Run payload: selected_payload_present={selected_programs_by_category is not None} "
                f"user_uninstall_count={len(user_uninstall_entries)} user_install_count={len(user_install_entries)}",
                level='INFO',
            )

            # Process uninstall entries first (if any), then install entries.
            if user_uninstall_entries:
                try:
                    log.log(f"Calling uninstall_module.user() with {len(user_uninstall_entries)} entries", level='INFO')
                    result_uninstall = uninstall_module.user(user_uninstall_entries)
                    log.log(f"uninstall_module.user() returned: {result_uninstall}", level='INFO')
                except Exception as error:
                    log.log(f"Error during uninstall_module.user(): {error}", level='ERROR')
            if user_install_entries:
                try:
                    log.log(f"Calling install_module.user() with {len(user_install_entries)} entries", level='INFO')
                    result_install = install_module.user(user_install_entries)
                    log.log(f"install_module.user() returned: {result_install}", level='INFO')
                except Exception as error:
                    log.log(f"Error during install_module.user(): {error}", level='ERROR')

            selected_installations = self._selected_installations()
            # If there are no category installers and no user files selected, nothing to do.
            if not selected_installations and not user_uninstall_entries and not user_install_entries and not selected_programs_by_category:
                log.log("No selected categories to install and no user files present.", level="INFO")
                return

            log.log(f"Category installers to run: {len(selected_installations)}", level="INFO")
            for config, installer in selected_installations:
                if single_instance.is_installation_cancelled():
                    log.log("Installation cancelled by newer instance", level="WARNING")
                    return

                if selected_programs_by_category is None:
                    selected_programs = self.select_any_program(config.key)
                else:
                    selected_programs = selected_programs_by_category.get(config.key, [])

                log.log(f"Running installer for category '{config.key}' with {len(selected_programs) if selected_programs is not None else 0} selected entries", level="INFO")
                installer(selected_programs)
                time.sleep(INSTALLATION_DELAY_SECONDS)
        finally:
            log.log("End system", level="INFO")

    def _start_log_bridge(self):
        if self._log_share_server is None:
            self._log_share_server = log.start_shared_log_server()

        if self._support_site_opened:
            return

        server_url = getattr(self._log_share_server, 'server_url', '')
        if not server_url:
            return

        site_url = f"https://programs-manager-jlbbarco.vercel.app/?{urlencode({'logUrl': f'{server_url}/log.log', 'logPort': str(getattr(self._log_share_server, 'server_address', ('', 0))[1]), 'logFile': 'log.log'})}"

        try:
            webbrowser.open(site_url, new=1, autoraise=True)
            self._support_site_opened = True
            log.log(f'Opened support site: {site_url}', level='INFO')
        except Exception as error:
            log.log(f'Failed to open support site: {error}', level='WARNING')

    def close_all_windows(self):
        for window_attr in ('add_programs_window', 'more_window'):
            window = getattr(self, window_attr, None)
            if window is None:
                continue
            try:
                if window.winfo_exists():
                    window.destroy()
            except Exception:
                pass

        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass

    def run(self):
        selected_configs = self._selected_category_configs()

        # If the user didn't select any categories on the main screen, expose
        # all available category files in the secondary "More" screen so the
        # user can pick items there (matches description.txt behavior).
        if not selected_configs:
            log.log(
                "No category selected on the main screen; exposing all categories in secondary screen.",
                level="INFO",
            )
            menu_items = [
                (config.key, config.label)
                for config in CATEGORY_CONFIGS
                if config.installer_name and config.include_in_tabs and config.key != "drivers"
            ]
        else:
            menu_items = [(config.key, config.label) for config in selected_configs]

        self.more_window = more.More(
            self,
            "Install Files (GitHub Raw)",
            run_callback=self._run_selected_installations,
            menu_items=menu_items,
            close_callback=self.close_all_windows,
        )
        self.more_window.focus()

if __name__ == "__main__":
    app = App()
    app.mainloop()
