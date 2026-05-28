import subprocess

from lib import log


def install(data, system):
    for item in data:
        try:
            if system == 'Windows':
                subprocess.run(["winget", "install", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements",], check=True)
            elif system == 'Linux':
                subprocess.run(["sudo", "apt", "install", "-y", item['id']], check=True)
            elif system == 'MacOS':
                subprocess.run(["brew", "install", item['id']], check=True)
            log.log(f"Installed {item['name']} successfully.", level="INFO")
        except subprocess.CalledProcessError as e:
            log.log(f"Failed to install {item['name']}: {e}", level="ERROR")

