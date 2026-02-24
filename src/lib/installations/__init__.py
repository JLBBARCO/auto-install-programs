import subprocess
import os

def install_program(program):
    process = subprocess.run(f"{program}.bat", capture_output=True, text=True, shell=True)
    return process.stdout + process.stderr

def essentials():
    return install_program("essentials")

def office():
    import shutil
    destinationPath = r"C:\office"
    files = ['setup.exe', 'settings.xml']

    os.makedirs(destinationPath, exist_ok=True)
    messages = []
    for file in files:
        try:
            shutil.copy(file, destinationPath)
            messages.append(f"Successfully copied {file} to {destinationPath}")
        except Exception as error:
            messages.append(f"Failed to copy {file} to {destinationPath}. Error: {error}")
    
    result = install_program("office")
    messages.append(result)
    return "\n".join(messages)

def development():
    return install_program("development")

def games():
    return install_program("games")

def customization():
    import winreg
    keyPath = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, keyPath, 0, winreg.KEY_SET_VALUE) as key:
            # Aplica tema escuro para apps
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
            # Aplica tema escuro para sistema
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)

        darkModeMessage = "Dark mode applied successfully."
    except Exception as error:
        darkModeMessage = f"Failed to apply dark mode. Error: {error}"

    os.system("taskkill /f /im explorer.exe")
    os.system("start explorer.exe")
    return install_program("customization") + darkModeMessage