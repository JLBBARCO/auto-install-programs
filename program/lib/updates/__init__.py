def update_package_manager(nameSO, log):
    import subprocess

    name_so = nameSO

    try:
        if name_so == "Windows":
            subprocess.run(["winget", "upgrade", "--id", 'Microsoft.AppInstaller'], check=True)
            log("Package manager updated successfully.", level="INFO")
        elif name_so == "Linux":
            subprocess.run(["sudo", "apt", "update"], check=True)
            log("Package manager updated successfully.", level="INFO")
        elif name_so == "MacOS":
            subprocess.run(["brew", "update"], check=True)
            log("Package manager updated successfully.", level="INFO")
        else:
            log(f"Unsupported operating system: {name_so}", level="ERROR")
    except subprocess.CalledProcessError as e:
        log(f"Failed to update package manager: {e}", level="ERROR")