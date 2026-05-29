import subprocess

from time import sleep

from lib import log, web


def uninstall(data, system):
    for item in data:
        try:
            web.wait_for_internet_connection()
            if system == 'Windows':
                subprocess.run(["winget", "uninstall", "--id", item['id']], check=True)
            elif system == 'Linux':
                subprocess.run(["sudo", "apt", "remove", "-y", item['id']], check=True)
            elif system == 'MacOS':
                subprocess.run(["brew", "uninstall", item['id']], check=True)
            log.log(f"Uninstalled {item['name']} successfully.", level="INFO")
        except subprocess.CalledProcessError as e:
            log.log(f"Failed to uninstall {item['name']}: {e}", level="ERROR")

        for _ in range(10):
            web.wait_for_internet_connection()
            sleep(0.1)

