import re
import shutil
import subprocess

from lib import log, system


WINDOWS_DRIVER_INSTALLERS = {
    'nvidia': {
        'id': 'TechPowerUp.NVCleanstall',
        'name': 'NVIDIA driver installer',
    },
    'amd': {
        'id': 'AMD.AMDSoftwareCloudEdition',
        'name': 'AMD software package',
    },
    'intel': {
        'id': 'Intel.IntelDriverAndSupportAssistant',
        'name': 'Intel Driver & Support Assistant',
    },
}

LINUX_PACKAGE_COMMANDS = {
    'apt': {
        'nvidia': [
            ['sudo', 'apt', 'update'],
            ['sudo', 'ubuntu-drivers', 'autoinstall'],
        ],
        'amd': [
            ['sudo', 'apt', 'update'],
            ['sudo', 'apt', 'install', '-y', 'mesa-vulkan-drivers', 'mesa-va-drivers', 'mesa-vdpau-drivers'],
        ],
        'intel': [
            ['sudo', 'apt', 'update'],
            ['sudo', 'apt', 'install', '-y', 'mesa-vulkan-drivers', 'intel-media-va-driver', 'vainfo'],
        ],
    },
    'dnf': {
        'nvidia': [
            ['sudo', 'dnf', 'install', '-y', 'akmod-nvidia', 'xorg-x11-drv-nvidia-cuda'],
        ],
        'amd': [
            ['sudo', 'dnf', 'install', '-y', 'mesa-dri-drivers', 'mesa-vulkan-drivers', 'mesa-va-drivers'],
        ],
        'intel': [
            ['sudo', 'dnf', 'install', '-y', 'mesa-dri-drivers', 'mesa-vulkan-drivers', 'intel-media-driver'],
        ],
    },
    'pacman': {
        'nvidia': [
            ['sudo', 'pacman', '-S', '--needed', 'nvidia', 'nvidia-utils'],
        ],
        'amd': [
            ['sudo', 'pacman', '-S', '--needed', 'mesa', 'vulkan-radeon', 'libva-mesa-driver'],
        ],
        'intel': [
            ['sudo', 'pacman', '-S', '--needed', 'mesa', 'vulkan-intel', 'intel-media-driver'],
        ],
    },
}


def _normalize_gpu_vendor(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '', value.casefold())


def _run_command(command: list[str]) -> tuple[int, str]:
    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore',
        shell=False,
    )
    output = (process.stdout or '') + ('\n' + process.stderr if process.stderr else '')
    return process.returncode, output.strip()


def _get_windows_gpu_names() -> list[str]:
    commands = [
        ['powershell', '-NoProfile', '-Command', 'Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name'],
        ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
    ]

    for command in commands:
        return_code, output = _run_command(command)
        if return_code != 0 or not output:
            continue

        names = []
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.casefold() == 'name':
                continue
            if 'microsoft basic display adapter' in line.casefold():
                continue
            names.append(line)

        if names:
            return names

    return []


def _get_linux_gpu_descriptions() -> list[str]:
    commands = [
        ['lspci', '-nnk'],
        ['lshw', '-C', 'display'],
    ]

    for command in commands:
        if not shutil.which(command[0]):
            continue

        return_code, output = _run_command(command)
        if return_code != 0 or not output:
            continue

        lines = []
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lowered = line.casefold()
            if 'vga compatible controller' in lowered or '3d controller' in lowered or 'display controller' in lowered:
                lines.append(line)
            elif command[0] == 'lshw' and 'description:' in lowered:
                lines.append(line)

        if lines:
            return lines

    return []


def _detect_gpu_vendors(gpu_descriptions: list[str]) -> list[str]:
    vendors = []
    for description in gpu_descriptions:
        normalized = _normalize_gpu_vendor(description)
        vendor = ''
        if any(token in normalized for token in ('nvidia', 'geforce', 'quadro', 'rtx', 'gtx')):
            vendor = 'nvidia'
        elif any(token in normalized for token in ('advancedmicrodevices', 'amdradeon', 'amd', 'radeon', 'ati')):
            vendor = 'amd'
        elif 'intel' in normalized:
            vendor = 'intel'

        if vendor and vendor not in vendors:
            vendors.append(vendor)

    return vendors


