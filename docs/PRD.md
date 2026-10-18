# Product Requirements Document — Dev & AI Cleaner

**Status:** Baseline product description and roadmap
**Date:** 2026-10-17
**Product type:** Windows desktop utility

## 1. Product summary

Dev & AI Cleaner is a local Windows desktop application that brings together selected cleanup, application-folder moving/restoring, Python package inspection, startup/service management, duplicate-file handling, and Windows utility actions. It uses a graphical interface so users can inspect candidate items and choose actions rather than relying solely on command-line workflows.

This document describes the implementation present in the repository at baseline and separates future improvements into the roadmap. It is not a guarantee that every operation is available or safe on every Windows installation.

## 2. Problem and opportunity

Windows users and developers accumulate temporary files, caches, project environments, duplicate files, installed packages, startup entries, and system tools across different locations. Managing these through separate utilities is fragmented. A unified interface can make discovery and selected maintenance more approachable, provided it clearly communicates scope, status, and consequences.

## 3. Goals

1. Provide a single desktop interface for the supported cleanup and system-management areas.
2. Let users inspect results and select items before destructive or state-changing actions.
3. Protect known critical application folders/packages through safeguards and confirmation steps.
4. Support recovery-oriented flows where feasible, including Recycle Bin handling, registry backups, and App Mover history.
5. Keep the application usable on Windows without requiring a browser-based UI runtime.

## 4. Non-goals

- Replacing Windows security, backup, package-management, or enterprise device-management products.
- Automatically deleting or uninstalling items without user selection/confirmation.
- Guaranteeing that every third-party installer or toolbox link is safe.
- Supporting non-Windows systems; the current implementation relies on Windows-specific APIs and commands.
- Claiming that planned behavior (startup scan preference, universal no-rescan behavior, or redesigned UI) is already implemented.

## 5. Users and primary use cases

### Users
- Windows developers who want to inspect development caches and project-generated directories.
- Advanced desktop users who need a consolidated view of selected maintenance actions.
- Users with multiple Python installations who need to inspect packages in a selected environment.

### Use cases
1. Select Smart Cleaner categories, run a scan, review findings, choose items, and confirm cleanup.
2. Scan eligible application folders, review the safety status and destination, then move selected folders and restore them later from history.
3. Choose a Python interpreter/environment, inspect installed distributions, and select non-protected packages for uninstall.
4. Review startup entries and Windows services before applying supported management actions.
5. Scan a user-selected location for duplicates and select files for cleanup.
6. Open or run available Windows utilities from the toolbox area.

## 6. Functional requirements

### 6.1 Smart Cleaner (implemented)
- Present user-selectable scan categories in the interface.
- Search supported browser/temp/developer/project and registry-orphan locations based on enabled categories.
- Display findings and associated location/size/status information.
- Require explicit selection and confirmation before cleanup.
- Optional startup Smart Scan: Configurable via checkbox, default OFF, saved to `%LOCALAPPDATA%\DevAICleaner\preferences.json`, executed once upon app launch following checked categories.
- Success-only mutation: Remove only verified cleaned items from UI state; failed/unverified items are retained and reported with diagnostic feedback. No action-triggered automatic rescans.
- Use the Recycle Bin for supported project-folder removal and create real `reg.exe export` registry backup files before registry cleanup.

### 6.2 App Mover & Restore (implemented)
- Standalone implementation within Cleaner without external WinUP runtime dependencies.
- Enumerate application candidates from Windows uninstall registry locations and determine candidate install folders.
- Apply path/name safety filters and display eligibility status.
- Allow choosing a destination outside the system drive and check available space when possible.
- Atomic move history persistence (`moves.json`), durable recovery phases (`restored_pending_cleanup`), and explicit retry for pending target cleanups without recopying or automatic rescans.
- Application-wide mutation guard: Prevents concurrent scans and mutations across all views.
- Copy using Robocopy and create an NTFS directory junction for selected eligible folders.
- Persist move history locally and offer a restore action.
- Report copy, junction, and restore failures without presenting them as successful operations.

### 6.3 Python Library Manager (implemented baseline)
- Discover Python environments and allow choosing an environment.
- Enumerate installed packages and show versions, approximate sizes, and dependency information where available.
- Prevent selected core packages from being selected for uninstall.
- Require confirmation before invoking pip uninstall.

### 6.4 Startup and services (implemented baseline)
- Present startup entries and Windows services through the corresponding view.
- Provide supported management actions with appropriate feedback and privilege/error handling.

