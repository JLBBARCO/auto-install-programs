import customtkinter as ctk

class _ProgramSelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title: str, items: list[dict[str, str]], on_submit, default_selected: bool = False):
        super().__init__(parent)
        self.title(title)
        self.geometry("640x520")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.items = [item for item in items if isinstance(item, dict)]
        self.on_submit = on_submit
        self.default_selected = default_selected
        self.item_vars: list[tuple[dict[str, str], ctk.BooleanVar]] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        self.header_label.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        self.container_tabs = ctk.CTkTabview(self)
        self.container_tabs.grid(row=1, column=0, padx=12, pady=8, sticky="nsew")
        self.container_tabs.add("Programs")

        programs_tab = self.container_tabs.tab("Programs")
        programs_tab.grid_columnconfigure(0, weight=1)
        programs_tab.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(programs_tab)
        self.scroll_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        if not self.items:
            empty_label = ctk.CTkLabel(self.scroll_frame, text="No programs found.", anchor="w")
            empty_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        else:
            for row_index, item in enumerate(self.items):
                row_frame = ctk.CTkFrame(self.scroll_frame)
                row_frame.grid(row=row_index, column=0, padx=8, pady=6, sticky="ew")
                row_frame.grid_columnconfigure(0, weight=1)

                label_name = str(item.get("name", "")).strip()
                text = label_name

                checkbox_var = ctk.BooleanVar(value=self.default_selected)
                checkbox = ctk.CTkCheckBox(row_frame, text=text, variable=checkbox_var)
                checkbox.grid(row=0, column=0, padx=10, pady=10, sticky="w")
                self.item_vars.append((item, checkbox_var))

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=0)
        self.button_frame.grid_columnconfigure(2, weight=0)

        self.cancel_button = ctk.CTkButton(self.button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.grid(row=0, column=0, padx=(0, 8), pady=10, sticky="e")

        self.toggle_all_button = ctk.CTkButton(self.button_frame, text=self._toggle_all_label(), command=self._toggle_all)
        self.toggle_all_button.grid(row=0, column=1, padx=8, pady=10, sticky="e")

        self.submit_button = ctk.CTkButton(self.button_frame, text="Save", command=self._submit)
        self.submit_button.grid(row=0, column=2, padx=(8, 0), pady=10, sticky="e")

    def _toggle_all_label(self) -> str:
        if self.item_vars and all(variable.get() for _, variable in self.item_vars):
            return "Unselect all"
        return "Select all"

    def _toggle_all(self):
        should_select = not self.item_vars or not all(variable.get() for _, variable in self.item_vars)
        for _, checkbox_var in self.item_vars:
            checkbox_var.set(should_select)
        self.toggle_all_button.configure(text=self._toggle_all_label())

    def _submit(self):
        selected_items: list[dict[str, str]] = []
        for item, checkbox_var in self.item_vars:
            if checkbox_var.get():
                selected_items.append(item)

        if callable(self.on_submit):
            self.on_submit(selected_items)

        self.destroy()