def _install_windows_vendor(vendor: str) -> str:
    installer = WINDOWS_DRIVER_INSTALLERS[vendor]
    if not shutil.which('winget'):
        raise FileNotFoundError('winget was not found on this system.')

    command = [
        'winget', 'install', '--id', installer['id'], '-e',
        '--accept-source-agreements', '--accept-package-agreements',
    ]
    return_code, output = _run_command(command)
    if return_code != 0:
        raise RuntimeError(output or f'Failed to install {installer["name"]}.')

    return f'Installed {installer["name"]} for Windows ({installer["id"]}).'


def _linux_package_manager() -> str:
    for package_manager in ('apt', 'dnf', 'pacman'):
        if shutil.which(package_manager):
            return package_manager
    return ''


def _find_apt_nvidia_driver_package() -> str:
    if not shutil.which('apt-cache'):
        return ''

    return_code, output = _run_command(['apt-cache', 'search', '^nvidia-driver-[0-9]+$'])
    if return_code != 0 or not output:
        return ''

    candidates = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = re.match(r'^(nvidia-driver-(\d+))\s+-', line)
        if not match:
            continue
        candidates.append((int(match.group(2)), match.group(1)))

    if not candidates:
        return ''

    return sorted(candidates, key=lambda item: item[0], reverse=True)[0][1]


def _install_linux_vendor(package_manager: str, vendor: str) -> str:
    if package_manager == 'apt' and vendor == 'nvidia':
        if shutil.which('ubuntu-drivers'):
            commands = [['sudo', 'apt', 'update'], ['sudo', 'ubuntu-drivers', 'autoinstall']]
        else:
            driver_package = _find_apt_nvidia_driver_package()
            if not driver_package:
                raise RuntimeError('Could not find an NVIDIA driver package for apt.')
            commands = [['sudo', 'apt', 'update'], ['sudo', 'apt', 'install', '-y', driver_package, 'nvidia-settings']]
    else:
        commands = LINUX_PACKAGE_COMMANDS.get(package_manager, {}).get(vendor, [])

    if not commands:
        raise RuntimeError(f'No Linux installation commands configured for {vendor} on {package_manager}.')

    for command in commands:
        return_code, output = _run_command(command)
        if return_code != 0:
            raise RuntimeError(output or f'Failed to install {vendor} drivers with {package_manager}.')

    return f'Installed {vendor} drivers on Linux using {package_manager}.'


def video_drivers():
    current_system = system.nameSO()

    try:
        if current_system == 'Windows':
            gpu_descriptions = _get_windows_gpu_names()
            vendors = _detect_gpu_vendors(gpu_descriptions)
            if not vendors:
                message = 'No supported GPU vendor was detected on Windows.'
                log.log(message, level='WARNING')
                return message

            results = []
            for vendor in vendors:
                try:
                    result = _install_windows_vendor(vendor)
                    log.log(result, level='INFO')
                    results.append(result)
                except Exception as error:
                    log.log(f'Failed to install {vendor} video drivers on Windows: {error}', level='ERROR')
                    results.append(f'Failed to install {vendor} drivers: {error}')

            return '; '.join(results)

        if current_system == 'Linux':
            gpu_descriptions = _get_linux_gpu_descriptions()
            vendors = _detect_gpu_vendors(gpu_descriptions)
            if not vendors:
                message = 'No supported GPU vendor was detected on Linux.'
                log.log(message, level='WARNING')
                return message

            package_manager = _linux_package_manager()
            if not package_manager:
                message = 'No supported Linux package manager was found.'
                log.log(message, level='ERROR')
                return message

            results = []
            for vendor in vendors:
                try:
                    result = _install_linux_vendor(package_manager, vendor)
                    log.log(result, level='INFO')
                    results.append(result)
                except Exception as error:
                    log.log(f'Failed to install {vendor} video drivers on Linux: {error}', level='ERROR')
                    results.append(f'Failed to install {vendor} drivers: {error}')

            return '; '.join(results)

        message = f'Video driver installation is not supported on {current_system}.'
        log.log(message, level='WARNING')
        return message
    except Exception as error:
        message = f'Failed to install video drivers: {error}'
        log.log(message, level='ERROR')
        return message