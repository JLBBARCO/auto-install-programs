import platform

def nameSO():
    system = platform.system()

    if system == "Windows":
        return "Windows"
    elif system == "Darwin":
        return "MacOS"
    elif system == "Linux":
        return "Linux"
    else:
        return "Unknown"