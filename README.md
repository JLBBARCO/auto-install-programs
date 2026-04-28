# Auto Installation Programs

Windows now runs only as a startup manager. It no longer installs programs or changes theme, power, mouse, or Explorer settings.

## More individual informations:

- [MacOS](#macos)
- [Linux](#linux)
- [Windows](#windows)

## Interface

![UI](src/assets/img/thumbnail.webp)

## Packaging

The project is built with PyInstaller using `build.bat`. Only the `src` package
is bundled into the executable.

The only local data written at runtime is:

- `programs.log` — startup-key dump written by the startup manager actions.

## Current Scope

The current Windows startup flow exposes two actions:

- Disable startup entries that are not listed in the repository whitelist.
- Re-enable startup entries listed in the repository whitelist.

Startup resources are downloaded from the repository at runtime, including category JSON files, the startup whitelist, and the Office deployment files.

## MacOS

This system install programs with basis in this topics:

- [Developer Tools](#developer-tools)
- [Essential Programs](#essential-programs)
- [Screen](#screen)

![MacOS print program](src/assets/img/macos.webp)

### Essential programs

- Adobe Acrobat
- Cloudflare Warp
- Free Download Manager
- Google Chrome
- Google Drive
- Mozilla FireFox
- Spotify
- Telegram
- The Unarchiver
- VLC
- WhatsApp

### Screen

- AnyDesk

### Developer Tools

- Arduino IDE
- Blender
- Docker
- Figma
- GIMP
- Github
- Microsoft Teams
- MySQL Workbench
- VirtualBox
- Visual Studio Code
- XAMPP

## Linux

This system install programs with basis in this topics:

- [Developer Tools](#developer-tools)
- [Drivers](#drivers)
- [Essential Programs](#essencial-programs)
- [Server Tools](#server-tools)
- [Screen](#screen)

![Linux print program](src/assets/img/linux.webp)

### Drivers

The system analyzes the video card and installs the necessary drivers.

- AMD
- Intel
- NVIDIA

### Essencial Programs

- Curl
- Free Download Manager
- Git
- Google Chrome
- Mozilla FireFox
- Spotify
- Telegram
- VLC
- WhatsApp

### Screen

- AnyDesk
- Git
- VNC Server

### Developer Tools

- Arduino IDE
- Blander
- Docker
- Gimp
- Git
- Node.js
- Python 3
- VirtualBox
- Visual Studio Code

### Server Tools

- Curl & Wget
- Git
- HTOP
- Net-Tools
- SSH Server
- Vim

## Windows

The current Windows app is restricted to startup management.

![Windows print program](src/assets/img/windows.webp)

### Behavior

- Disable startup entries that are not on the repository whitelist.
- Re-enable startup entries that are on the repository whitelist.
- Save the current registry startup dump to `programs.log` after each action.

### Safety Changes

- The whitelist is downloaded from the repository and cached locally at runtime.
- Matching is normalized and exact; broad substring matches were removed.
- Theme, mouse precision, power plan, Explorer restarts, and installer execution were removed from the Windows flow.

### Whitelist

Allowed startup keys are defined in `install/windows/white_list.txt` in the repository.

Use `install/windows/list_startup_programs.py` to inspect the registry names present on your machine and adjust the whitelist if needed.
