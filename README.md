# Programs Manager

Programs Manager is a cross-platform installer and startup manager. The Windows build includes installer categories plus custom actions such as startup management and system customization.

## More information

- [macOS](#macos)
- [Linux](#linux)
- [Windows](#windows)

## Interface

![UI](src/assets/img/thumbnail.webp)

## Packaging

The project is packaged with PyInstaller using `build.bat` on Windows, `build.sh` on Linux, and `build-mac.sh` on macOS. Both `src` and `install` are bundled into the executable so runtime configuration and Windows assets remain available.

Runtime data written locally:

- `programs.log` — registry startup dump produced by the startup manager actions.
- `log.log` — shared runtime log exposed to the background log bridge.

## One-line run (no manual download)

Run directly from the terminal without cloning the repository. The script fetches/updates source code into a local cache and launches the app.

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
```

Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```

MacOS:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```

Optional branch override (useful for testing `beta`):

```powershell
$env:AIP_BRANCH='beta'; irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
```

```bash
AIP_BRANCH=beta curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```

## Current scope

The Windows flow currently exposes these actions:

- Disable startup entries that are not listed in the repository whitelist.
- Re-enable startup entries listed in the repository whitelist.
- Install categories from the Windows JSON files, including custom `function` entries.
- Apply the Vision Cursor Black fallback from `install/windows/vision-cursor-black` when the function is selected.
- Run uninstall selections before install selections in the same execution flow.
- Support Windows category entries that use either `id` or `function`, including `ti_tools.json`.

Startup resources (category JSON files, whitelist, Office deployment files) are downloaded from the repository at runtime when needed.

## Configuration (JSON schema)

Category files in `install/windows/*.json` follow a simple schema. Each file contains a top-level `programs` array with entries that use one of two keys to define an action:

- `id` — package identifier used by the system package manager (e.g., `winget`, `brew`, `apt`). When present, the installer uses the package manager to install the program.
- `function` — a repository-defined custom action. The installer dispatches these to internal handlers instead of a package manager.

Example entries:

```json
{ "name": "Rufus", "id": "Rufus.Rufus" }
{ "name": "Dark Mode", "function": "dark-mode" }
{ "name": "BIOS", "function": "path-to-bios" }
```

Behavior notes:

- If an entry provides both `id` and `function`, `function` will take precedence and the custom handler will run.
- Supported built-in `function` keys include `dark-mode`, `path-to-bios`, and `vision-cursor`. Custom handlers are implemented in `lib.install._run_custom_function` and `lib.customizations`.
- The GUI and `install` module accept either store `id` values or `function` keys and will present entries accordingly.

## Build and CI

The main build workflow runs on Python 3.12 and is configured for the `main` and `beta` branches. It triggers when Python files, install data, workflow files, the README, `requirements.txt`, or platform build scripts change. Pushes to `beta` publish GitHub pre-releases; pushes to `main` publish regular releases.

The macOS installer workflow uses Python 3.12 and creates a package with `pkgbuild` after the app bundle is produced.

On each successful platform build, the CI workflow launches the compiled app, captures a screenshot for Windows, Linux, and macOS, updates `src/assets/img/windows.webp`, `src/assets/img/linux.webp`, `src/assets/img/macos.webp`, and rebuilds `src/assets/img/thumbnail.webp` from those three images.

## macOS

The macOS section is organized around these areas:

- [Developer Tools](#developer-tools)
- [Essential Programs](#essential-programs)
- [Screen](#screen)

![macOS screenshot](src/assets/img/macos.webp)

### Essential programs

- Adobe Acrobat
- Cloudflare Warp
- Free Download Manager
- Google Chrome
- Google Drive
- Mozilla Firefox
- Spotify
- Telegram
- The Unarchiver
- VLC
- WhatsApp

### Screen

- AnyDesk

### Developer Tools

- Blender
- Docker
- Figma
- GIMP
- GitHub
- Microsoft Teams
- MySQL Workbench
- VirtualBox
- Visual Studio Code
- XAMPP

## Linux

The Linux section is organized around these areas:

- [Developer Tools](#developer-tools)
- [Drivers](#drivers)
- [Essential Programs](#essential-programs-1)
- [Server Tools](#server-tools)
- [Screen](#screen-1)

![Linux screenshot](src/assets/img/linux.webp)

### Drivers

The system analyzes the graphics card and installs the appropriate drivers.

- AMD
- Intel
- NVIDIA

### Essential programs

- Curl
- Free Download Manager
- Git
- Google Chrome
- Mozilla Firefox
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
- Blender
- Docker
- GIMP
- Git
- Node.js
- Python 3
- VirtualBox
- Visual Studio Code

### Server Tools

- Curl & Wget
- Git
- htop
- net-tools
- SSH server
- Vim

## Windows

The Windows app combines startup management, install categories, and system customization.

The Linux section is organized around these areas:

- [Behavior](#behavior)
- [Installations and Modifications](#installations-and-modifications)
- [Safety](#safety)
- [Whitelist](#whitelist)

![Windows screenshot](src/assets/img/windows.webp)

### Behavior

- Disable startup entries that are not on the repository whitelist.
- Re-enable startup entries that are on the repository whitelist.
- Save the current registry startup dump to `programs.log` after each action.
- Run uninstall selections before install selections when both are chosen.
- Support JSON entries that use either `id` or `function`.
- Open the shared log bridge for the runtime site when the app starts a run session.

### Safety

- The whitelist is downloaded from the repository and cached locally at runtime.
- Matching is normalized and exact; broad substring matches were removed to avoid false positives.
- Theme, mouse precision, power plan, Explorer restarts, and other deprecated Windows-only actions are kept isolated behind explicit functions.

### Whitelist

Allowed startup keys are defined in `install/windows/white_list.txt` in the repository.

Use `install/windows/list_startup_programs.py` to inspect the registry names present on your machine and adjust the whitelist if needed.

### Installations and Modifications

- [Customization](#customization)
- [Development](#development)
- [Drivers](#drivers-1)
- [Essential Programs](#essential-programs-2)
- [Games](#games)
- [Screen](#screen-2)
- [Customization](#customization)
- [TI Tools](#ti-tools)

#### Customization

- Dark Mode (Enable dark mode)
- Essential Programs Initialization (Disable all programs and re-enable only essential programs on initialization to Windows)
- Lively Wallpaper
- Microsoft PowerToys
- Rainmeter
- Seelen UI
- TranslucentTB
- Vision Cursor (Alter cursor to Vision Cursor)

#### Development

- Blender
- Docker
- Figma
- GIMP
- Git
- Github Desktop
- Java Runtime Environment
- Microsoft PowerShell
- Microsoft Teams
- MySQL
- Node.JS
- Postman
- Python 3.12
- Python Install Manager
- VirtualBox
- Visual Studio Code
- XAMPP

#### Drivers

The system analyzes the graphics card and installs the appropriate drivers.

- AMD
- Intel
- NVIDIA

#### Essential Programs

- Adobe Acrobat
- Camo Studio
- Cloudflare Warp
- Free Download Manager
- Google Chrome
- Google Drive
- Microsoft Office
- Mozilla Firefox
- Notion
- Obsidian
- Spotify
- Tor Browser
- VLC
- WinRAR

#### Games

- CurseForge
- Discord
- Epic Games Launcher
- Google Play Games
- Radmin VPN
- Steam
- Xbox App

#### Screen

- AnyDesk
- Spacedesk Client
- Spacedesk Server

#### TI Tools

- Bios Shortcut
- EaseUS DiskCopy
- EaseUS Todo Backup
- Rufus
- Ventoy
