from src.lib.externalLibs import ctk
from src.lib import installations, log, system

# * Main Variables
systemName = f"{system.nameSO()} Installations"

class App(ctk.CTk):  # type: ignore
    def __init__(self):
        super().__init__()

        log.log('Program started', level="INFO")
        ctk.set_appearance_mode("system")

        self.title(systemName)

        self.container = ctk.CTkFrame(self)
        self.container.grid(pady=20, padx=50, row=0, column=0)

        self.labelTitle = ctk.CTkLabel(self.container, text=f"Welcome to the {system.nameSO()} Installations", font=ctk.CTkFont(size=16, weight="bold"))
        self.labelTitle.grid(pady=10, padx=10, columnspan=2, row=0)

        self.labelCheck = ctk.CTkLabel(self.container, text="Select the programs you want to install:")
        self.labelCheck.grid(pady=10, padx=10, columnspan=2, row=1)

        self.options_frame = ctk.CTkFrame(self.container)
        self.options_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        self.checkedButtonDrivers = ctk.BooleanVar()
        self.checkButtonDrivers = ctk.CTkCheckBox(self.options_frame, text="Drivers", onvalue=True, offvalue=False, variable=self.checkedButtonDrivers)

        self.checkedButtonEssentials = ctk.BooleanVar()
        self.checkButtonEssentials = ctk.CTkCheckBox(self.options_frame, text="Essential Programs", onvalue=True, offvalue=False, variable=self.checkedButtonEssentials)
        self.checkButtonEssentials.select()
        self.checkButtonEssentials.grid(padx=20, pady=5, row=1, column=0, sticky="w")

        self.checkedButtonOffice = ctk.BooleanVar()
        self.checkButtonOffice = ctk.CTkCheckBox(self.options_frame, text="Microsoft Office", onvalue=True, offvalue=False, variable=self.checkedButtonOffice)

        self.checkedButtonScreen = ctk.BooleanVar()
        self.checkButtonScreen = ctk.CTkCheckBox(self.options_frame, text="Screen", onvalue=True, offvalue=False, variable=self.checkedButtonScreen)
        self.checkButtonScreen.select()
        self.checkButtonScreen.grid(padx=20, pady=5, row=3, column=0, sticky="w")

        self.checkedButtonCustomization = ctk.BooleanVar()
        self.checkButtonCustomization = ctk.CTkCheckBox(self.options_frame, text="Customization", onvalue=True, offvalue=False, variable=self.checkedButtonCustomization)

        self.checkedButtonDevelopment = ctk.BooleanVar()
        self.checkButtonDevelopment = ctk.CTkCheckBox(self.options_frame, text="Developer Tools", onvalue=True, offvalue=False, variable=self.checkedButtonDevelopment)
        self.checkButtonDevelopment.select()
        self.checkButtonDevelopment.grid(padx=20, pady=5, row=4, column=0, sticky="w")

        self.checkedButtonServer = ctk.BooleanVar()
        self.checkButtonServer = ctk.CTkCheckBox(self.options_frame, text="Server Tools", onvalue=True, offvalue=False, variable=self.checkedButtonServer)

        self.checkedButtonGames = ctk.BooleanVar()
        self.checkButtonGames = ctk.CTkCheckBox(self.options_frame, text="Games", onvalue=True, offvalue=False, variable=self.checkedButtonGames)

        self.submitButton = ctk.CTkButton(self.container, text="Install", command=self.install)
        self.submitButton.grid(pady=20, column=0, row=3)

        self.cancelButton = ctk.CTkButton(self.container, text="Cancel", command=self.cancel)
        self.cancelButton.grid(pady=20, column=1, row=3)

        if system.nameSO() == 'Windows':
            self.checkButtonDrivers.select()
            self.checkButtonDrivers.grid(padx=20, pady=5, row=0, column=0, sticky="w")

            self.checkButtonOffice.select()
            self.checkButtonOffice.grid(padx=20, pady=5, row=2, column=0, sticky="w")

            self.checkButtonCustomization.select()
            self.checkButtonCustomization.grid(padx=20, pady=5, row=4, column=0, sticky="w")

            self.checkButtonGames.select()
            self.checkButtonGames.grid(padx=20, pady=5, row=6, column=0, sticky="w")

        if 'Linux' in system.nameSO():
            self.checkButtonDrivers.select()
            self.checkButtonDrivers.grid(padx=20, pady=5, row=0, column=0, sticky="w")

            self.checkButtonServer.select()
            self.checkButtonServer.grid(padx=20, pady=5, row=5, column=0, sticky="w")

    def install(self):
        self.destroy()  # Close the GUI before starting installations
        
        if self.checkedButtonEssentials.get():
            log.log(f'Install Essential Programs: {self.checkedButtonEssentials.get()}')
            log.log(installations.essentials())

        if self.checkedButtonOffice.get():
            log.log(f'Install Office: {self.checkedButtonOffice.get()}')
            log.log(installations.office())

        if self.checkedButtonDevelopment.get():
            log.log(f'Install Development Programs: {self.checkedButtonDevelopment.get()}')
            log.log(installations.development())

        if self.checkedButtonGames.get():
            log.log(f'Install Games: {self.checkedButtonGames.get()}')
            log.log(installations.games())

        if self.checkedButtonScreen.get():
            log.log(f'Install Screen: {self.checkedButtonScreen.get()}')
            log.log(installations.screen())

        if self.checkedButtonServer.get():
            log.log(f'Install Server: {self.checkedButtonServer.get()}')
            log.log(installations.server())

        if self.checkedButtonCustomization.get():
            log.log(f'Install Customization: {self.checkedButtonCustomization.get()}')
            log.log(installations.customization())

    def cancel(self):
        log.log('Installation cancelled by the user')
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
