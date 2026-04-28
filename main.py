import importlib
import os
import subprocess
import sys
import time
import webbrowser
from urllib.parse import urlencode
from dataclasses import dataclass

try:
    from lib import add_programs, install as install_module, json, log, more, screen, system, uninstall as uninstall_module
    from lib.install import single_instance
except ModuleNotFoundError:
    # Compatibility mode for executions where "src" is already the working root.
    from lib import add_programs, install as install_module, json, log, more, screen, system, uninstall as uninstall_module
    from lib.install import single_instance

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
GRID_PADDING_X = 20
GRID_PADDING_Y = 5
PROGRAM_TAB_ROW = 10
INSTALLATION_DELAY_SECONDS = 3


@dataclass(frozen=True)
class CategoryConfig:
    key: str
    label: str
    row: int
    default_selected: bool = False
    supported_systems: tuple[str, ...] = ()
    include_in_tabs: bool = True
    installer_name: str | None = None


CATEGORY_CONFIGS = (
    CategoryConfig("customization", "Customization", 0, supported_systems=("Windows",), installer_name="customization"),
    CategoryConfig("development", "Developer Tools", 1, default_selected=True, installer_name="development"),
    CategoryConfig("drivers", "Drivers", 2, supported_systems=("Windows", "Linux"), installer_name="drivers"),
    CategoryConfig("essentials", "Essential Programs", 3, default_selected=True, installer_name="essentials"),
    CategoryConfig("games", "Games", 4, supported_systems=("Windows", "Linux"), installer_name="games"),
    CategoryConfig("screen", "Screen", 5, default_selected=True, installer_name="screen"),
    CategoryConfig("server", "Server Tools", 6, supported_systems=("Linux",), installer_name="server"),
    CategoryConfig("ti_tools", "TI Tools", 7, supported_systems=("Windows",), installer_name="ti_tools", include_in_tabs=False),
)


class App(ctk.CTk):  # type: ignore
    def __init__(self):
        super().__init__()

        self.system_name = system.nameSO()
        self.program_selection_vars = {}
        self.category_vars = {}
        self.category_checkboxes = {}
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

    def _build_options_frame(self):
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        for col in range(8):
            self.options_frame.grid_columnconfigure(col, weight=1)
        self.options_frame.grid_rowconfigure(PROGRAM_TAB_ROW - 1, weight=1)

        for config in CATEGORY_CONFIGS:
            self._create_category_checkbox(config)

    def _build_action_buttons(self):
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(pady=20, padx=10, row=5, column=0, sticky="e")

        self.uncheckAllOptions = ctk.CTkButton(
            settings_frame,
            text="Uncheck all options",
            command=self.uncheck_all_options,
        )
        self.uncheckAllOptions.grid(padx=5, pady=20, row=0, column=0)

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(pady=20, padx=10, row=5, column=1, sticky="e")

        run_button = ctk.CTkButton(button_frame, text="Run", command=self.run)
        run_button.grid(padx=5, pady=20, column=0, row=0)

    def _create_category_checkbox(self, config: CategoryConfig):
        variable = ctk.BooleanVar(value=config.default_selected)
        checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text=config.label,
            variable=variable,
            onvalue=True,
            offvalue=False,
        )

        self.category_vars[config.key] = variable
        self.category_checkboxes[config.key] = checkbox

        if self._should_display_category(config):
            checkbox.grid(
                padx=GRID_PADDING_X,
                pady=GRID_PADDING_Y,
                row=config.row,
                column=0,
                sticky="w",
            )

    def _should_display_category(self, config: CategoryConfig) -> bool:
        if not config.supported_systems:
            return True
        return any(system_name in self.system_name for system_name in config.supported_systems)

    def uncheck_all_options(self):
        for checkbox in self.category_checkboxes.values():
            checkbox.deselect()

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
        user_uninstall_entries = []
        user_install_entries = []
        if selected_programs_by_category is not None:
            user_uninstall_entries = selected_programs_by_category.get("user_uninstall", [])
            user_install_entries = selected_programs_by_category.get("user_install", [])

            if user_uninstall_entries:
                uninstall_module.user(user_uninstall_entries)

        selected_installations = self._selected_installations()
        if not selected_installations and not selected_programs_by_category:
            log.log("No selected categories to install.", level="INFO")
            return

        for config, installer in selected_installations:
            if single_instance.is_installation_cancelled():
                log.log("Installation cancelled by newer instance", level="WARNING")
                return

            if selected_programs_by_category is None:
                selected_programs = self.select_any_program(config.key)
            else:
                selected_programs = selected_programs_by_category.get(config.key, [])

            installer(selected_programs)
            time.sleep(INSTALLATION_DELAY_SECONDS)

        if selected_programs_by_category is None:
            return

        if user_install_entries:
            install_module.user(user_install_entries)

    def _start_log_bridge(self):
        if self._log_share_server is None:
            self._log_share_server = log.start_shared_log_server()

        if self._support_site_opened:
            return

        server_url = getattr(self._log_share_server, 'server_url', '')
        if not server_url:
            return

        site_url = f"https://programs-manager-website.vercel.app/?{urlencode({'logUrl': f'{server_url}/log.log', 'logPort': str(getattr(self._log_share_server, 'server_address', ('', 0))[1]), 'logFile': 'log.log'})}"

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
        menu_items = [(config.key, config.label) for config in selected_configs]

        if not menu_items:
            log.log("No supported categories selected for installation.", level="INFO")
            return

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
