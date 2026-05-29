import subprocess

from time import sleep

from lib import log, web


def install(data, system):
    for item in data:
        try:
            web.wait_for_internet_connection()
            if system == 'Windows':
                subprocess.run(["winget", "install", "--id", item['id'], "-e", "--accept-source-agreements", "--accept-package-agreements",], check=True)
            elif system == 'Linux':
                subprocess.run(["sudo", "apt", "install", "-y", item['id']], check=True)
            elif system == 'MacOS':
                subprocess.run(["brew", "install", item['id']], check=True)
            log.log(f"Installed {item['name']} successfully.", level="INFO")
        except subprocess.CalledProcessError as e:
            log.log(f"Failed to install {item['name']}: {e}", level="ERROR")

        for _ in range(10):
            web.wait_for_internet_connection()
            sleep(0.1)

