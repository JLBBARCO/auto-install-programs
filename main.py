import subprocess
import sys
import importlib
import os
import time
try:
    from src.lib import installations, log, system, json, add_programs
    from src.lib.installations import single_instance
except ModuleNotFoundError:
    # Compatibility mode for executions where "src" is already the working root.
    from lib import installations, log, system, json, add_programs
    from lib.installations import single_instance
try:
    import customtkinter as ctk
except ImportError:
    # try installing missing requirements and re-importing
    subprocess.run([sys.executable, "-m", "pip", "install", "requirements.txt"], check=True)
    try:
        ctk = importlib.import_module('customtkinter')
    except Exception:
        sys.exit("customtkinter is required. Install dependencies and run again.")
# ensure the working directory is predictable when the app is frozen
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))

# * Main Variables
systemName = f"{system.nameSO()} Installations"

# * Single Instance Control
# The application allows multiple GUI windows to be opened simultaneously,
# but only the most recently started installation will execute.
# When a new installation begins, any previous running installation is
# automatically cancelled and terminated, ensuring no conflicts between
# concurrent installation processes.

class App(ctk.CTk):  # type: ignore
    def __init__(self):
        super().__init__()

        self.program_selection_vars = {}
        self.add_programs_window = None

        log.log('Program started', level="INFO")
        ctk.set_appearance_mode("system")

        self.title(systemName)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Keep the app inside the visible screen area on smaller displays.
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_w = min(1200, max(900, int(screen_w * 0.9)))
        window_h = min(820, max(620, int(screen_h * 0.88)))
        self.geometry(f"{window_w}x{window_h}")

        self.labelTitle = ctk.CTkLabel(self, text=f"Welcome to the {system.nameSO()} Installations", font=ctk.CTkFont(size=16, weight="bold"))
        self.labelTitle.grid(pady=10, padx=10, columnspan=2, row=0)

        self.labelCheck = ctk.CTkLabel(self, text="Select the programs you want to install:")
        self.labelCheck.grid(pady=10, padx=10, columnspan=2, row=1)

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")
        for col in range(8):
            self.options_frame.grid_columnconfigure(col, weight=1)
        self.options_frame.grid_rowconfigure(1, weight=1)

        self.checkedButtonDrivers = ctk.BooleanVar()
        self.checkButtonDrivers = ctk.CTkCheckBox(self.options_frame, text="Drivers", onvalue=True, offvalue=False, variable=self.checkedButtonDrivers)

        self.checkedButtonEssentials = ctk.BooleanVar()
        self.checkButtonEssentials = ctk.CTkCheckBox(self.options_frame, text="Essential Programs", onvalue=True, offvalue=False, variable=self.checkedButtonEssentials)
        self.checkButtonEssentials.select()
        self.checkButtonEssentials.grid(padx=20, pady=5, row=0, column=1, sticky="w")

        self.checkedButtonScreen = ctk.BooleanVar()
        self.checkButtonScreen = ctk.CTkCheckBox(self.options_frame, text="Screen", onvalue=True, offvalue=False, variable=self.checkedButtonScreen)
        self.checkButtonScreen.select()
        self.checkButtonScreen.grid(padx=20, pady=5, row=0, column=2, sticky="w")

        self.checkedButtonCustomization = ctk.BooleanVar()
        self.checkButtonCustomization = ctk.CTkCheckBox(self.options_frame, text="Customization", onvalue=True, offvalue=False, variable=self.checkedButtonCustomization)

        self.checkedButtonDevelopment = ctk.BooleanVar()
        self.checkButtonDevelopment = ctk.CTkCheckBox(self.options_frame, text="Developer Tools", onvalue=True, offvalue=False, variable=self.checkedButtonDevelopment)
        self.checkButtonDevelopment.select()
        self.checkButtonDevelopment.grid(padx=20, pady=5, row=0, column=4, sticky="w")

        self.checkedButtonServer = ctk.BooleanVar()
        self.checkButtonServer = ctk.CTkCheckBox(self.options_frame, text="Server Tools", onvalue=True, offvalue=False, variable=self.checkedButtonServer)

        self.checkedButtonGames = ctk.BooleanVar()
        self.checkButtonGames = ctk.CTkCheckBox(self.options_frame, text="Games", onvalue=True, offvalue=False, variable=self.checkedButtonGames)

        self.checkedButtonOffice = ctk.BooleanVar()
        self.checkButtonOffice = ctk.CTkCheckBox(self.options_frame, text="Office", onvalue=True, offvalue=False, variable=self.checkedButtonOffice)

        self.checkedButtonUser = ctk.BooleanVar()
        self.checkButtonUser = ctk.CTkCheckBox(self.options_frame, text='User', onvalue=True, offvalue=False, variable=self.checkedButtonUser)
        self.checkButtonUser.select()
        self.checkButtonUser.grid(padx=20, pady=5, row=0, column=7, sticky="w")

        # Program list containers inside a tabview — one tab per category prevents
        # side-by-side overflow that would make the window wider than the screen.
        self.programTabview = ctk.CTkTabview(self.options_frame, height=280)
        self.programTabview.grid(row=1, column=0, columnspan=8, padx=10, pady=5, sticky="nsew")

        _tab = self.programTabview.add("Essentials")
        self.containerEssentials = ctk.CTkScrollableFrame(_tab)
        self.containerEssentials.pack(fill="both", expand=True)
        self.selectAnyoneProgram("essentials", self.containerEssentials)
        if system.nameSO() == 'Windows':
            ctk.CTkLabel(self.containerEssentials, text="── Office ──", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=(10, 4))
            self.selectAnyoneProgram("office", self.containerEssentials)

        _tab = self.programTabview.add("Screen")
        self.containerScreen = ctk.CTkScrollableFrame(_tab)
        self.containerScreen.pack(fill="both", expand=True)
        self.selectAnyoneProgram("screen", self.containerScreen)

        _tab = self.programTabview.add("Development")
        self.containerDevelopment = ctk.CTkScrollableFrame(_tab)
        self.containerDevelopment.pack(fill="both", expand=True)
        self.selectAnyoneProgram("development", self.containerDevelopment)

        _tab = self.programTabview.add("User")
        self.containerUser = ctk.CTkScrollableFrame(_tab)
        self.containerUser.pack(fill="both", expand=True)
        self.selectAnyoneProgram('user', self.containerUser)

        if system.nameSO() in ('Windows', 'Linux'):
            _tab = self.programTabview.add("Drivers")
            self.containerDrivers = ctk.CTkScrollableFrame(_tab)
            self.containerDrivers.pack(fill="both", expand=True)
            self.selectAnyoneProgram("drivers", self.containerDrivers)

        if system.nameSO() == 'Windows':
            _tab = self.programTabview.add("Customization")
            self.containerCustomization = ctk.CTkScrollableFrame(_tab)
            self.containerCustomization.pack(fill="both", expand=True)
            self.selectAnyoneProgram("customization", self.containerCustomization)

        if system.nameSO() in ('Windows', 'Linux'):
            _tab = self.programTabview.add("Games")
            self.containerGames = ctk.CTkScrollableFrame(_tab)
            self.containerGames.pack(fill="both", expand=True)
            self.selectAnyoneProgram("games", self.containerGames)

        if system.nameSO() == 'Linux':
            _tab = self.programTabview.add("Server")
            self.containerServer = ctk.CTkScrollableFrame(_tab)
            self.containerServer.pack(fill="both", expand=True)
            self.selectAnyoneProgram("server", self.containerServer)

        self.containerSettings = ctk.CTkFrame(self)
        self.containerSettings.grid(pady=20, padx=10, row=5, column=0, sticky='e')

        self.addProgramsButton = ctk.CTkButton(self.containerSettings, text="Add Programs", command=self.addPrograms)
        self.addProgramsButton.grid(padx=5, pady=20)

        self.containerButtons = ctk.CTkFrame(self)
        self.containerButtons.grid(pady=20, padx=10, row=5, column=1, sticky="e")

        self.submitButton = ctk.CTkButton(self.containerButtons, text="Install", command=self.install)
        self.submitButton.grid(padx=5, pady=20, column=0, row=0)

        self.cancelButton = ctk.CTkButton(self.containerButtons, text="Cancel", command=self.cancel)
        self.cancelButton.grid(padx=5, pady=20, column=1, row=0)

        if system.nameSO() == 'Windows':
            self.checkButtonDrivers.select()
            self.checkButtonDrivers.grid(padx=20, pady=5, row=0, column=0, sticky="w")

            self.checkButtonCustomization.select()
            self.checkButtonCustomization.grid(padx=20, pady=5, row=0, column=3, sticky="w")

            self.checkButtonOffice.select()
            self.checkButtonOffice.grid(padx=20, pady=5, row=0, column=5, sticky="w")

            self.checkButtonGames.select()
            self.checkButtonGames.grid(padx=20, pady=5, row=0, column=6, sticky="w")

        if 'Linux' in system.nameSO():
            self.checkButtonDrivers.select()
            self.checkButtonDrivers.grid(padx=20, pady=5, row=0, column=0, sticky="w")

            self.checkButtonServer.select()
            self.checkButtonServer.grid(padx=20, pady=5, row=0, column=5, sticky="w")

            self.checkButtonGames.select()
            self.checkButtonGames.grid(padx=20, pady=5, row=0, column=6, sticky="w")

    def selectAnyoneProgram(self, category, container=None):
        programsArray = json.read_json(category)
        if not programsArray:
            log.log(f"Could not load JSON data for category {category}.", "WARNING")
            return []

        programs = programsArray.get('programs', [])
        if not programs:
            log.log(f"No 'programs' key found in JSON file for category {category}.", "WARNING")
            return []

        if container is not None:
            # Build one active checkbox per JSON program entry and persist vars.
            self.program_selection_vars[category] = {}
            programs_sorted = sorted(programs, key=lambda p: str(p.get('name', '')).lower())
            for program in programs_sorted:
                if not isinstance(program, dict):
                    continue

                program_name = str(program.get('name', '')).strip()
                program_id = str(program.get('id', '')).strip()
                if not program_name:
                    continue

                checkbox_var = ctk.BooleanVar(value=True)
                key = f"{program_name}::{program_id}"
                self.program_selection_vars[category][key] = {
                    "var": checkbox_var,
                    "id": program_id,
                }

                checkbox = ctk.CTkCheckBox(
                    container,
                    text=program_name,
                    variable=checkbox_var,
                    onvalue=True,
                    offvalue=False,
                )
                checkbox.pack(anchor="w", padx=10, pady=4)

            return []

        selected_programs = []
        for program_data in self.program_selection_vars.get(category, {}).values():
            if program_data["var"].get() and program_data["id"]:
                selected_programs.append(program_data["id"])
        return selected_programs

    def addPrograms(self):
        if self.add_programs_window is not None and self.add_programs_window.winfo_exists():
            self.add_programs_window.focus()
            return

        self.add_programs_window = add_programs.searchPrograms(parent=self, on_submit=self.refresh_user_programs)
        self.add_programs_window.focus()

    def refresh_user_programs(self):
        if not hasattr(self, 'containerUser'):
            return
        for widget in self.containerUser.winfo_children():
            widget.destroy()
        self.selectAnyoneProgram('user', self.containerUser)
        self.programTabview.set('User')
        self.update_idletasks()

    def showAllPrograms(self):
        self.programTabview.grid(row=1, column=0, columnspan=8, padx=10, pady=5, sticky="nsew")
        self.update_idletasks()

    def install(self):
        self.destroy()  # Close the GUI before starting installations

        log.log('Update installation package', level='INFO')
        installations.update()

        # Acquire installation lock - this will cancel any previous installation
        log.log('Acquiring installation lock...', level="INFO")
        single_instance.acquire_installation_lock()
        time.sleep(3)

        try:
            if self.checkedButtonDrivers.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("drivers")
                log.log(f'Install Drivers: {self.checkedButtonDrivers.get()}')
                installations.drivers(selected_programs)
                time.sleep(3)

            if self.checkedButtonEssentials.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("essentials")
                log.log(f'Install Essential Programs: {self.checkedButtonEssentials.get()}')
                installations.essentials(selected_programs)
                time.sleep(3)

            if self.checkedButtonOffice.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("office")
                log.log(f'Install Office: {self.checkedButtonOffice.get()}')
                installations.office(selected_programs)
                time.sleep(3)

            if self.checkedButtonDevelopment.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("development")
                log.log(f'Install Development Programs: {self.checkedButtonDevelopment.get()}')
                installations.development(selected_programs)
                time.sleep(3)

            if self.checkedButtonGames.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("games")
                log.log(f'Install Games: {self.checkedButtonGames.get()}')
                installations.games(selected_programs)
                time.sleep(3)

            if self.checkedButtonScreen.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("screen")
                log.log(f'Install Screen: {self.checkedButtonScreen.get()}')
                installations.screen(selected_programs)
                time.sleep(3)

            if self.checkedButtonServer.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("server")
                log.log(f'Install Server: {self.checkedButtonServer.get()}')
                installations.server(selected_programs)
                time.sleep(3)

            if self.checkedButtonCustomization.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("customization")
                log.log(f'Install Customization: {self.checkedButtonCustomization.get()}')
                installations.customization(selected_programs)
                time.sleep(3)

            if self.checkedButtonUser.get():
                if single_instance.is_installation_cancelled():
                    log.log('Installation cancelled by newer instance', level="WARNING")
                    return
                selected_programs = self.selectAnyoneProgram("user")
                log.log(f'Install User Programs: {self.checkedButtonUser.get()}')
                installations.user(selected_programs)
                time.sleep(3)

            log.log('All installations completed successfully', level="INFO")
        finally:
            # Always release the lock when done
            single_instance.release_installation_lock()

    def cancel(self):
        log.log('Installation cancelled by the user')
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
