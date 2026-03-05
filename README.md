# Auto Installation Programs

Auto installation programs for windows

## Interface

![UI](src/assets/img/thumbnail.webp)

## Packaging

The project is built with PyInstaller using `build.bat`. All files under
`install/` and the `src` package are bundled into the executable. When the
application is run from the compiled directory the code uses a helper named
`_resource_path` to locate data files inside the bundle (`sys._MEIPASS`).

Logs (`log.log` and `programs.log`) are written next to the executable rather
than the current working directory, avoiding mysterious “path not found”
errors which were previously seen during installations.
