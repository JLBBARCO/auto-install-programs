import subprocess
import os
import shutil

def install_program(program):
    process = subprocess.run(f"{program}.bat", capture_output=True, text=True, shell=True)
    return process.stdout + process.stderr

def essentials():
    return install_program("essentials")

def office():
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
    return install_program("customization")