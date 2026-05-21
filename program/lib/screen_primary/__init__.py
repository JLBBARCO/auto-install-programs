from typing import Tuple
import customtkinter as ctk
from dataclasses import dataclass


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
    CategoryConfig("customization", "Customization", 0, supported_systems=("Windows",), installer_name="customization.json"),
    CategoryConfig("development", "Developer Tools", 1, default_selected=True, installer_name="development.json"),
    CategoryConfig("drivers", "Drivers", 2, supported_systems=("Windows", "Linux"), installer_name="driver.json"),
    CategoryConfig("essentials", "Essential Programs", 3, default_selected=True, installer_name="essential.json"),
    CategoryConfig("games", "Games", 4, supported_systems=("Windows", "Linux"), installer_name="game.json"),
    CategoryConfig("screen", "Screen", 5, default_selected=True, installer_name="screen.json"),
    CategoryConfig("server", "Server Tools", 6, supported_systems=("Linux",), installer_name="server.json"),
    CategoryConfig("ti_tools", "TI Tools", 7, supported_systems=("Windows",), installer_name="ti_tools.json", include_in_tabs=False),
)
GRID_PADDING_X = 20
GRID_PADDING_Y = 5
PROGRAM_TAB_ROW = 10


class ScreenPrimary(ctk.CTk):
    def __init__(self, operational_system: str, theme: str):
        super().__init__()
        ctk.set_appearance_mode(theme)
        self.title(f'{operational_system} Programs Manager')
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.category_vars = {}
        self.category_checkboxes = {}
        self.system_name = operational_system

        self.main_title = ctk.CTkLabel(self, text=f'{self.system_name} Programs Manager', font=ctk.CTkFont(size=16, weight="bold"))
        self.main_title.grid(pady=10, row=0, columnspan=2)

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(columnspan=2, sticky='n')
        
        for col in range(8):
            self.options_frame.grid_columnconfigure(col, weight=1)
        self.options_frame.grid_rowconfigure(PROGRAM_TAB_ROW - 1, weight=1)

        for config in CATEGORY_CONFIGS:
            self._create_category_checkbox(config)

        self.buttons_option_frame = ctk.CTkFrame(self)
        self.buttons_option_frame.grid(padx=10, pady=10, row=2, column=0, sticky='ws')

        initial_text = 'Unselect all' if self._all_visible_categories_selected() else 'Select all'
        self.toggle_button = ctk.CTkButton(self.buttons_option_frame, text=initial_text, command=self.toggle_all_options)
        self.toggle_button.grid(padx=10, pady=10, row=0)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(padx=10, pady=10, row=2, column=1, sticky='es')

        self.button_next = ctk.CTkButton(self.button_frame, text='Next', command=self.next)
        self.button_next.grid(padx=10, pady=10, row=0)


    def _should_display_category(self, config: CategoryConfig) -> bool:
        if not config.supported_systems:
            return True
        return any(system_name in self.system_name for system_name in config.supported_systems)


    def _create_category_checkbox(self, config: CategoryConfig):
        variable = ctk.BooleanVar(value=config.default_selected)
        checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text=config.label,
            variable=variable,
            onvalue=True,
            offvalue=False,
        )

        self.category_vars[config.installer_name] = variable
        self.category_checkboxes[config.installer_name] = checkbox

        if self._should_display_category(config):
            checkbox.grid(
                padx=GRID_PADDING_X,
                pady=GRID_PADDING_Y,
                row=config.row,
                column=0,
                sticky="w",
            )


    def next(self):
        self.destroy()
        self.array_json = []
        for installer_name, var in self.category_vars.items():
            if var.get():
                self.array_json.append(installer_name)


    def toggle_all_options(self):
        should_select_all = not self._all_visible_categories_selected()

        for config in CATEGORY_CONFIGS:
            if not self._should_display_category(config):
                continue

            category_var = self.category_vars.get(config.installer_name)
            if category_var is not None:
                category_var.set(should_select_all)
        # Update the toggle button text to reflect the new action
        self.toggle_button.configure(text='Unselect all' if should_select_all else 'Select all')


    def uncheck_all_options(self):
        for config in CATEGORY_CONFIGS:
            if not self._should_display_category(config):
                continue
            category_var = self.category_vars.get(config.installer_name)
            if category_var is not None:
                category_var.set(False)


    def _all_visible_categories_selected(self) -> bool:
        visible_configs = [config for config in CATEGORY_CONFIGS if self._should_display_category(config)]
        if not visible_configs:
            return False

        for config in visible_configs:
            category_var = self.category_vars.get(config.installer_name)
            if category_var is None or not category_var.get():
                return False
        return True


    def return_array(self):
        if self.array_json:
            return self.array_json