# Auto Installation Programs

Windows now runs only as a startup manager. It no longer installs programs or changes theme, power, mouse, or Explorer settings.

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

### [MacOS](MacOS.md)

### [Linux](Linux.md)

### [Windows](Windows.md)
