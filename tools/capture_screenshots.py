"""Capture actual Tk client pixels with demo data; Windows + Pillow required.

No desktop capture fallback. Startup patches come from the layout test BOOTSTRAP.
The source and tests remain unchanged. Run without administrator privileges.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import ExitStack
import ctypes
from ctypes import wintypes
import importlib
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
VIEWS = {
    "smart_cleaner": "smart-cleaner.png", "app_mover": "app-mover.png",
    "dup_finder": "duplicates.png", "py_libs": "python-libraries.png",
    "startup_svc": "startup-services.png", "ghost_toolbox": "system-toolbox.png",
}


class CaptureBlocked(RuntimeError):
    pass


def bootstrap_setup():
    """Parse shared bootstrap without importing tests; stop before app creation."""
    tree = ast.parse((ROOT / "tests/test_bootstrap_layout.py").read_text(encoding="utf-8"))
    source = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == "BOOTSTRAP" for t in n.targets))
    setup = ast.parse(source)
    for i, node in enumerate(setup.body):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "app" for t in node.targets):
            return compile(ast.Module(body=setup.body[:i], type_ignores=[]), "<layout-bootstrap>", "exec")
    raise CaptureBlocked("Shared BOOTSTRAP has no app construction boundary")


def capture_client(app):
    """PrintWindow captures only this HWND's client, even when covered."""
    from PIL import Image
    user, gdi = ctypes.windll.user32, ctypes.windll.gdi32
    user.GetDC.argtypes = [wintypes.HWND]
    user.GetDC.restype = wintypes.HDC
    user.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user.GetParent.argtypes = [wintypes.HWND]
    user.GetParent.restype = wintypes.HWND
    user.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    gdi.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi.CreateCompatibleDC.restype = wintypes.HDC
    gdi.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
    gdi.SelectObject.restype = wintypes.HGDIOBJ
    gdi.DeleteObject.argtypes = [wintypes.HGDIOBJ]
    gdi.DeleteDC.argtypes = [wintypes.HDC]
    gdi.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT,
                            wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT]

    class Header(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("width", wintypes.LONG), ("height", wintypes.LONG),
                    ("planes", wintypes.WORD), ("bits", wintypes.WORD), ("compression", wintypes.DWORD),
                    ("image_size", wintypes.DWORD), ("xppm", wintypes.LONG), ("yppm", wintypes.LONG),
                    ("used", wintypes.DWORD), ("important", wintypes.DWORD)]

    hwnd = user.GetParent(app.winfo_id()) or app.winfo_id()
    rect = wintypes.RECT()
    if not user.GetClientRect(hwnd, ctypes.byref(rect)):
        raise CaptureBlocked("Cannot measure Tk window")
    width, height = rect.right, rect.bottom
    if (width, height) != (1260, 840):
        raise CaptureBlocked(f"Expected 1260x840 client pixels, got {width}x{height}")
    dc = user.GetDC(hwnd)
    memory = bitmap = previous = None
    try:
        memory = gdi.CreateCompatibleDC(dc)
        bitmap = gdi.CreateCompatibleBitmap(dc, width, height)
        previous = gdi.SelectObject(memory, bitmap)
        if not user.PrintWindow(hwnd, memory, 3):  # CLIENTONLY | RENDERFULLCONTENT
            raise CaptureBlocked("PrintWindow failed; desktop fallback forbidden")
        gdi.SelectObject(memory, previous)
        previous = None
        info = Header(ctypes.sizeof(Header), width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
        pixels = ctypes.create_string_buffer(width * height * 4)
        if gdi.GetDIBits(memory, bitmap, 0, height, pixels, ctypes.byref(info), 0) != height:
            raise CaptureBlocked("Cannot read window bitmap")
        image = Image.frombuffer("RGB", (width, height), pixels.raw, "raw", "BGRX", 0, 1)
        if max(high - low for low, high in image.getextrema()) < 20:
            raise CaptureBlocked("Window capture is blank")
        return image
    finally:
        if previous:
            gdi.SelectObject(memory, previous)
        if bitmap:
            gdi.DeleteObject(bitmap)
        if memory:
            gdi.DeleteDC(memory)
        user.ReleaseDC(hwnd, dc)


def seed_demo(ui, app):
    for widget in app.smart_scroll.winfo_children():
        widget.destroy()
    app.smart_findings = [dict(name=name, path=path, size_bytes=size * 1024**2, badge="[DEMO]", type="folder")
                          for name, path, size in (("Browser Cache", "C:/Demo/Browser/Cache", 128),
                                                   ("Python Package Cache", "C:/Demo/Python/Cache", 256),
                                                   ("Project Bytecode", "C:/Demo/Project/__pycache__", 24))]
    for item in app.smart_findings:
        app._render_smart_row(item)
    app.update_smart_summary()
    app.lbl_scan_status.configure(text="DATA DEMO - bukan hasil pemindaian")
    app.app_items = [dict(name=f"Demo Editor {n}", path=f"C:/Demo/Apps/Editor{n}", size_bytes=n * 128 * 1024**2,
                         is_safe=True, reason="DATA DEMO") for n in (1, 2, 3)]
    for item in app.app_items:
        app._render_app_row(item)
    app.lib_items = [dict(name=name, version="1.0.0", size_bytes=size * 1024**2, used_by=[],
                         is_core=core, python_exe="C:/Demo/Python/python.exe")
                     for name, size, core in (("demo-core", 12, True), ("demo-parser", 8, False), ("demo-utils", 3, False))]
    for item in app.lib_items:
        app._render_lib_row(item)
    app.startup_items = [dict(name=f"Demo Launcher {n}", cmd=f"C:/Demo/Apps/Launcher{n}.exe",
                             root_tag="HKCU", is_enabled=n == 1) for n in (1, 2)]
    for item in app.startup_items:
        app._render_startup_row(item)
    items = [dict(group_id=1, path=f"C:/Demo/{folder}/sample.txt", name="sample.txt", size_bytes=2 * 1024**2,
                  mtime=1704067200 + n * 86400, is_newest=n == 1, is_oldest=n == 0)
             for n, folder in enumerate(("Original", "Copy"))]
    app.dup_groups = [dict(group_id=1, size_bytes=2 * 1024**2, items=items)]
    app.dup_items = items
    app._render_all_dup_groups()
    app.dup_target_dir = "C:/Demo"
    app.lbl_dup_path.configure(text="C:/Demo")
    app.var_recycle_reminder.set(False)
    app.installed_registry_map = {}
    app.native_app_data = [dict(id=f"demo-{n}", name=f"Demo Utility {n}", category="Utilities & Tools",
                                desc="DATA DEMO - contoh katalog, tanpa unduhan", filename=f"demo-{n}.exe", url="") for n in (1, 2, 3)]
    app._render_native_apps(app.native_app_data)
    ui.ctk.CTkLabel(app.sidebar_frame, text="DATA DEMO\nUI asli / tanpa scan sistem",
                   font=ui.ctk.CTkFont(size=11, weight="bold"), text_color=ui.UI_COLORS["warning"]).pack(side="bottom", pady=8)
    app.update()
    app.clear_log()
    app.log_box.insert("end", "DATA DEMO - UI asli dengan data demonstrasi.\nTidak ada scan, perubahan sistem, jaringan, atau installer yang dijalankan.\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "docs/images")
    args = parser.parse_args()
    if sys.platform != "win32":
        parser.error("Actual Tk capture requires Windows and an interactive desktop")
    from PIL import Image, PngImagePlugin  # noqa: F401 - preload before guards
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT))
    setup = bootstrap_setup()
    output = args.output_dir.resolve()
    violations = []
    audit_active = False

    def reject(*unused, **kwargs):
        violations.append("Unexpected work scheduled or system API invoked")
        raise CaptureBlocked(violations[-1])

    def audit(event, values):
        if not audit_active:
            return
        if event.startswith(("subprocess.", "socket.", "winreg.")) or event in ("os.system", "os.startfile", "os.startfile/2"):
            reject()
        mutation = event in ("os.remove", "os.rmdir", "os.mkdir", "os.rename", "shutil.copyfile", "shutil.rmtree")
        if event == "open":
            mode, flags = values[1:3]
            mutation = bool((isinstance(mode, str) and any(c in mode for c in "wax+")) or
                            (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)))
        if mutation:
            paths = values[:2] if event in ("os.rename", "shutil.copyfile") else values[:1]
            for path in paths:
                if isinstance(path, (str, bytes, os.PathLike)) and not Path(os.fsdecode(path)).resolve().is_relative_to(sandbox):
                    reject()

    sys.addaudithook(audit)
    app = None
    namespace = {}
    with tempfile.TemporaryDirectory(prefix="cleaner-screenshots-") as temporary:
        sandbox = Path(temporary).resolve()
        for folder in ("Local", "Roaming", "Home", "Downloads", "stage"):
            (sandbox / folder).mkdir()
        with ExitStack() as guards:
            guards.enter_context(patch.dict(os.environ, {"LOCALAPPDATA": str(sandbox / "Local"), "APPDATA": str(sandbox / "Roaming"),
                                                        "USERPROFILE": str(sandbox / "Home"), "HOME": str(sandbox / "Home")}))
            ui = importlib.import_module("dev_cleaner")
            try:
                audit_active = True
                exec(setup, namespace)
                guards.callback(namespace["stack"].close)
                for obj, name in ((ui.ThreadPoolExecutor, "submit"), (threading.Thread, "start"), (ui.subprocess, "Popen"),
                                  (ui.subprocess, "run"), (ui.urllib.request, "urlopen"), (socket, "create_connection"),
                                  (ui.webbrowser, "open"), (ui.os, "startfile"), (ui.os, "walk"),
                                  (ui.psutil, "process_iter"), (ui.psutil, "win_service_iter")):
                    guards.enter_context(patch.object(obj, name, side_effect=reject))
                for name in ("OpenKey", "OpenKeyEx", "CreateKey", "CreateKeyEx", "QueryValue", "QueryValueEx", "QueryInfoKey",
                             "EnumKey", "EnumValue", "SetValue", "SetValueEx", "DeleteKey", "DeleteValue"):
                    guards.enter_context(patch.object(ui.winreg, name, side_effect=reject))
                for name in ("scan_startup_items_async", "scan_installed_apps_async", "scan_libs_async", "start_smart_scan_async",
                             "start_dup_scan_async", "acquire_mutation_guard"):
                    guards.enter_context(patch.object(ui.DevAICleanerApp, name, side_effect=reject))
                guards.enter_context(patch.object(ui.DevAICleanerApp, "_get_cleaner_downloads_dir", return_value=str(sandbox / "Downloads")))
                guards.enter_context(patch.object(ui, "get_target_drive_options", return_value=[("C:/Demo/Target (demo only)", "C:/Demo/Target")]))
                guards.enter_context(patch.object(ui, "discover_python_environments", return_value={"Demo Python": "C:/Demo/Python/python.exe"}))
                guards.enter_context(patch.object(ui, "load_moves_history", return_value=[]))
                guards.enter_context(patch.object(ui, "save_moves_history", side_effect=reject))
                guards.enter_context(patch.object(ui, "save_startup_scan_preference", side_effect=reject))
                guards.enter_context(patch.object(ui.DevAICleanerApp, "report_callback_exception", side_effect=reject))
                # Retain the partially built root if construction fails, for cleanup.
                app = ui.DevAICleanerApp.__new__(ui.DevAICleanerApp)
                ui.DevAICleanerApp.__init__(app)
                app.geometry("1260x840+30+30")
                app.update()
                seed_demo(ui, app)
                for key, filename in VIEWS.items():
                    app.nav_buttons[key].invoke()
                    app.update_idletasks()
                    app.update()
                    if violations:
                        raise CaptureBlocked("Capture aborted after blocked work")
                    capture_client(app).save(sandbox / "stage" / filename, format="PNG")
                if violations:
                    raise CaptureBlocked("Capture aborted after blocked work")
            finally:
                try:
                    if app is not None and "tk" in app.__dict__:
                        for callback in app.tk.call("after", "info"):
                            app.after_cancel(callback)
                        if "executor" in app.__dict__:
                            app.executor.shutdown(wait=False, cancel_futures=True)
                        app.destroy()
                finally:
                    audit_active = False
        output.mkdir(parents=True, exist_ok=True)
        for filename in VIEWS.values():
            destination = output / filename
            destination.write_bytes((sandbox / "stage" / filename).read_bytes())
            print(f"Captured actual Tk client 1260x840: {destination}")
    print("Finished: zero scheduled jobs, network requests, registry access, or system mutations; temporary state removed.")


if __name__ == "__main__":
    main()
