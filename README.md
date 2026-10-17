# Dev & AI Cleaner

A Windows desktop utility built with Python and CustomTkinter for reviewing and managing selected cleanup, application, Python-package, startup/service, duplicate-file, and Windows-toolbox tasks. The main entry point is `dev_cleaner.py`.

> **Use with care.** Cleaning, uninstalling, moving applications, changing Windows settings, and running system utilities can affect the operating system and user data. Review selections and confirmation dialogs before proceeding. Keep backups of important data.

## Current capabilities

The current application source provides these sections:

- **Smart Cleaner** — scans configured browser, temporary, developer-cache/project, and selected registry-orphan categories; presents findings before cleanup.
- **App Mover & Restore** — identifies candidate application folders, checks safety rules, and can move eligible folders to another drive using Robocopy and NTFS directory junctions. A local move history supports restore.
- **Python Library Manager** — discovers Python environments and lists installed packages; protects selected core packages from uninstall selection.
- **Startup & Windows Services** — displays startup entries and Windows services for management.
- **Duplicate File Finder** — scans a selected location and offers duplicate-file handling.
- **Ghost Toolbox** — includes links and Windows utility/tweak actions.

Feature details vary by Windows version, permissions, available system tools, and selected environment. This repository is an early-stage utility; inspect the source and test carefully before using operations that modify the system.

## Requirements

- Windows 10/11 (Windows-specific registry, junction, service, and system-tool integrations are used).
- Python 3.10 or later for source execution (the provided launcher also checks for Python; PyInstaller builds may run without a separate Python installation).
- Runtime Python packages: `customtkinter`, `psutil`, and `send2trash`.
- Optional system tools used by individual actions may include `robocopy`, `cmd.exe`, `mklink`, `winget`, `sc.exe`, `powercfg`, `dism`, and `sfc`.
- Administrator privileges are required for some system-level actions, including App Mover operations.

## Run from source

Create and activate a virtual environment, then install the runtime dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install customtkinter psutil send2trash pyinstaller
python dev_cleaner.py
```

The `Run-Dev-Cleaner.bat` launcher is also provided. Review it before use: it installs some dependencies with pip and starts the GUI using `pythonw`.

## Build a Windows executable

With the dependencies installed, build from the project directory:

```powershell
pyinstaller --clean --noconfirm Dev-AI-Cleaner.spec
```

The PyInstaller specification is configured for a windowed application (`console=False`). Build output is generated under `build/` and `dist/`; these directories are intentionally excluded from version control.

## Local data

The application stores App Mover history, registry backups, and Python Library Manager diagnostics under `%LOCALAPPDATA%\DevAICleaner`. It may also read the legacy `C:\ProgramData\WinUP\AppMover\moves.json` history file if present. Do not commit these local files.

## Safety and privacy notes

- The application is a local desktop utility; this project documentation does not guarantee the behavior or safety of downloaded tools linked by the toolbox.
- Avoid running unknown installers or commands. Verify sources independently.
- Review the selected rows and target paths before cleanup or move/restore operations.
- Registry changes and system cleanup can have lasting effects; maintain backups and use a non-production/test environment where possible.
- Some operations may require elevated privileges. Grant them only when necessary and when you understand the operation.

## Roadmap

Planned work, not yet represented as completed functionality, includes optional one-shot Smart Scan on startup, success-only in-place UI updates without action-triggered rescans, broader terminal-window suppression for child processes, packaging cleanup, and a lightweight CustomTkinter visual refresh. See [PRD](docs/PRD.md) and [Tech Stack](docs/TECH_STACK.md).

## Project documents

- [Product Requirements Document](docs/PRD.md)
- [Technical Stack](docs/TECH_STACK.md)
- [No-rescan and App Mover design note](docs/plans/2026-10-17-no-rescan-and-app-mover-design.md)
