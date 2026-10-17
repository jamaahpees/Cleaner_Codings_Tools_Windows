# Technical Stack — Dev & AI Cleaner

**Snapshot date:** 2026-10-17
**Primary entry point:** `dev_cleaner.py`

## Runtime and application structure

- **Language/runtime:** Python; the code uses modern standard-library APIs and the project launcher recommends Python 3.10+.
- **Desktop UI:** CustomTkinter (`customtkinter`) with Tkinter/ttk components. The application creates a `DevAICleanerApp` window and runs the Tk event loop.
- **Application shape:** Single main Python module with helper functions and a `DevAICleanerApp` class. Feature areas are organized as views in a left-navigation desktop layout.
- **Concurrency:** `concurrent.futures.ThreadPoolExecutor` and threading-related standard-library facilities support long-running tasks. UI callbacks are scheduled through Tk's `after(...)` mechanism.
- **Appearance:** CustomTkinter dark appearance mode and its built-in blue theme are selected in source.

## Dependencies

### Runtime dependencies identified in source/build configuration

| Package/module | Purpose |
|---|---|
| `customtkinter` | Main themed desktop widgets |
| `psutil` | Disk, process, and system information |
| `send2trash` | Send supported files/folders to the Recycle Bin |
| `darkdetect` | CustomTkinter appearance/platform support; collected by the PyInstaller spec |
| `pywin32` modules (`win32api`, `win32con`, `win32process`, `win32gui`) | Explicit PyInstaller hidden imports for Windows integration |

The source also uses Python standard-library modules including `tkinter`, `winreg`, `subprocess`, `concurrent.futures`, `importlib.metadata`, `pathlib`, `urllib`, `ssl`, `json`, and filesystem/process APIs. `winreg` and several invoked commands make the application Windows-specific.

> Dependency lists should be reconciled with a future pinned requirements/lock file. The repository baseline currently has no authoritative dependency lock file; versions are therefore not specified here.

## Windows integrations

- **Registry:** `winreg` reads application uninstall entries, Python environment registrations, registry orphans, startup and service-related configuration; cleanup paths can modify registry keys.
- **Filesystems:** Python `os`, `pathlib`, `shutil`; NTFS junction detection uses file attributes; Recycle Bin operations use `send2trash`.
- **Processes:** `psutil` inspects/stops processes in application folders. `subprocess` invokes tools including Robocopy, `cmd.exe`/`mklink`, pip in selected Python environments, and Windows system commands.
- **System status:** `psutil` queries disk partitions and free space.
- **External access:** `urllib`/`webbrowser` support URL/download and toolbox-related flows in the source.
- **Privilege:** `ctypes` checks Windows administrator status for operations that require elevation.

## Packaging and launch

- **Builder:** PyInstaller, configured by `Dev-AI-Cleaner.spec`.
- **Executable mode:** The spec sets `console=False`, producing a GUI/windowed executable rather than a console-subsystem application.
- **Collected assets/imports:** The spec uses PyInstaller `collect_all` for `customtkinter` and `darkdetect`, and declares Windows-related hidden imports.
- **Build command:** `pyinstaller --clean --noconfirm Dev-AI-Cleaner.spec`.
- **Output:** PyInstaller writes generated artifacts into `build/` and `dist/`; these are ignored and must not be committed.
- **Source launcher:** `Run-Dev-Cleaner.bat` checks Python, installs `customtkinter` and `send2trash` using pip, then starts `dev_cleaner.py` with `pythonw`. Note that the launcher does not currently install every package imported by source (notably `psutil`) and installs unpinned dependencies; treat it as a development convenience, not a reproducible installer.

## Local persistence and logging

The source stores operational state under `%LOCALAPPDATA%\DevAICleaner`, including App Mover history, registry backup files, and Python package diagnostics. It may also read a legacy move-history file at `C:\ProgramData\WinUP\AppMover\moves.json`. These files are per-machine/user state and must not be added to version control.

## Build prerequisites and reproducibility gaps

A reproducible developer setup should use a virtual environment and install the documented runtime packages plus PyInstaller. The project does not currently provide a pinned requirements file, test/development dependency group, CI build workflow, or signed release process. Build output and executable behavior should be validated on Windows because registry, junction, system command, and GUI behavior cannot be fully validated on other platforms.

## Planned engineering improvements

These are roadmap items, not current guarantees:

- Add an optional one-shot startup Smart Scan preference using existing worker/scan flow.
- Apply success-only in-place UI mutation and remove automatic rescans after selected operations.
- Verify Python package removal with the same selected interpreter.
- Consistently suppress child-process terminal windows while preserving output and exit codes.
- Improve packaging/dependency declarations and smoke-test the packaged GUI.
- Refresh the desktop UI within CustomTkinter, avoiding a WebView/browser runtime unless separately justified.