### 6.5 Duplicate File Finder (implemented baseline)
- Allow scanning a selected target location and presenting duplicate candidates.
- Require explicit selection and confirmation for cleanup actions.

### 6.6 Toolbox (implemented baseline)
- Present Windows utility/tweak actions and links available in the current source.
- Clearly report action failures; users remain responsible for validating third-party downloads and commands.

## 7. Non-functional requirements

- **Platform:** Windows 10/11 is the target; current source imports `winreg` and uses Windows-specific commands/APIs.
- **Usability:** destructive or system-changing actions require clear selection and confirmation; errors should identify the failed operation.
- **Responsiveness:** long-running scans/operations should use worker execution and marshal GUI updates to the Tk event loop.
- **Resource use:** avoid unnecessary resident services/background polling. Startup scanning is planned as opt-in and one-shot; it is not part of the current baseline.
- **Privacy:** local history, backups, and diagnostic logs remain on the user's machine; they should not be committed or uploaded.
- **Packaging:** provide a windowed executable build via PyInstaller; build output is generated and excluded from source control.
- **Reliability:** only confirmed successful operations should be represented as completed. This is a roadmap requirement where current code does not yet satisfy it consistently.

## 8. Safety, privacy, and permissions

- The application can delete files, uninstall packages, alter registry entries, manage services, move application folders, and run system commands. These actions can cause data loss or system instability.
- Users must review target paths and selections, preserve backups, and use elevated privileges only when required.
- App Mover history, registry backups, and Python diagnostics are stored under `%LOCALAPPDATA%\DevAICleaner`; a legacy move history may be read from `C:\ProgramData\WinUP\AppMover\moves.json`.
- No telemetry or remote account service is declared by the current source. Toolbox actions may access external URLs or download third-party software; those external interactions are distinct from core local scanning and should be evaluated independently.
- Secrets, local histories, generated catalogs, installer binaries, and test downloads must not be included in the public source baseline. The repository is intended to remain private as requested.

## 9. Acceptance criteria for the current baseline

- The application launches as a CustomTkinter desktop GUI on a supported Windows environment with required packages installed.
- Each documented capability is present in the source or explicitly identified as roadmap.
- Destructive flows expose selection/confirmation before action where implemented.
- The PyInstaller spec builds a windowed executable when dependencies and the build environment are available.
- README and technical documentation describe actual source/build behavior and do not claim unimplemented roadmap items as complete.
- Repository baseline contains curated source and documentation only, not generated installers/build outputs/local user data.

## 10. Roadmap (not yet delivered)

1. **Startup Smart Scan preference:** optional, default off, persisted locally; when enabled, run exactly once at application startup using the existing worker and currently checked categories, with no resident service or polling.
2. **Success-only in-place updates:** after delete/move/restore/uninstall, update current UI state without automatically rescanning; retain failed items. Verify pip uninstall against the same selected interpreter before removing a row.
3. **Silent child processes:** hide console windows for applicable application-launched subprocesses on Windows while retaining stdout/stderr/exit status for diagnostics.
4. **Packaging cleanup:** curate runtime assets/dependencies and validate a clean PyInstaller build and GUI launch.
5. **Lightweight desktop refresh:** improve CustomTkinter hierarchy/navigation/readability without migrating to Bootstrap or WebView and without adding unnecessary runtime weight.

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Cleanup targets data the user wanted to keep | Show paths, require selected items and confirmation, use Recycle Bin where supported, document backups |
| Incorrect app folder detection or interrupted move | Apply safety filters, preserve history, validate copy/junction steps, use rollback and keep failures visible |
| Multiple Python interpreters cause package confusion | Display the selected environment and execute package operations through that interpreter |
| Privileged system actions cause unexpected changes | Explain required elevation and action scope; confirm before destructive operations |
| External toolbox content changes or is unsafe | Treat third-party URLs/downloads as untrusted; require independent source verification |
| Large scans or UI-thread work affect responsiveness | Reuse worker-based scanning and measure resource use; avoid resident polling |

## 12. Success measures for future work

- Startup scan remains off by default; opt-in launches no more than one scan, respects checked categories, and introduces no resident process.
- Mutation flows remove only items verified as successful and do not start an automatic full scan.
- Applicable Windows child processes do not display terminal windows, while logs retain useful diagnostics.
- Clean packaging build and GUI smoke test succeed on a supported Windows build environment.
- UI refresh adds no browser runtime and does not materially increase packaged size or idle memory compared with the measured baseline.
