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

def installation():
    name = nameSO()

    if name == "Windows":
        return "bat"
    elif name == "Linux" or name == "MacOS":
        return "sh"
    else:
        return "Unknown"