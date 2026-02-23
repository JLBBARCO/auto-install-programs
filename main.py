from src.lib import installations
from src.lib import log
import subprocess
import sys
try:
    import customtkinter as ctk
except Exception as error:
    log.log(f'Failed to import customtkinter: {error}')
    subprocess.run([r"src\lib\install_libs.bat"], shell=True)
    try:
        import importlib
        ctk = importlib.import_module('customtkinter')
    except Exception as error2:
        log.log(f'Failed to install/import customtkinter: {error2}')
        sys.exit("customtkinter is required. Instale dependências e execute novamente.")

# * Main Variables
systemName = "Windows Installations"
widthWindow = 400
heightWindow = 400

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        log.log('Program started')
        ctk.set_appearance_mode("system")

        self.title(systemName)
        self.geometry(f'{widthWindow}x{heightWindow}')

        self.container = ctk.CTkFrame(self)
        self.container.grid(pady=20, padx=50, row=0, column=0)

        self.labelTitle = ctk.CTkLabel(self.container, text="Welcome to the Windows Installations", font=ctk.CTkFont(size=16, weight="bold"))
        self.labelTitle.grid(pady=10, columnspan=2, row=0)

        self.labelCheck = ctk.CTkLabel(self.container, text="Select the programs you want to install:")
        self.labelCheck.grid(pady=10, columnspan=2, row=1)

        self.options_frame = ctk.CTkFrame(self.container)
        self.options_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.checkedButtonEssentials = ctk.BooleanVar()
        self.checkButtonEssentials = ctk.CTkCheckBox(self.options_frame, text="Essential Programs", onvalue=True, offvalue=False, variable=self.checkedButtonEssentials)
        self.checkButtonEssentials.select()
        self.checkButtonEssentials.grid(padx=20, pady=5, row=0, column=0, sticky="w")

        self.checkedButtonOffice = ctk.BooleanVar()
        self.checkButtonOffice = ctk.CTkCheckBox(self.options_frame, text="Microsoft Office", onvalue=True, offvalue=False, variable=self.checkedButtonOffice)
        self.checkButtonOffice.select()
        self.checkButtonOffice.grid(padx=20, pady=5, row=1, column=0, sticky="w")

        self.checkedButtonCustomization = ctk.BooleanVar()
        self.checkButtonCustomization = ctk.CTkCheckBox(self.options_frame, text="Customization", onvalue=True, offvalue=False, variable=self.checkedButtonCustomization)
        self.checkButtonCustomization.select()
        self.checkButtonCustomization.grid(padx=20, pady=5, row=2, column=0, sticky="w")

        self.checkedButtonDevelopment = ctk.BooleanVar()
        self.checkButtonDevelopment = ctk.CTkCheckBox(self.options_frame, text="Developer Tools", onvalue=True, offvalue=False, variable=self.checkedButtonDevelopment)
        self.checkButtonDevelopment.select()
        self.checkButtonDevelopment.grid(padx=20, pady=5, row=3, column=0, sticky="w")

        self.checkedButtonGames = ctk.BooleanVar()
        self.checkButtonGames = ctk.CTkCheckBox(self.options_frame, text="Games", onvalue=True, offvalue=False, variable=self.checkedButtonGames)
        self.checkButtonGames.select()
        self.checkButtonGames.grid(padx=20, pady=5, row=4, column=0, sticky="w")

        self.submitButton = ctk.CTkButton(self.container, text="Install", command=self.install)
        self.submitButton.grid(pady=20, column=0, row=3)

        self.cancelButton = ctk.CTkButton(self.container, text="Cancel", command=self.cancel)
        self.cancelButton.grid(pady=20, column=1, row=3)

    def install(self):
        self.destroy()

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
            log.log(f'Install Games Programs: {self.checkedButtonGames.get()}')
            log.log(installations.games())

        if self.checkedButtonCustomization.get():
            log.log(f'Install Customizations: {self.checkedButtonCustomization.get()}')
            log.log(installations.customization())

    def cancel(self):
        log.log('Installation cancelled by the user')
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
