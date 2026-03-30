# Auto Installation Programs

Windows now runs only as a startup manager. It no longer installs programs or changes theme, power, mouse, or Explorer settings.

## Interface

![UI](src/assets/img/thumbnail.webp)

## Packaging

The project is built with PyInstaller using `build.bat`. Only the `src` package
is bundled into the executable.

The only local data written at runtime is:

- `programs.log` — startup-key dump written by the startup manager actions.

## One-Line Run (No Manual Download)

Use these commands to run directly from terminal without downloading the repository manually.
The script will fetch/update source code in a local cache and launch the app.

- Windows PowerShell:

  ```powershell
  irm https://raw.githubusercontent.com/JLBBARCO/auto-programs/main/run.ps1 | iex
  ```

- Linux:

  ```bash
  curl -fsSL https://raw.githubusercontent.com/JLBBARCO/auto-programs/main/run.sh | bash
  ```

- macOS:

  ```bash
  curl -fsSL https://raw.githubusercontent.com/JLBBARCO/auto-programs/main/run.sh | bash
  ```

Optional branch override (for testing `develop`):

```powershell
$env:AIP_BRANCH='develop'; irm https://raw.githubusercontent.com/JLBBARCO/auto-programs/main/run.ps1 | iex
```

```bash
AIP_BRANCH=develop curl -fsSL https://raw.githubusercontent.com/JLBBARCO/auto-programs/main/run.sh | bash
```

## Current Scope

The current Windows startup flow exposes two actions:

- Disable startup entries that are not listed in the repository whitelist.
- Re-enable startup entries listed in the repository whitelist.

Startup resources are downloaded from the repository at runtime, including category JSON files, the startup whitelist, and the Office deployment files.

### [MacOS](MacOS.md)

### [Linux](Linux.md)

### [Windows](Windows.md)
