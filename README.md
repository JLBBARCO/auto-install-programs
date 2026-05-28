# Programs Manager

Programs Manager is a cross-platform installer/uninstaller and startup manager. The Windows build includes installer categories and additional custom actions such as startup management and system personalization.

## Contents

- [Program](#program)
  - [Frontend](#frontend-program)
  - [Backend](#backend-program)
- [Website](#website)
  - [Frontend](#frontend-site)
  - [Backend](#backend-site)
- [GitHub Actions](#github-actions)
- [GitHub RAW](#github-raw)
  - [Run](#run)

## System icon

![System icon](src/assets/icon/icon.ico)

## Program

This is a program manager for easy installation or removal of software when preparing a machine, reconfiguring it, or performing an optimization.

### Frontend (Program)

#### UI language

English (En-US)

#### First screen

- The title is dynamic and reflects the detected operating system.
- A container shows each function category as a checklist.
- Bottom-left: a button to select or deselect all checkboxes in the main container.
- Bottom-right: a "Next" button that closes the first screen and opens the second screen, passing an array containing only the selected options.

#### Second screen

##### Main container

When the second screen opens, it displays the `data` array from each JSON object present in the `json_data` array and shows those entries in the main container.

##### Dropdown menu (tabs)

Each tab corresponds to the `name` field of a JSON object loaded by the JSON reader; selecting a tab shows that JSON's entries in alphabetical order in the content container.

##### Content

The content panel displays a checklist for the selected JSON with these columns:

- First column: checkbox
- Second column: function name
- Third column: function type (`install`, `uninstall`, or `function`)

##### Button container

Bottom-left contains two buttons:

- `Add Program`: opens a search dialog (screen 3.1) with:
  - a search input and a Search button at the top;
  - when the user searches, the backend queries the package manager and returns matching programs;
  - the results are shown in three columns: an action button (toggles Add/Remove), program name, and program id.
- `Remove Programs`: opens a removal dialog (screen 3.2) with a similar layout to 3.1.

##### Run button

Bottom-right has a `RUN` button that closes the UI and starts the main background process.

### Backend (Program)

#### JSON

##### Writing JSON

When the program writes JSON, it checks for `user.json` in `C:\Users\<user>\Downloads\Programs Manager`. If the file does not exist, it is created with the following structure:

```json
{
  "name": "User",
  "description": "User data generated after execution of write system",
  "data": []
}
```

##### Reading JSON

###### Internal JSON

Internal JSON reading behaves like the write flow, except it only reads the file and places the result into the `json_data` array.

###### External JSON

External JSON is fetched from GitHub RAW using the URL:
`https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/program/system/<operating_system>/json/<file_name>.json` and each JSON payload is added to `json_data`.

#### Logging (`log.log`)

Log messages use three severity tags:

- `[INFO]`
- `[WARNING]`
- `[ERROR]`

`[INFO]` indicates normal progress (examples: `Start system`, `Find and read essentials.json`, `End system`).
`[WARNING]` denotes partial or recoverable problems (examples: `Find and not read essentials.json`, `Visual Studio Code updated`).
`[ERROR]` is used for fatal failures (examples: `Not found essentials.json`, `Visual Studio Code not installed and not updated`).

#### Add Program (screen 2)

When the user clicks `Add Program`, the search UI queries the system package manager (e.g., WinGet on Windows). Selected items are saved into `user.json` appended to the `data` array as:

```json
{
  "name": "<program_name>",
  "type": "install",
  "checkbox": true,
  "id": "<program_id>"
}
```

#### Remove Program (screen 2)

When the user clicks `Remove Programs`, the UI lists installed packages and selected items are saved into `user.json` as:

```json
{
  "name": "<program_name>",
  "type": "uninstall",
  "checkbox": true,
  "id": "<program_id>"
}
```

Those entries are intended for package-manager commands such as `winget uninstall -id <program_id>`.

#### Default terminal flags

- Windows: WinGet commands should include `--accept-source-agreements --accept-package-agreements >nul 2>&1` to suppress progress and accept agreements.
- Linux/macOS: shell commands should redirect output to `/dev/null` with `> /dev/null 2>&1` when appropriate.
- PowerShell runs should redirect to `$null` when needed (e.g. `*> $null`).

#### Background execution

When the user presses `RUN`, all windows close and the program continues running in the background. It writes `[dd/mm/yyyy hh:mm:ss] [INFO] Start system` to `log.log`, exposes `log.log` via an HTTP endpoint on a dynamically chosen `localhost` port in the range `9900–9999` (the program will bind a free `99xx` port), and opens the Programs Manager website including the selected port as a query parameter (for example: `https://programs-manager-website.vercel.app?port=9936`).

Startup tasks are executed in this order:

- Update the package manager (example: Microsoft.AppInstaller on Windows)
- Read internal JSON and store it into `json_data`
- Fetch external JSON and append it to `json_data`
- For each JSON read, log success or failure:
  - Success:

    ```log
    [dd/mm/yyyy hh:mm:ss] [INFO] Read <file_name> successfully
    ```

  - Failure:

    ```log
    [dd/mm/yyyy hh:mm:ss] [ERROR] Read <file_name> with error <error>
    ```

- Process the `json_data` array and separate entries by type: `install`, `uninstall`, and `function`.
- Execute actions in this order:
  1. Uninstall packages listed in `uninstall` (e.g. `winget uninstall -id <program_id>`)
  2. Run `function` entries (execute configured functions)
  3. Install packages listed in `install`

## Website

The website displays the `log.log` output in real time while the program runs. The UI groups log lines by severity (`INFO`, `WARNING`, `ERROR`) and shows recent entries first, with automatic scrolling unless the user scrolls up.

### Frontend (Site)

#### Language

English (En-US)

#### Main view

- Three containers display `INFO`, `WARNING`, and `ERROR` messages.
- Each container has a fixed height and horizontal scrollbar. Older messages appear above newer messages.
- Incoming log lines follow these formats:

  ```log
  [dd/mm/yyyy hh:mm:ss] [INFO] <message>
  [dd/mm/yyyy hh:mm:ss] [WARNING] <message>
  [dd/mm/yyyy hh:mm:ss] [ERROR] <message>
  ```

- Example input line: `[01/06/2026 12:30:45] [SUCCESS] Visual Studio Code installed` is displayed as `01/06/2026 12:30:45 | Visual Studio installed` with the timestamp colored `#808080`.
- The site partitions historical runs: entries older than 1 minute compared to the site's load timestamp are shown in a separate history section.

#### Footer — Contact container

Contact cards are loaded from a remote JSON and displayed as circular icon buttons. Hovering shows the contact `name`. The JSON `url` becomes the card link and `iconName` indicates the icon to display.

CSS layout example:

```css
display: flex;
flex-flow: row wrap;
justify-content: space-between;
align-items: center;
```

#### Error page

If the site cannot access the `log.log` port (the port provided in the page query parameter `?port=NNNN` or any `99xx` port) or the file is not shared, an error page is shown with a refresh button and a link to the GitHub repository: `https://github.com/JLBBARCO/programs-manager`.

### Backend (Site)

The site temporarily records the page load time and uses it to partition current-run logs from historical logs. Monitoring stops when the latest log line contains `[INFO] End system`.

#### Port probe

On load the site probes the port specified by the query parameter `?port=NNNN` (if present) or falls back to a sensible default in the `99xx` range for up to 30 seconds. If the log endpoint is not available, monitoring is paused until the user refreshes.

#### Contacts source

Contact data is fetched from:

`https://raw.githubusercontent.com/JLBBARCO/portfolio/main/src/json/areas/contact.json` and cached by Vercel hourly to minimize GitHub requests.

## GitHub Actions

GitHub Actions should build the program for each OS when the branch is `main` or `develop`.

Use `build.bat`, `build.sh`, and `build-mac.sh` to produce OS-specific builds, package them (e.g. zip), and attach them to a GitHub Release. Rules:

- `main` branch builds are published as the Last Release
- `beta` branch builds are published as Pre-release

The `system` folder is not included in the build artifacts because those files are fetched at runtime via GitHub RAW.

Actions should also capture screenshots for each OS as WEBP and replace these files in the repository:

![Print MacOS](src/assets/img/macos.webp)
![Print Linux](src/assets/img/linux.webp)
![Print Windows](src/assets/img/windows.webp)

An aggregated thumbnail combining the three screenshots will replace:
![Print from all system prints compiled](src/assets/img/thumbnail.webp)

## GitHub RAW

### Run

Use `./run.ps1` and `./run.sh` to download and run the appropriate build for Windows, Linux, or macOS directly from the Last Release.

Examples:

Windows (PowerShell):

```powershell
irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
```

Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```

macOS:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```

Optional branch override (useful for testing, e.g. `develop`):

PowerShell:

```powershell
$env:AIP_BRANCH='develop'; irm https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.ps1 | iex
```

Bash:

```bash
AIP_BRANCH=develop curl -fsSL https://raw.githubusercontent.com/JLBBARCO/programs-manager/main/run.sh | bash
```
