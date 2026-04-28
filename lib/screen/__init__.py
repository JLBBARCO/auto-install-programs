from typing import Callable

import customtkinter as ctk


class Screen(ctk.CTkToplevel):
    def __init__(
        self,
        parent=None,
        title: str = "Select Programs",
        options: list[dict] | None = None,
        search_handler: Callable[[str], list[dict]] | None = None,
        submit_handler: Callable[[dict[str, list[dict]]], None] | None = None,
        submit_text: str = "Submit",
    ):
        super().__init__(parent)
        self.title(title)

        self.search_handler = search_handler
        self.submit_handler = submit_handler
        self.selection_state: dict[str, dict[str, dict]] = {}
        self.section_containers: dict[str, ctk.CTkScrollableFrame] = {}
        self.section_modes: dict[str, str] = {}
        self.section_labels: dict[str, str] = {}
        self.search_section_key: str | None = None

        if parent is not None:
            self.transient(parent)
            self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.header_label.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="w")

        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=12, pady=(6, 12), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)

        self.search_frame = ctk.CTkFrame(self.content_frame)
        self.search_frame.grid(row=0, column=0, padx=10, pady=(10, 6), sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)

        self.search_input = ctk.CTkEntry(self.search_frame, placeholder_text="Search")
        self.search_input.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.search_button = ctk.CTkButton(self.search_frame, text="Search", width=110, command=self._on_search)
        self.search_button.grid(row=0, column=1, padx=(0, 0), pady=8)

        if self.search_handler is None:
            self.search_frame.grid_remove()

        self.content_title = ctk.CTkLabel(
            self.content_frame,
            text="Options",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.content_title.grid(row=1, column=0, padx=10, pady=(2, 6), sticky="ew")

        self.options_frame = ctk.CTkFrame(self.content_frame)
        self.options_frame.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="nsew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.options_frame, height=330)
        self.tabview.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        self.status_label = ctk.CTkLabel(self.content_frame, text="", anchor="w")
        self.status_label.grid(row=3, column=0, padx=10, pady=(0, 8), sticky="ew")

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="ew")
        self.button_frame.grid_columnconfigure(0, weight=1)

        self.submit_button = ctk.CTkButton(self.button_frame, text=submit_text, command=self._submit)
        self.submit_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")

        self.set_options(options or [])

    def set_options(self, options: list[dict]):
        self.selection_state.clear()
        self.section_containers.clear()
        self.section_modes.clear()
        self.section_labels.clear()
        self.search_section_key = None

        for widget in self.tabview.winfo_children():
            widget.destroy()

        if not options:
            self.status_label.configure(text="No options provided.")
            self.submit_button.configure(state="disabled")
            return

        self.submit_button.configure(state="normal")

        for section in options:
            section_key = str(section.get("key", "")).strip()
            section_label = str(section.get("label", section_key)).strip()
            selection_type = str(section.get("selection_type", "checkbox")).strip().lower()
            items = section.get("items", [])

            if not section_key or not section_label:
                continue

            self.selection_state[section_key] = {}
            self.section_modes[section_key] = selection_type
            self.section_labels[section_key] = section_label

            if section.get("search_target"):
                self.search_section_key = section_key

            tab = self.tabview.add(section_label)
            container = ctk.CTkScrollableFrame(tab)
            container.pack(fill="both", expand=True, padx=10, pady=10)
            container.grid_columnconfigure(0, weight=0)
            container.grid_columnconfigure(1, weight=1)
            self.section_containers[section_key] = container

            self._render_section_items(section_key, items)

        if self.section_labels:
            first_key = next(iter(self.section_labels.keys()))
            self.tabview.set(self.section_labels[first_key])
            self.content_title.configure(text=self.section_labels[first_key])

    def _item_key(self, item: dict) -> str:
        name = str(item.get("name", "")).strip()
        item_id = str(item.get("id", "")).strip()
        item_function = str(item.get("function", "")).strip()
        return f"{name}::{item_id}::{item_function}"

    def _render_section_items(self, section_key: str, items: list[dict]):
        container = self.section_containers.get(section_key)
        if container is None:
            return

        for widget in container.winfo_children():
            widget.destroy()

        mode = self.section_modes.get(section_key, "checkbox")
        sorted_items = sorted(
            [item for item in items if isinstance(item, dict)],
            key=lambda item: str(item.get("name", "")).lower(),
        )

        if not sorted_items:
            ctk.CTkLabel(container, text="No items found.", anchor="w").grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="w")
            return

        for row_index, item in enumerate(sorted_items):
            item_name = str(item.get("name", "")).strip()
            item_id = str(item.get("id", "")).strip()
            item_function = str(item.get("function", "")).strip()
            if not item_name:
                continue

            key = self._item_key(item)
            if key not in self.selection_state[section_key]:
                default_selected = bool(item.get("selected", False))
                self.selection_state[section_key][key] = {
                    "selected": default_selected,
                    "item": {
                        "name": item_name,
                        "id": item_id,
                        "function": item_function,
                    },
                }

            item_state = self.selection_state[section_key][key]

            if mode == "button":
                action_button = ctk.CTkButton(
                    container,
                    width=100,
                    text="Remove" if item_state["selected"] else "Add",
                    command=lambda s=section_key, k=key: self._toggle_button_item(s, k),
                )
                action_button.grid(row=row_index, column=0, padx=8, pady=4, sticky="w")
                item_state["button"] = action_button
            else:
                checkbox_var = ctk.BooleanVar(value=bool(item_state["selected"]))
                checkbox = ctk.CTkCheckBox(
                    container,
                    text="",
                    variable=checkbox_var,
                    onvalue=True,
                    offvalue=False,
                    command=lambda s=section_key, k=key, v=checkbox_var: self._toggle_checkbox_item(s, k, v),
                )
                checkbox.grid(row=row_index, column=0, padx=8, pady=4, sticky="w")
                item_state["var"] = checkbox_var

            item_text = item_name
            if item_id:
                item_text = f"{item_name} ({item_id})"
            elif item_function:
                item_text = f"{item_name} ({item_function})"

            ctk.CTkLabel(container, text=item_text, anchor="w").grid(
                row=row_index,
                column=1,
                padx=8,
                pady=4,
                sticky="w",
            )

    def _toggle_button_item(self, section_key: str, key: str):
        state = self.selection_state.get(section_key, {}).get(key)
        if not state:
            return

        state["selected"] = not bool(state.get("selected"))
        button = state.get("button")
        if button is not None:
            button.configure(text="Remove" if state["selected"] else "Add")

    def _toggle_checkbox_item(self, section_key: str, key: str, checkbox_var: ctk.BooleanVar):
        state = self.selection_state.get(section_key, {}).get(key)
        if not state:
            return
        state["selected"] = bool(checkbox_var.get())

    def _on_search(self):
        if self.search_handler is None:
            return

        query = self.search_input.get().strip()
        if not query:
            self.status_label.configure(text="Type something to search.")
            return

        try:
            results = self.search_handler(query)
            if not self.search_section_key:
                self.status_label.configure(text="Search target is not configured.")
                return

            # Preserve already selected entries when new search results are rendered.
            old_state = self.selection_state.get(self.search_section_key, {})
            self.selection_state[self.search_section_key] = {}
            for item in results:
                key = self._item_key(item)
                if key in old_state and old_state[key].get("selected"):
                    item["selected"] = True

            self._render_section_items(self.search_section_key, results)
            self.status_label.configure(text=f"{len(results)} result(s) found.")
        except Exception as error:
            self.status_label.configure(text=f"Search failed: {error}")

    def _collect_selected(self) -> dict[str, list[dict]]:
        selected_by_section: dict[str, list[dict]] = {}

        for section_key, items in self.selection_state.items():
            selected_entries: list[dict] = []
            for item_state in items.values():
                if not bool(item_state.get("selected")):
                    continue
                item_payload = item_state.get("item")
                if isinstance(item_payload, dict):
                    selected_entries.append(dict(item_payload))
            selected_by_section[section_key] = selected_entries

        return selected_by_section

    def _submit(self):
        selected_by_section = self._collect_selected()
        if callable(self.submit_handler):
            self.submit_handler(selected_by_section)
        self.destroy()