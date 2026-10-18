"""
Dev & AI CLI Cleaner + App Mover Suite
Refactored UI: Full Left-Side Vertical Navigation Menu (Compact Layout)
With Compact Table List Layout, Smart Scanner, Safe Registry Cleaner,
and Startup & Windows Services Manager.
"""

import os
import sys
import shutil
import tempfile
import time
import json
import re
import threading
import subprocess
import winreg
import hashlib
import urllib.request
import urllib.error
import ssl
import webbrowser
import importlib.metadata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import psutil
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont


UI_COLORS = {
    "background": "#101827", "sidebar": "#0B1220", "card": "#182438",
    "header": "#203149", "border": "#34445B", "text": "#E8EEF7",
    "muted": "#A8B7CB", "primary": "#2DD4BF", "ink": "#062A27",
    "success": "#4ADE80", "warning": "#FBBF24", "danger": "#F87171",
}
# Translate legacy presentation colors in one place; scan metadata remains unchanged.
LEGACY_COLORS = {
    "#18191c": "card", "#1e2024": "background", "#141517": "sidebar",
    "#111827": "sidebar", "#0f172a": "header", "#1e293b": "header",
    "#334155": "border", "#94a3b8": "muted", "#64748b": "muted",
    "#e2e8f0": "text", "#ffffff": "text", "#38bdf8": "primary",
    "#0284c7": "primary", "#0369a1": "primary", "#16a34a": "success",
    "#dc2626": "danger", "#ea580c": "warning", "#ca8a04": "warning",
}


def ui_color(value):
    return UI_COLORS.get(LEGACY_COLORS.get(str(value).lower()), value)


def parent_background(master):
    try:
        return master.cget("background")
    except (tk.TclError, AttributeError):
        return UI_COLORS["background"]


def character_width(master, pixels, font=None, inset=0):
    """CTk dimensions are pixels; ttk text-widget widths are font characters."""
    metrics = tkfont.Font(master=master, font=font or ("Segoe UI", 10))
    return max(0, round((float(pixels) - inset) / max(1, metrics.measure("0"))))
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ScrolledFrame, ScrolledText
from send2trash import send2trash


class CTk:
    """ttkbootstrap Window adapter maintaining compatibility and super-lightweight RAM footprint."""
    pass


class _BootstrapUIAdapter:
    """Modern Bootstrap Desktop Adapter powered by ttkbootstrap."""

    Window = tb.Window

    @staticmethod
    def set_appearance_mode(mode):
        pass

    @staticmethod
    def set_default_color_theme(theme):
        pass

    @staticmethod
    def _filter_allowed_kwargs(widget_cls, kwargs, extra_strip=None):
        strip = {
            "fg_color", "text_color", "corner_radius", "hover_color", "border_color",
            "border_width", "progress_color", "segmented_button_selected_color",
            "segmented_button_selected_hover_color", "segmented_button_unselected_color",
            "segmented_button_unselected_hover_color", "button_color", "button_hover_color",
            "dropdown_fg_color", "dropdown_hover_color", "dropdown_text_color",
            "checkbox_width", "checkbox_height", "radiobutton_width", "radiobutton_height",
            "hover", "state_color"
        }
        if extra_strip:
            strip.update(extra_strip)
        res = {}
        for k, v in kwargs.items():
            if k in strip:
                continue
            res[k] = v
        return res

    @staticmethod
    def _clean_tk_kwargs(kwargs, remove_height=False, remove_font=False):
        strip = {
            "fg_color", "text_color", "corner_radius", "hover_color", "border_color",
            "border_width", "progress_color", "segmented_button_selected_color",
            "segmented_button_selected_hover_color", "segmented_button_unselected_color",
            "segmented_button_unselected_hover_color", "button_color", "button_hover_color",
            "dropdown_fg_color", "dropdown_hover_color", "dropdown_text_color",
            "checkbox_width", "checkbox_height", "radiobutton_width", "radiobutton_height",
            "hover", "state_color", "anchor"
        }
        res = {k: v for k, v in kwargs.items() if k not in strip}
        if remove_height:
            res.pop("height", None)
        if remove_font:
            res.pop("font", None)
        return res

    @staticmethod
    def _text_options(master, kwargs, styled=False, inset=16):
        font = kwargs.get("font") or ("Segoe UI", 10)
        kw = _BootstrapUIAdapter._clean_tk_kwargs(kwargs, remove_height=True, remove_font=styled)
        if "width" in kw:
            kw["width"] = character_width(master, kw["width"], font, inset)
        if not styled:
            kw["font"] = font
        return kw

    @staticmethod
    def _font_style(widget, font):
        if font:
            base = widget.cget("style") or widget.winfo_class()
            name = f"Compact{str(font).encode().hex()}.{base}"
            tb.Style().configure(name, font=font, padding=(8, 5))
            widget.configure(style=name)

    class CTk(tb.Window):
        def __init__(self, *args, **kwargs):
            themename = kwargs.pop("themename", "darkly")
            super().__init__(*args, themename=themename, **kwargs)
            self.configure(background=UI_COLORS["background"])
            style = tb.Style()
            style.configure(".", font=("Segoe UI", 10), background=UI_COLORS["background"], foreground=UI_COLORS["text"])
            for kind in ("TButton", "TMenubutton"):
                style.configure(kind, padding=(8, 5), font=("Segoe UI", 10))
            style.configure("TCheckbutton", background=UI_COLORS["card"], font=("Segoe UI", 10))
            for semantic in ("primary", "success", "warning", "danger", "secondary"):
                color = UI_COLORS.get(semantic, UI_COLORS["border"])
                for kind in ("TButton", "TMenubutton"):
                    name = f"{semantic}.{kind}"
                    style.configure(name, background=color, foreground=UI_COLORS["ink"], padding=(8, 5))
                    style.map(name, background=[("disabled", UI_COLORS["border"]), ("pressed", UI_COLORS["muted"]), ("active", UI_COLORS["text"])], foreground=[("disabled", UI_COLORS["muted"]), ("active", UI_COLORS["ink"])])

    class CTkFrame(tk.Frame):
        def __init__(self, master=None, corner_radius=None, fg_color=None, border_width=None, border_color=None, **kwargs):
            kwargs.pop("bootstyle", None)
            bg = ui_color(fg_color) or UI_COLORS["card"]
            if bg == "transparent":
                try:
                    bg = master.cget("bg")
                except Exception:
                    bg = "#14171d"
            bd = border_width or 0
            hl = ui_color(border_color) or UI_COLORS["border"]
            kwargs.pop("border_color", None)
            kwargs.pop("border_width", None)
            kwargs.pop("corner_radius", None)
            kwargs.pop("fg_color", None)
            super().__init__(master, bg=bg, highlightthickness=bd, highlightbackground=hl, **kwargs)

        def configure(self, cnf=None, **kwargs):
            if cnf and isinstance(cnf, dict):
                kwargs.update(cnf)
            fg = kwargs.pop("fg_color", None)
            if fg:
                if fg == "transparent":
                    try:
                        fg = self.master.cget("bg")
                    except Exception:
                        fg = "#14171d"
                self.config(bg=ui_color(fg))
            bd = kwargs.pop("border_width", None)
            if bd is not None:
                self.config(highlightthickness=bd)
            bc = kwargs.pop("border_color", None)
            if bc is not None:
                self.config(highlightbackground=bc)
            kwargs.pop("corner_radius", None)
            kwargs.pop("bootstyle", None)
            super().configure(**kwargs)

    class CTkScrollableFrame(ScrolledFrame):
        def __init__(self, master=None, corner_radius=None, fg_color=None, **kwargs):
            kw = _BootstrapUIAdapter._clean_tk_kwargs(kwargs)
            super().__init__(master, autohide=True, **kw)

    class CTkLabel(tb.Label):
        def __init__(self, master=None, text="", font=None, text_color=None, fg_color=None, **kwargs):
            kwargs.pop("bootstyle", None)
            kwargs.pop("corner_radius", None)
            kwargs.pop("height", None)
            self._pixel_width = kwargs.pop("width", None)
            self._label_font = font or ("Segoe UI", 10)
            bg = parent_background(master) if fg_color in (None, "transparent") else ui_color(fg_color)
            fg = ui_color(text_color) if text_color else UI_COLORS["text"]
            if bg in (UI_COLORS["success"], UI_COLORS["warning"], UI_COLORS["danger"], UI_COLORS["primary"]):
                fg = UI_COLORS["ink"]
            if self._pixel_width is not None:
                kwargs["width"] = character_width(master, self._pixel_width, self._label_font)
            super().__init__(master, text=text, font=self._label_font, background=bg, foreground=fg, **kwargs)

        def configure(self, cnf=None, **kwargs):
            if isinstance(cnf, str):
                return super().configure(cnf)
            if isinstance(cnf, dict):
                kwargs.update(cnf)
            if "font" in kwargs:
                self._label_font = kwargs["font"]
            if "width" in kwargs:
                self._pixel_width = kwargs.pop("width")
            if self._pixel_width is not None:
                kwargs["width"] = character_width(self.master, self._pixel_width, self._label_font)
            if "text_color" in kwargs:
                kwargs["foreground"] = ui_color(kwargs.pop("text_color"))
            if "fg_color" in kwargs:
                color = kwargs.pop("fg_color")
                kwargs["background"] = parent_background(self.master) if color == "transparent" else ui_color(color)
                if kwargs["background"] in (UI_COLORS["success"], UI_COLORS["warning"], UI_COLORS["danger"], UI_COLORS["primary"]):
                    kwargs["foreground"] = UI_COLORS["ink"]
            background = kwargs.get("background", self.cget("background"))
            if background in (UI_COLORS["success"], UI_COLORS["warning"], UI_COLORS["danger"], UI_COLORS["primary"]):
                kwargs["foreground"] = UI_COLORS["ink"]
            kwargs.pop("height", None)
            kwargs.pop("corner_radius", None)
            return super().configure(**kwargs)

    class CTkButton(tb.Button):
        def __init__(self, master=None, text="", command=None, fg_color=None, hover_color=None, **kwargs):
            bootstyle = kwargs.pop("bootstyle", "")
            cursor = kwargs.pop("cursor", "hand2")
            if not bootstyle:
                fg = fg_color or kwargs.pop("fg_color", None)
                if fg:
                    fgl = str(fg).lower()
                    if "dc2626" in fgl or "b91c1c" in fgl or "red" in fgl:
                        bootstyle = "danger"
                    elif "ea580c" in fgl or "orange" in fgl:
                        bootstyle = "warning"
                    elif "16a34a" in fgl or "green" in fgl:
                        bootstyle = "success"
                    elif "transparent" in fgl or "334155" in fgl or "272a30" in fgl:
                        bootstyle = "secondary-outline"
                    else:
                        bootstyle = "primary"
                else:
                    bootstyle = "primary"
            kw = _BootstrapUIAdapter._text_options(master, kwargs, styled=True)
            super().__init__(master, text=text, command=command, bootstyle=bootstyle, cursor=cursor, **kw)
            _BootstrapUIAdapter._font_style(self, kwargs.get("font"))

        def configure(self, cnf=None, **kwargs):
            if cnf and isinstance(cnf, dict):
                kwargs.update(cnf)
            fg = kwargs.pop("fg_color", None)
            tc = kwargs.pop("text_color", None)
            if fg:
                fgl = str(fg).lower()
                if "transparent" in fgl:
                    kwargs["bootstyle"] = "secondary-outline"
                elif "dc2626" in fgl or "red" in fgl:
                    kwargs["bootstyle"] = "danger"
                elif "16a34a" in fgl or "green" in fgl:
                    kwargs["bootstyle"] = "success"
                elif "ea580c" in fgl or "orange" in fgl:
                    kwargs["bootstyle"] = "warning"
                else:
                    kwargs["bootstyle"] = "primary"
            kw = _BootstrapUIAdapter._text_options(self.master, kwargs, styled=True)
            super().configure(**kw)

    class CTkCheckBox(tb.Checkbutton):
        def __init__(self, master=None, text="", variable=None, command=None, **kwargs):
            bootstyle = kwargs.pop("bootstyle", "primary")
            kw = _BootstrapUIAdapter._text_options(master, kwargs, styled=True, inset=25)
            if not text:
                kw["width"] = 0
            super().__init__(master, text=text, variable=variable, command=command, bootstyle=bootstyle, **kw)
            _BootstrapUIAdapter._font_style(self, kwargs.get("font"))

    class CTkEntry(tb.Entry):
        def __init__(self, master=None, placeholder_text=None, **kwargs):
            bootstyle = kwargs.pop("bootstyle", "dark")
            kw = _BootstrapUIAdapter._text_options(master, kwargs)
            super().__init__(master, bootstyle=bootstyle, **kw)

    class CTkComboBox(tb.Combobox):
        def __init__(self, master=None, values=None, command=None, **kwargs):
            kw = _BootstrapUIAdapter._text_options(master, kwargs)
            super().__init__(master, values=values or [], **kw)
            if command:
                self.bind("<<ComboboxSelected>>", lambda e: command(self.get()))

    class CTkOptionMenu(tb.Menubutton):
        def __init__(self, master=None, values=None, command=None, **kwargs):
            self.command = command
            self.values = values or []
            self.var = tb.StringVar(value=self.values[0] if self.values else "")
            bootstyle = kwargs.pop("bootstyle", "secondary")
            kw = _BootstrapUIAdapter._text_options(master, kwargs, styled=True)
            super().__init__(master, textvariable=self.var, bootstyle=bootstyle, **kw)
            self.menu = tb.Menu(self, tearoff=0)
            self["menu"] = self.menu
            self._rebuild_menu()

        def _select(self, value):
            self.set(value)
            if self.command:
                self.command(value)

        def _rebuild_menu(self):
            self.menu.delete(0, "end")
            for val in self.values:
                self.menu.add_command(label=val, command=lambda v=val: self._select(v))

        def configure(self, cnf=None, **kwargs):
            if cnf:
                if isinstance(cnf, dict):
                    kwargs.update(cnf)
            if "values" in kwargs:
                self.values = kwargs.pop("values")
                self._rebuild_menu()
            clean_kw = _BootstrapUIAdapter._text_options(self.master, kwargs, styled=True)
            super().configure(**clean_kw)

        def set(self, val):
            self.var.set(val)

        def get(self):
            return self.var.get()

    class CTkProgressBar(tb.Progressbar):
        def __init__(self, master=None, **kwargs):
            bootstyle = kwargs.pop("bootstyle", (STRIPED, SUCCESS))
            kw = _BootstrapUIAdapter._clean_tk_kwargs(kwargs, remove_height=True)
            super().__init__(master, bootstyle=bootstyle, maximum=100, **kw)

        def set(self, val):
            try:
                # CTk progress bar set is 0.0 to 1.0, ttk is 0 to maximum (100)
                num = float(val)
                if num <= 1.0:
                    self.configure(value=num * 100)
                else:
                    self.configure(value=num)
            except Exception:
                pass

    class CTkTextbox(ScrolledText):
        def __init__(self, master=None, **kwargs):
            kw = _BootstrapUIAdapter._clean_tk_kwargs(kwargs)
            super().__init__(master, autohide=True, **kw)

    class CTkSegmentedButton(tb.Frame):
        def __init__(self, master=None, values=None, command=None, **kwargs):
            super().__init__(master)
            self.command = command
            self.values = values or []
            self.buttons = {}
            self.current_value = self.values[0] if self.values else ""
            for val in self.values:
                b = tb.Button(self, text=val, bootstyle="secondary-outline",
                              command=lambda v=val: self.set(v, invoke_command=True))
                index = len(self.buttons)
                b.grid(row=index // 2, column=index % 2, sticky="ew", padx=2, pady=2)
                self.columnconfigure(index % 2, weight=1)
                self.buttons[val] = b
            if self.current_value:
                self.set(self.current_value)

        def set(self, val, invoke_command=False):
            self.current_value = val
            for k, b in self.buttons.items():
                if k == val:
                    b.configure(bootstyle="primary")
                else:
                    b.configure(bootstyle="secondary-outline")
            if invoke_command and self.command:
                self.command(val)

        def get(self):
            return self.current_value

    class CTkFont:
        def __new__(cls, *args, **kwargs):
            family = kwargs.get("family", "Segoe UI")
            size = kwargs.get("size", 10)
            weight = kwargs.get("weight", "normal")
            slant = kwargs.get("slant", "roman")
            styles = []
            if weight == "bold":
                styles.append("bold")
            if slant == "italic":
                styles.append("italic")
            style_str = " ".join(styles) if styles else "normal"
            return (family, -size, style_str)


ctk = _BootstrapUIAdapter()

PROTECTED_PACKAGES = {"pip", "setuptools", "wheel", "ttkbootstrap", "customtkinter", "send2trash", "darkdetect", "psutil"}
BLOCKED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".md", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".sql", ".db", ".sqlite"}
BLOCKED_DIRS = {"windows", "system32", "program files", "program files (x86)", "appdata\\local\\microsoft"}

BLOCKED_APP_PATTERNS = [
    r'Windhawk', r'ExplorerPatcher', r'StartAllBack', r'Start11', r'Open-Shell', r'TranslucentTB',
    r'Microsoft Visual C\+\+', r'Microsoft Edge', r'WebView2', r'Windows', r'Defender',
    r'Antivirus', r'Security', r'Driver', r'Intel', r'AMD Software', r'NVIDIA', r'Realtek',
    r'Runtime', r'\.NET', r'OneDrive', r'Creative Cloud', r'Adobe Genuine', r'DirectX',
    r'Windows Subsystem', r'Hyper-V', r'Bonjour', r'Common Files'
]

MOVES_HISTORY_DIR = os.path.join(os.getenv("LOCALAPPDATA", "C:\\"), "DevAICleaner")
MOVES_HISTORY_FILE = os.path.join(MOVES_HISTORY_DIR, "moves.json")
REG_BACKUP_DIR = os.path.join(MOVES_HISTORY_DIR, "RegistryBackups")
PY_LIBS_DEBUG_LOG = os.path.join(MOVES_HISTORY_DIR, "py_libs_debug.log")
STARTUP_SCAN_PREFERENCE_FILE = os.path.join(MOVES_HISTORY_DIR, "preferences.json")


def hidden_console_creation_flags():
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def load_startup_scan_preference(path=STARTUP_SCAN_PREFERENCE_FILE):
    try:
        with open(path, "r", encoding="utf-8") as prefs:
            value = json.load(prefs).get("startup_smart_scan", False)
        return value is True
    except (OSError, ValueError, AttributeError, TypeError):
        return False


def save_startup_scan_preference(path, enabled):
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as prefs:
            json.dump({"startup_smart_scan": bool(enabled)}, prefs)
        return True
    except (OSError, TypeError, ValueError):
        return False


def log_py_debug(msg):
    try:
        os.makedirs(MOVES_HISTORY_DIR, exist_ok=True)
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(PY_LIBS_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def is_user_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def discover_python_environments():
    pythons = {}
    # 1. Running sys.executable if valid python
    if os.path.exists(sys.executable) and not getattr(sys, 'frozen', False):
        pythons['Python Berjalan (Current)'] = sys.executable

    # 2. Windows Registry PEP 514
    reg_roots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Python\PythonCore"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Python\PythonCore"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Python\PythonCore")
    ]
    for r, base in reg_roots:
        try:
            with winreg.OpenKey(r, base) as k:
                for i in range(winreg.QueryInfoKey(k)[0]):
                    ver = winreg.EnumKey(k, i)
                    try:
                        with winreg.OpenKey(r, f"{base}\\{ver}\\InstallPath") as ik:
                            p = winreg.QueryValue(ik, "")
                            exe = os.path.join(p, "python.exe")
                            if os.path.exists(exe):
                                pythons[f"Python {ver} (Registry)"] = exe
                    except Exception:
                        pass
        except Exception:
            pass

    # 3. Known Standard Installations
    known = [
        ("FlyEnv Python", r"C:\Program Files\FlyEnv-Data\env\python\python.exe"),
        ("User Python 3.11", os.path.expanduser(r"~\AppData\Local\Programs\Python\Python311\python.exe")),
        ("User Python 3.12", os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe")),
        ("User Python 3.10", os.path.expanduser(r"~\AppData\Local\Programs\Python\Python310\python.exe")),
        ("System Python 3.12", r"C:\Program Files\Python312\python.exe"),
        ("System Python 3.11", r"C:\Program Files\Python311\python.exe"),
        ("System Python 3.10", r"C:\Program Files\Python310\python.exe")
    ]
    for lbl, exe in known:
        if os.path.exists(exe) and exe not in pythons.values():
            pythons[lbl] = exe

    # Fallback jika kosong
    if not pythons:
        pythons["Python Default"] = "python"

    return pythons


def is_junction(path_str):
    try:
        if not os.path.lexists(path_str):
            return False
        # Di Windows, directory junction adalah NTFS reparse point (0x400) yang harus dicek via os.lstat
        attrs = os.lstat(path_str).st_file_attributes
        return bool(attrs & 0x400)
    except Exception:
        return False


def directory_manifest(path):
    """Hash regular files without following reparse points; fail closed on unreadable data."""
    if not os.path.isdir(path) or os.path.islink(path) or is_junction(path):
        raise OSError(f"Folder verifikasi tidak valid atau berupa reparse point: {path}")
    manifest = {}
    def walk_error(error):
        raise error
    for root, dirs, files in os.walk(path, followlinks=False, onerror=walk_error):
        for name in dirs + files:
            full_path = os.path.join(root, name)
            if os.path.islink(full_path) or is_junction(full_path):
                raise OSError(f"Reparse point tidak didukung untuk verifikasi: {full_path}")
        for name in dirs:
            manifest[os.path.relpath(os.path.join(root, name), path)] = None
        for name in files:
            full_path = os.path.join(root, name)
            digest = hashlib.sha256()
            with open(full_path, "rb") as file:
                for chunk in iter(lambda: file.read(1024 * 1024), b""):
                    digest.update(chunk)
            manifest[os.path.relpath(full_path, path)] = digest.hexdigest()
    return manifest


def cleanup_verified_copy(original, target, manifest):
    """Remove only unchanged remnants of a recorded copy after verifying its survivor."""
    original_real = os.path.normcase(os.path.realpath(original))
    target_real = os.path.normcase(os.path.realpath(target))
    try:
        common = os.path.commonpath([original_real, target_real])
    except ValueError:
        common = None
    if common in (original_real, target_real):
        raise OSError("Lokasi salinan pemulihan tidak boleh sama atau bersarang.")
    if not isinstance(manifest, dict) or directory_manifest(original) != manifest:
        raise OSError("Folder hasil pemulihan berubah; pembersihan otomatis dibatalkan.")
    if not os.path.lexists(target):
        return
    remaining = directory_manifest(target)
    if any(name not in manifest or manifest[name] != digest
           for name, digest in remaining.items()):
        raise OSError("Salinan target berubah; data dipertahankan untuk pemeriksaan manual.")
    # Validate everything before deletion, then recheck each entry as it is removed.
    for name, digest in sorted(remaining.items(), key=lambda pair: pair[0].count(os.sep), reverse=True):
        path = os.path.join(target, name)
        if os.path.islink(path) or is_junction(path):
            raise OSError(f"Lokasi pembersihan berubah: {path}")
        if digest is None:
            os.rmdir(path)
        else:
            if directory_manifest(original) != manifest:
                raise OSError("Folder hasil pemulihan berubah selama pembersihan.")
            with open(path, "rb") as file:
                actual = hashlib.sha256()
                for chunk in iter(lambda: file.read(1024 * 1024), b""):
                    actual.update(chunk)
            if actual.hexdigest() != digest:
                raise OSError(f"File target berubah: {path}")
            os.remove(path)
    os.rmdir(target)


def get_directory_size_bytes(path):
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_directory_size_bytes(entry.path)
                except (PermissionError, FileNotFoundError, OSError):
                    pass
    except (PermissionError, FileNotFoundError, OSError):
        pass
    return total


def format_size(bytes_val):
    if bytes_val >= 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"
    elif bytes_val >= 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val} B"


def load_moves_history():
    try:
        with open(MOVES_HISTORY_FILE, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []
    if not isinstance(data, list):
        raise ValueError("Riwayat pemindahan harus berupa daftar; file tidak diubah.")
    records = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Entri riwayat pemindahan tidak valid; file tidak diubah.")
        orig = item.get("original_path") or item.get("Original")
        target = item.get("target_path") or item.get("Destination")
        if not isinstance(orig, str) or not orig or not isinstance(target, str) or not target:
            raise ValueError("Lokasi riwayat pemindahan tidak valid; file tidak diubah.")
        record = dict(item)
        record.update({"name": item.get("name") or item.get("Name", "Aplikasi"),
                       "original_path": orig, "target_path": target,
                       "size_bytes": item.get("size_bytes", 0),
                       "date": item.get("date") or item.get("Date", "")})
        records.append(record)
    return records


def save_moves_history(records):
    os.makedirs(MOVES_HISTORY_DIR, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=MOVES_HISTORY_DIR,
                                         prefix="moves-", suffix=".tmp", delete=False) as file:
            temporary_path = file.name
            json.dump(records, file, indent=2, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_path, MOVES_HISTORY_FILE)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


def get_target_drive_options():
    options = []
    try:
        for part in psutil.disk_partitions(all=False):
            if "cdrom" in part.opts or not part.device:
                continue
            drive_letter = part.mountpoint.rstrip("\\")
            if drive_letter.upper() == "C:":
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                free_gb = usage.free / (1024 * 1024 * 1024)
                if free_gb >= 2.0:
                    options.append((f"{drive_letter}\\DevApps ({free_gb:.1f} GB Free)", f"{drive_letter}\\DevApps", usage.free))
            except Exception:
                pass
    except Exception:
        pass

    options.sort(key=lambda x: x[2], reverse=True)
    return options


def stop_processes_in_folder(folder_path):
    folder_abs = str(Path(folder_path).resolve()).lower()
    stopped = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            exe = proc.info.get('exe')
            if exe and str(Path(exe).resolve()).lower().startswith(folder_abs):
                proc.terminate()
                stopped.append(proc.info['name'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if stopped:
        time.sleep(1.5)
    return stopped


# ==========================================
# REGISTRY CLEANER & BACKUP HELPERS
# ==========================================
def create_registry_backup(keys_data, log_callback=None):
    backup_file = None
    try:
        if not keys_data:
            return None
        os.makedirs(REG_BACKUP_DIR, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="registry-export-", dir=REG_BACKUP_DIR) as staging:
            exports = []
            for index, item in enumerate(keys_data):
                root_str = item.get("root_str", "")
                sub_path = item.get("sub_path", "")
                if root_str not in ("HKEY_LOCAL_MACHINE", "HKEY_CURRENT_USER") or not sub_path:
                    raise ValueError("Lokasi registry backup tidak valid.")
                key_path = f"{root_str}\\{sub_path}"
                export_path = os.path.join(staging, f"{index}.reg")
                result = subprocess.run(["reg.exe", "export", key_path, export_path, "/y"],
                                        capture_output=True, text=True,
                                        creationflags=hidden_console_creation_flags())
                if result.returncode != 0:
                    raise OSError(result.stderr.strip() or result.stdout.strip() or "Ekspor registry gagal.")
                with open(export_path, encoding="utf-16") as exported:
                    text = exported.read()
                header = "Windows Registry Editor Version 5.00"
                if not text.startswith(header) or f"[{key_path}]" not in text:
                    raise OSError("Hasil ekspor registry tidak valid.")
                exports.append(text[len(header):].lstrip("\r\n"))
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-16", dir=REG_BACKUP_DIR,
                                             prefix="Registry_Backup_", suffix=".reg", delete=False) as backup:
                backup_file = backup.name
                backup.write(header + "\n\n" + "\n".join(exports))
                backup.flush()
                os.fsync(backup.fileno())
        if log_callback:
            log_callback(f"Backup registry dibuat: {backup_file}")
        return backup_file
    except Exception as error:
        if backup_file and os.path.exists(backup_file):
            os.remove(backup_file)
        if log_callback:
            log_callback(f"Gagal membuat backup registry: {error}")
        return None


def scan_registry_orphans():
    orphans = []
    # 1. Broken App Paths
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\App Paths")
        for i in range(winreg.QueryInfoKey(k)[0]):
            subname = winreg.EnumKey(k, i)
            try:
                sk = winreg.OpenKey(k, subname)
                try:
                    target, _ = winreg.QueryValueEx(sk, "")
                    t = os.path.expandvars(target.strip('"').strip())
                    if t and not os.path.exists(t):
                        orphans.append({
                            "type": "reg_app_path",
                            "name": f"App Path: {subname}",
                            "path": f"HKLM\\...\\App Paths\\{subname}",
                            "detail": f"File tujuan hilang: {t}",
                            "root": winreg.HKEY_LOCAL_MACHINE,
                            "root_str": "HKEY_LOCAL_MACHINE",
                            "sub_path": rf"Software\Microsoft\Windows\CurrentVersion\App Paths\{subname}",
                            "key_name": subname,
                            "size_bytes": 1024,
                            "badge": "[REGISTRY]",
                            "badge_color": "#EA580C"
                        })
                except OSError:
                    pass
            except OSError:
                pass
    except Exception:
        pass

    # 2. Orphaned Uninstall Entries
    uninstall_roots = [
        (winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE", r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE", r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, "HKEY_CURRENT_USER", r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    for root_h, root_name, base_sub in uninstall_roots:
        try:
            bk = winreg.OpenKey(root_h, base_sub)
            for i in range(winreg.QueryInfoKey(bk)[0]):
                subname = winreg.EnumKey(bk, i)
                try:
                    sk = winreg.OpenKey(bk, subname)
                    try:
                        disp_name, _ = winreg.QueryValueEx(sk, "DisplayName")
                        loc = ""
                        try:
                            loc, _ = winreg.QueryValueEx(sk, "InstallLocation")
                            loc = os.path.expandvars(loc.strip('"').strip())
                        except OSError:
                            pass
                        if loc and not os.path.exists(loc) and not any(re.search(pat, disp_name, re.I) for pat in BLOCKED_APP_PATTERNS):
                            orphans.append({
                                "type": "reg_uninstall",
                                "name": f"Sisa Uninstall: {disp_name}",
                                "path": f"{root_name}\\...\\Uninstall\\{subname}",
                                "detail": f"Folder instalasi sudah tidak ada: {loc}",
                                "root": root_h,
                                "root_str": root_name,
                                "sub_path": rf"{base_sub}\{subname}",
                                "key_name": subname,
                                "size_bytes": 2048,
                                "badge": "[REGISTRY]",
                                "badge_color": "#EA580C"
                            })
                    except OSError:
                        pass
                except OSError:
                    pass
        except Exception:
            pass

    return orphans


# ==========================================
# MAIN APPLICATION CLASS
# ==========================================
class DevAICleanerApp(ctk.CTk):
    active_mutation = None
    is_scanning_smart = False
    is_scanning_apps = False
    is_scanning_libs = False
    is_scanning_dup = False
    is_scanning_startup = False
    is_scanning_services = False

    def __init__(self):
        super().__init__()
        self.title("Dev & AI CLI Cleaner - All-In-One Modern Suite")
        self.geometry("1260x840")
        self.minsize(1050, 720)

        self.executor = ThreadPoolExecutor(max_workers=4)
        self.selected_smart_items = []
        self.smart_findings = []
        self.app_items = []
        self.lib_items = []
        self.startup_items = []
        self.service_items = []
        self.dup_groups = []
        self.dup_items = []
        self.dup_target_dir = os.path.expanduser("~\\Downloads")
        if not os.path.exists(self.dup_target_dir):
            self.dup_target_dir = str(Path.home())
        # Default project dir: Cek D:\coding atau fallback ke ~\\Projects atau ~
        if os.path.exists(r"D:\coding"):
            self.custom_project_dir = r"D:\coding"
        elif os.path.exists(os.path.expanduser("~\\Projects")):
            self.custom_project_dir = os.path.expanduser("~\\Projects")
        else:
            self.custom_project_dir = str(Path.home())

        # Single-task debouncing locks
        self.is_scanning_smart = False
        self.is_scanning_apps = False
        self.is_scanning_libs = False
        self.is_scanning_dup = False
        self.is_scanning_startup = False
        self.is_scanning_services = False
        self.active_mutation = None

        self.startup_scan_var = tk.BooleanVar(value=load_startup_scan_preference())
        self.create_layout()
        self.log("Aplikasi siap. Navigasi menu dan tampilan tabel siap digunakan.")
        self.log("Silakan klik 'SMART SCAN (ANALISIS)' untuk memulai pemindaian file sampah.")
        self.after(0, self.auto_initial_scan)

    def acquire_mutation_guard(self, operation_name):
        if self.active_mutation is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; permintaan '{operation_name}' dibatalkan.")
            return False
        # Check if any scan is active
        if (getattr(self, "is_scanning_smart", False) or
            getattr(self, "is_scanning_apps", False) or
            getattr(self, "is_scanning_libs", False) or
            getattr(self, "is_scanning_dup", False) or
            getattr(self, "is_scanning_startup", False) or
            getattr(self, "is_scanning_services", False)):
            self.log(f"Pemindaian sedang berjalan; operasi '{operation_name}' tidak dapat dijalankan.")
            return False
        self.active_mutation = operation_name
        return True

    def release_mutation_guard(self):
        self.active_mutation = None

    def create_layout(self):
        # Master Container: Left Sidebar Menu + Right Content Canvas
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # 1. LEFT SIDEBAR MENU (Semua Menu di Sebelah Kiri)
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self.main_container, width=256, corner_radius=0, fg_color=UI_COLORS["sidebar"])
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)

        # App Brand / Title
        brand_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_frame.pack(fill="x", padx=15, pady=(18, 12))

        lbl_app_title = ctk.CTkLabel(
            brand_frame,
            text="⚡ DEV & AI CLEANER",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#38BDF8"
        )
        lbl_app_title.pack(anchor="w")

        lbl_app_sub = ctk.CTkLabel(
            brand_frame,
            text="System & Dev Optimizer Suite",
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8"
        )
        lbl_app_sub.pack(anchor="w")

        # Disk C: Indicator Badge
        c_usage = psutil.disk_usage("C:\\")
        c_free_gb = c_usage.free / (1024 * 1024 * 1024)
        c_total_gb = c_usage.total / (1024 * 1024 * 1024)
        self.lbl_disk_c = ctk.CTkLabel(
            self.sidebar_frame,
            text=f"Drive C: {c_free_gb:.1f} GB Free / {c_total_gb:.0f} GB",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#0F172A",
            corner_radius=6,
            text_color="#4ADE80",
            height=28
        )
        self.lbl_disk_c.pack(fill="x", padx=15, pady=(0, 15))

        # Main Navigation Buttons (Kiri Semua)
        nav_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="NAVIGASI UTAMA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#64748B"
        )
        nav_label.pack(anchor="w", padx=18, pady=(0, 4))

        self.nav_buttons = {}
        nav_items = [
            ("smart_cleaner", "🧹  Smart Cleaner"),
            ("app_mover", "📦  App Mover & Restore"),
            ("dup_finder", "📑  Duplicate File Finder (Safe)"),
            ("py_libs", "🐍  Python Library Manager"),
            ("startup_svc", "⚡  Startup & Windows Services"),
            ("ghost_toolbox", "🛠️  System Toolbox (Tweaks & Tools)")
        ]

        for key, text in nav_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                anchor="w",
                font=ctk.CTkFont(size=13, weight="bold"),
                height=38,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#272A30",
                text_color="#E2E8F0",
                command=lambda k=key: self.switch_view(k)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = btn

        # Separator line
        sep = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color="#334155")
        sep.pack(fill="x", padx=15, pady=12)

        # -------------------------------------------------------------
        # SUB-KATEGORI CHECKLIST (COMPACT STYLE) KHUSUS SMART CLEANER
        # -------------------------------------------------------------
        self.subcat_container = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.subcat_container.pack(fill="both", expand=True, padx=10, pady=0)

        lbl_subcat = ctk.CTkLabel(
            self.subcat_container,
            text="SUB-KATEGORI PEMBERSIHAN:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#64748B"
        )
        lbl_subcat.pack(anchor="w", padx=8, pady=(0, 4))

        self.subcat_scroll = ctk.CTkScrollableFrame(self.subcat_container, fg_color="transparent")
        self.subcat_scroll.pack(fill="both", expand=True)

        self.init_subcat_checklist()

        # -------------------------------------------------------------
        # 2. RIGHT CONTENT CANVAS (Main Area)
        # -------------------------------------------------------------
        self.content_area = ctk.CTkFrame(self.main_container, corner_radius=0, fg_color="#1E2024")
        self.content_area.pack(side="right", fill="both", expand=True)

        # View Containers (Stacked in Right Canvas)
        self.views = {
            "smart_cleaner": ctk.CTkFrame(self.content_area, fg_color="transparent"),
            "app_mover": ctk.CTkFrame(self.content_area, fg_color="transparent"),
            "dup_finder": ctk.CTkFrame(self.content_area, fg_color="transparent"),
            "py_libs": ctk.CTkFrame(self.content_area, fg_color="transparent"),
            "startup_svc": ctk.CTkFrame(self.content_area, fg_color="transparent"),
            "ghost_toolbox": ctk.CTkFrame(self.content_area, fg_color="transparent")
        }

        self.setup_smart_cleaner_view()
        self.setup_app_mover_view()
        self.setup_dup_finder_view()
        self.setup_py_libs_view()
        self.setup_startup_svc_view()
        self.setup_ghost_toolbox_view()

        # Wrap the compact action controls rather than clipping their callbacks away.
        for view in self.views.values():
            self._compact_toolbar(view.winfo_children()[0])
        self._compact_toolbar(self.chk_recycle_reminder.master)
        self._compact_toolbar(self.native_app_search.master)

        # Log Execution Drawer at bottom
        self.setup_log_drawer()

        # Default Active View
        self.switch_view("smart_cleaner")

    def _compact_toolbar(self, bar):
        """Flow existing controls into grid rows using their actual requested sizes."""
        children = list(bar.winfo_children())
        for child in children:
            child.pack_forget()
        bar.pack_propagate(True)
        bar.grid_propagate(True)

        def reflow(event=None):
            available = max(1, event.width if event is not None else 730)
            row = used = 0
            for child in children:
                if getattr(child, "_toolbar_hidden", False):
                    child.grid_remove()
                    continue
                requested = child.winfo_reqwidth() + 16
                if used and used + requested > available:
                    row += 1
                    used = 0
                child.grid(row=row, column=used, columnspan=requested, sticky="w", padx=8, pady=4)
                used += requested
        bar.bind("<Configure>", reflow, add="+")
        bar._reflow = reflow
        reflow()

    def switch_view(self, view_key):
        for k, view in self.views.items():
            view.pack_forget()
            self.nav_buttons[k].configure(fg_color="transparent", text_color="#E2E8F0")

        self.views[view_key].pack(fill="both", expand=True, padx=12, pady=(10, 0))
        self.nav_buttons[view_key].configure(fg_color="#0284C7", text_color="#FFFFFF")

        # Tampilkan atau sembunyikan subcat checklist di sidebar kiri
        if view_key == "smart_cleaner":
            self.subcat_container.pack(fill="both", expand=True, padx=10, pady=0)
        else:
            self.subcat_container.pack_forget()

    # -------------------------------------------------------------
    # SUB-CATEGORY CHECKLIST (LEFT SIDEBAR)
    # -------------------------------------------------------------
    def init_subcat_checklist(self):
        self.subcat_vars = {}

        categories = [
            ("1. Browser & Windows (Biasa)", [
                ("chrome_cache", "Google Chrome Cache", True),
                ("edge_cache", "Microsoft Edge Cache", True),
                ("win_user_temp", "Windows User Temp (%TEMP%)", True),
                ("win_sys_temp", "Windows System Temp", True),
                ("win_thumbs", "Thumbnail Cache (Thumbcache)", True),
                ("win_dumps", "Crash Dumps & Error Logs", True),
                ("win_recycle", "Windows Recycle Bin", False)
            ]),
            ("2. Dev & AI Coding Caches", [
                ("pip_uv", "Pip & Astral UV Cache", True),
                ("npm_pnpm_bun", "NPM, PNPM & Bun Store", True),
                ("ai_cli_logs", "Claude, OpenCode, Codex Logs", True),
                ("ai_models", "AI Weights (HuggingFace, Torch)", True),
                ("browser_bins", "Playwright & Puppeteer Binaries", True)
            ]),
            ("3. Proyek & Dependencies", [
                ("proj_envs", "Virtual Envs (.venv, venv, env)", True),
                ("proj_modules", "Node Modules (node_modules)", True),
                ("proj_bytecode", "Python Bytecode (__pycache__)", True)
            ]),
            ("4. Registry Clean (Safe)", [
                ("reg_orphans", "Orphaned Uninstall Entries", True),
                ("reg_app_paths", "Invalid App Paths (.exe hilang)", True)
            ])
        ]

        for cat_title, items in categories:
            header_lbl = ctk.CTkLabel(
                self.subcat_scroll,
                text=cat_title,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#38BDF8"
            )
            header_lbl.pack(anchor="w", padx=4, pady=(8, 2))

            for item_id, label, default_val in items:
                v = tk.BooleanVar(value=default_val)
                self.subcat_vars[item_id] = v
                chk = ctk.CTkCheckBox(
                    self.subcat_scroll,
                    text=label,
                    variable=v,
                    font=ctk.CTkFont(size=11),
                    checkbox_width=17,
                    checkbox_height=17,
                    border_width=2
                )
                chk.pack(anchor="w", padx=12, pady=2)

        # Quick preset selection buttons
        btn_box = ctk.CTkFrame(self.subcat_scroll, fg_color="transparent")
        btn_box.pack(fill="x", padx=4, pady=(12, 5))

        btn_all = ctk.CTkButton(btn_box, text="Semua", width=65, height=24, fg_color="#334155", font=ctk.CTkFont(size=10), command=lambda: self.set_subcats(True))
        btn_all.pack(side="left", padx=2)

        btn_rec = ctk.CTkButton(btn_box, text="Default", width=65, height=24, fg_color="#334155", font=ctk.CTkFont(size=10), command=self.set_subcats_default)
        btn_rec.pack(side="left", padx=2)

        btn_none = ctk.CTkButton(btn_box, text="Batal", width=65, height=24, fg_color="#334155", font=ctk.CTkFont(size=10), command=lambda: self.set_subcats(False))
        btn_none.pack(side="left", padx=2)

    def set_subcats(self, val):
        for v in self.subcat_vars.values():
            v.set(val)

    def set_subcats_default(self):
        defaults = {
            "chrome_cache": True, "edge_cache": True, "win_user_temp": True, "win_sys_temp": True,
            "win_thumbs": True, "win_dumps": True, "win_recycle": False, "pip_uv": True,
            "npm_pnpm_bun": True, "ai_cli_logs": True, "ai_models": True, "browser_bins": True,
            "proj_envs": True, "proj_modules": True, "proj_bytecode": True, "reg_orphans": True, "reg_app_paths": True
        }
        for k, v in self.subcat_vars.items():
            v.set(defaults.get(k, True))

    # =============================================================
    # VIEW 1: SMART CLEANER (COMPACT TABLE STYLE)
    # =============================================================
    def setup_smart_cleaner_view(self):
        parent = self.views["smart_cleaner"]

        # Top Action Bar
        action_bar = ctk.CTkFrame(parent, corner_radius=8, fg_color="#18191C")
        action_bar.pack(fill="x", padx=0, pady=(0, 8))

        self.btn_smart_scan = ctk.CTkButton(
            action_bar,
            text="🔍  SMART SCAN (ANALISIS)",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            width=200,
            height=36,
            command=self.start_smart_scan_async
        )
        self.btn_smart_scan.pack(side="left", padx=12, pady=10)

        self.btn_clean_smart = ctk.CTkButton(
            action_bar,
            text="🧹  JALANKAN PEMBERSIHAN",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            width=210,
            height=36,
            command=self.confirm_and_clean_smart
        )
        self.btn_clean_smart.pack(side="left", padx=6, pady=10)

        if not hasattr(self, "startup_scan_var"):
            self.startup_scan_var = tk.BooleanVar(value=load_startup_scan_preference())
        self.chk_startup_scan = ctk.CTkCheckBox(
            action_bar,
            text="Pindai otomatis saat dibuka",
            variable=self.startup_scan_var,
            command=self._save_startup_scan_preference,
            font=ctk.CTkFont(size=11)
        )
        self.chk_startup_scan.pack(side="left", padx=8, pady=10)

        summary_panel = ctk.CTkFrame(parent, fg_color=UI_COLORS["card"])
        summary_panel.pack(fill="x", pady=(0, 8))
        # Summary has its own row, never competes with action controls.
        self.lbl_smart_summary = ctk.CTkLabel(
            summary_panel,
            text="Total sampah ditemukan: 0 B (0 items)\nTerpilih untuk dibersihkan: 0 B (0 items)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#38BDF8"
        )
        self.lbl_smart_summary.pack(anchor="w", padx=12, pady=8)

        # Compact App Mover Fixed Table Header Bar
        table_header = ctk.CTkFrame(parent, height=32, corner_radius=6, fg_color="#0F172A")
        table_header.pack(fill="x", padx=0, pady=(0, 4))
        table_header.pack_propagate(False)

        self.var_smart_master = tk.BooleanVar(value=True)
        chk_master = ctk.CTkCheckBox(
            table_header,
            text="",
            variable=self.var_smart_master,
            width=25,
            checkbox_width=18,
            checkbox_height=18,
            command=self.toggle_all_smart_rows
        )
        chk_master.grid(row=0, column=0, padx=8)
        self.smart_table_header = table_header
        for column, text in enumerate(("Nama Item / Sub-Kategori", "Detail / Lokasi Path", "Ukuran Disk", "Status"), 1):
            label = ctk.CTkLabel(table_header, text=text, font=ctk.CTkFont(size=11, weight="bold"), text_color=UI_COLORS["muted"], anchor="e" if column == 3 else "w")
            label.grid(row=0, column=column, sticky="ew", padx=4)
        self._smart_columns(table_header)

        # Scanning Progress Bar - Ditempatkan permanen dan rapi, tanpa pack/pack_forget dinamis agar tidak flickering
        self.scan_progress_frame = ctk.CTkFrame(parent, corner_radius=4, fg_color="#0F172A", height=24)
        self.scan_progress_frame.pack(fill="x", padx=0, pady=(0, 4))
        self.scan_progress_frame.pack_propagate(False)

        self.scan_progress_bar = ctk.CTkProgressBar(
            self.scan_progress_frame,
            mode="indeterminate",
            height=6,
            progress_color="#38BDF8",
            fg_color="#1E293B",
            corner_radius=3
        )
        self.scan_progress_bar.pack(side="left", fill="x", expand=True, padx=(8, 10), pady=9)
        self.scan_progress_bar.set(0)

        self.lbl_scan_status = ctk.CTkLabel(
            self.scan_progress_frame,
            text="Siap untuk analisis sistem",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        )
        self.lbl_scan_status.pack(side="right", padx=(0, 12), pady=2)

        # Scrollable Table Body (Compact Tabular Cards)
        self.smart_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.smart_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # Tampilkan kartu awal (Idle guide placeholder) saat aplikasi baru dibuka
        self._show_smart_idle_placeholder()

    def _show_smart_idle_placeholder(self):
        for w in self.smart_scroll.winfo_children():
            w.destroy()

        card = ctk.CTkFrame(self.smart_scroll, corner_radius=10, fg_color="#18191C", border_width=1, border_color="#334155")
        card.pack(fill="x", padx=10, pady=25)

        ctk.CTkLabel(
            card,
            text="✨ Selamat Datang di Smart Cleaner",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#38BDF8"
        ).pack(pady=(20, 6))

        ctk.CTkLabel(
            card,
            text="Aplikasi berada dalam mode siap (Idle). Belum ada pemindaian yang berjalan.\n"
                 "Pilih sub-kategori yang ingin dianalisis pada panel sebelah kiri, lalu klik tombol di bawah untuk memulai.",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
            justify="center"
        ).pack(padx=20, pady=6)

        ctk.CTkButton(
            card,
            text="🔍  MULAI SMART SCAN SEKARANG",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            height=38,
            width=260,
            command=self.start_smart_scan_async
        ).pack(pady=(12, 22))

    def start_smart_scan_async(self):
        if getattr(self, "active_mutation", None) is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; pemindaian Smart Scan ditunda.")
            return
        if getattr(self, "is_scanning_smart", False):
            self.log("Peringatan: Smart Scan sedang berjalan. Mohon tunggu proses selesai.")
            return

        self.is_scanning_smart = True
        self.log("Memulai Smart Scan berdasarkan sub-kategori terpilih...")
        for w in self.smart_scroll.winfo_children():
            w.destroy()
        self.smart_findings.clear()
        self.update_smart_summary()

        # Mulai animasi progress bar secara halus tanpa re-pack layout
        self.scan_progress_bar.start()
        self.lbl_scan_status.configure(text="Sedang menganalisis direktori & cache...", text_color="#38BDF8")
        self.btn_smart_scan.configure(state="disabled", text="⏳  SCANNING...")

        # Animasi teks status secara tenang tanpa log spam
        self._scan_anim_step = 0
        self._animate_scan_processing()

        categories = {key: bool(variable.get()) for key, variable in self.subcat_vars.items()}
        self.executor.submit(self._bg_smart_scan, categories)

    def _animate_scan_processing(self):
        if not getattr(self, "is_scanning_smart", False):
            return
        dots = "." * ((self._scan_anim_step % 4) + 1)
        phases = [
            "Memeriksa cache browser & direktori temp",
            "Menganalisis cache AI CLI, Claude & Node/Python",
            "Memindai direktori proyek (.venv, node_modules)",
            "Memeriksa entri registry sistem & file orphan"
        ]
        phase_text = phases[(self._scan_anim_step // 3) % len(phases)]
        try:
            self.lbl_scan_status.configure(text=f"Sedang menganalisis: {phase_text}{dots}")
        except Exception:
            pass
        self._scan_anim_step += 1
        self.after(300, self._animate_scan_processing)

    def _bg_smart_scan(self, categories):
        findings = []
        user_home = str(Path.home())
        local_app = os.getenv("LOCALAPPDATA", "")
        app_data = os.getenv("APPDATA", "")

        # 1. Browser & Windows
        if categories.get("chrome_cache", False):
            c_path = os.path.join(local_app, r"Google\Chrome\User Data\Default\Cache")
            gpu_path = os.path.join(local_app, r"Google\Chrome\User Data\Default\GPUCache")
            for p in [c_path, gpu_path]:
                if os.path.exists(p):
                    sz = get_directory_size_bytes(p)
                    findings.append({"name": "Google Chrome Cache", "path": p, "detail": "Browser Cache & GPU Data", "size_bytes": sz, "badge": "[CACHE]", "badge_color": "#0284C7", "type": "folder"})

        if categories.get("edge_cache", False):
            e_path = os.path.join(local_app, r"Microsoft\Edge\User Data\Default\Cache")
            if os.path.exists(e_path):
                sz = get_directory_size_bytes(e_path)
                findings.append({"name": "Microsoft Edge Cache", "path": e_path, "detail": "Edge Browser Cache", "size_bytes": sz, "badge": "[CACHE]", "badge_color": "#0284C7", "type": "folder"})

        if categories.get("win_user_temp", False):
            temp_p = os.getenv("TEMP", "")
            if os.path.exists(temp_p):
                sz = get_directory_size_bytes(temp_p)
                findings.append({"name": "Windows User Temp (%TEMP%)", "path": temp_p, "detail": "Temporary User Files", "size_bytes": sz, "badge": "[AMAN]", "badge_color": "#16A34A", "type": "folder_contents"})

        if categories.get("win_sys_temp", False):
            sys_temp = r"C:\Windows\Temp"
            if os.path.exists(sys_temp):
                sz = get_directory_size_bytes(sys_temp)
                findings.append({"name": "Windows System Temp", "path": sys_temp, "detail": "System Temporary Files", "size_bytes": sz, "badge": "[AMAN]", "badge_color": "#16A34A", "type": "folder_contents"})

        if categories.get("win_thumbs", False):
            exp_p = os.path.join(local_app, r"Microsoft\Windows\Explorer")
            if os.path.exists(exp_p):
                sz = sum(f.stat().st_size for f in Path(exp_p).glob("thumbcache_*.db") if f.is_file())
                if sz > 0:
                    findings.append({"name": "Thumbnail Cache (Thumbcache)", "path": exp_p, "detail": "Windows Explorer Previews", "size_bytes": sz, "badge": "[AMAN]", "badge_color": "#16A34A", "type": "thumbcache"})

        if categories.get("win_dumps", False):
            cd_p = os.path.join(local_app, "CrashDumps")
            if os.path.exists(cd_p):
                sz = get_directory_size_bytes(cd_p)
                findings.append({"name": "Crash Dumps & Error Reports", "path": cd_p, "detail": "Application Error Dumps", "size_bytes": sz, "badge": "[AMAN]", "badge_color": "#16A34A", "type": "folder_contents"})

        # 2. Dev & AI Caches
        dev_targets = [
            ("pip_uv", "Pip & UV Cache", [os.path.join(local_app, r"pip\Cache"), os.path.join(local_app, r"uv\cache")], "Python Wheel & Build Cache", "[CACHE]", "#0284C7"),
            ("npm_pnpm_bun", "NPM & Bun Store", [os.path.join(local_app, "npm-cache"), os.path.join(app_data, "npm-cache"), os.path.join(local_app, "pnpm-store"), os.path.join(user_home, r".bun\install\cache")], "JS Package Manager Storage", "[CACHE]", "#0284C7"),
            ("ai_cli_logs", "Claude, OpenCode, Codex Logs", [os.path.join(user_home, r".claude\logs"), os.path.join(user_home, r".opencode\cache"), os.path.join(user_home, r".codex\cache")], "AI CLI Prompt & Session Logs", "[AI MODEL]", "#9333EA"),
            ("ai_models", "AI Weights (HuggingFace, Torch)", [os.path.join(user_home, r".cache\huggingface"), os.path.join(user_home, r".cache\torch"), os.path.join(user_home, r".cache\whisper"), os.path.join(user_home, ".paddleocr")], "Pretrained Model Checkpoints", "[AI MODEL]", "#9333EA"),
            ("browser_bins", "Playwright & Puppeteer", [os.path.join(local_app, "ms-playwright"), os.path.join(local_app, "puppeteer")], "Automated Browser Binaries", "[CACHE]", "#0284C7")
        ]

        for flag, title, paths, desc, badge, bcolor in dev_targets:
            if categories.get(flag, False):
                for p in paths:
                    if os.path.exists(p):
                        sz = get_directory_size_bytes(p)
                        findings.append({"name": title, "path": p, "detail": desc, "size_bytes": sz, "badge": badge, "badge_color": bcolor, "type": "folder"})

        # 3. Proyek & Dependencies (.venv, node_modules)
        if any(categories.get(k, False) for k in ["proj_envs", "proj_modules", "proj_bytecode"]):
            target_patterns = []
            if categories.get("proj_envs", False):
                target_patterns.extend(["venv", ".venv", "env"])
            if categories.get("proj_modules", False):
                target_patterns.append("node_modules")
            if categories.get("proj_bytecode", False):
                target_patterns.extend(["__pycache__", ".pytest_cache"])

            # Lewati direktori sistem Windows/Appdata yang rawan hang saat traverse
            skip_dir_names = {"windows", "program files", "program files (x86)", "appdata", "$recycle.bin", "system volume information", "msocache", "recovery"}

            if os.path.exists(self.custom_project_dir):
                base_depth = self.custom_project_dir.rstrip(os.sep).count(os.sep)
                for root, dirs, _ in os.walk(self.custom_project_dir):
                    cur_depth = root.count(os.sep) - base_depth
                    if cur_depth > 5:
                        dirs.clear()
                        continue

                    # Filter direktori yang tidak perlu di-traverse
                    dirs[:] = [d for d in dirs if d.lower() not in skip_dir_names]

                    dirs_to_check = list(dirs)
                    for d in dirs_to_check:
                        d_lower = d.lower()
                        if d_lower in target_patterns:
                            full_p = os.path.join(root, d)
                            sz = get_directory_size_bytes(full_p)
                            findings.append({"name": f"Proyek: {d}", "path": full_p, "detail": f"Environment di {os.path.basename(root)}", "size_bytes": sz, "badge": "[PROYEK]", "badge_color": "#CA8A04", "type": "project_env"})
                            dirs.remove(d)

        # 4. Registry Cleaner
        if categories.get("reg_orphans", False) or categories.get("reg_app_paths", False):
            reg_items = scan_registry_orphans()
            findings.extend(item for item in reg_items
                            if (item.get("type") == "reg_uninstall" and categories.get("reg_orphans", False))
                            or (item.get("type") == "reg_app_path" and categories.get("reg_app_paths", False)))

        self.smart_findings = findings

        def _on_scan_finish():
            self.is_scanning_smart = False
            self.scan_progress_bar.stop()
            self.scan_progress_bar.set(1.0)
            self.lbl_scan_status.configure(text=f"Analisis selesai: Ditemukan {len(findings)} item", text_color="#4ADE80")
            self.btn_smart_scan.configure(state="normal", text="🔍  SMART SCAN (ANALISIS)")

            if not findings:
                lbl_empty = ctk.CTkLabel(
                    self.smart_scroll,
                    text="Tidak ada file cache atau junk yang ditemukan. Sistem Anda sudah bersih!",
                    font=ctk.CTkFont(size=13),
                    text_color="#94A3B8"
                )
                lbl_empty.pack(pady=40)
            else:
                for item in findings:
                    self._render_smart_row(item)

            total_sz = sum(it.get("size_bytes", 0) for it in findings)
            self.log(f"Smart Scan selesai. Ditemukan {len(findings)} item ({format_size(total_sz)}).")
            self.update_smart_summary()

        self.after(0, _on_scan_finish)

    @staticmethod
    def _smart_columns(container):
        for column, width, weight in ((0, 36, 0), (1, 190, 1), (2, 120, 1), (3, 100, 0), (4, 104, 0)):
            container.columnconfigure(column, minsize=width, weight=weight, uniform="flex" if weight else "")
        container.rowconfigure(0, weight=1)

    def _render_smart_row(self, item):
        row = ctk.CTkFrame(self.smart_scroll, corner_radius=4, fg_color="#18191C", height=38)
        row.pack(fill="x", padx=0, pady=2)
        row.pack_propagate(False)
        row.grid_propagate(False)
        self._smart_columns(row)

        var = tk.BooleanVar(value=True if item.get("size_bytes", 0) > 0 else False)
        item["var"] = var
        item["row_widget"] = row

        chk = ctk.CTkCheckBox(
            row,
            text="",
            variable=var,
            width=25,
            checkbox_width=18,
            checkbox_height=18,
            command=self.update_smart_summary
        )
        chk.grid(row=0, column=0, padx=8)

        lbl_name = ctk.CTkLabel(
            row,
            text=item["name"],
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
            width=220
        )
        lbl_name.grid(row=0, column=1, sticky="ew", padx=4)

        # Badge Status di Kanan
        lbl_badge = ctk.CTkLabel(
            row,
            text=item["badge"],
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=item.get("badge_color", "#0284C7"),
            corner_radius=4,
            text_color="#FFFFFF",
            width=85,
            height=22
        )
        lbl_badge.grid(row=0, column=4, sticky="ew", padx=4)

        # Ukuran Disk
        sz_str = format_size(item.get("size_bytes", 0))
        lbl_size = ctk.CTkLabel(
            row,
            text=sz_str,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8",
            width=90,
            anchor="e"
        )
        lbl_size.grid(row=0, column=3, sticky="ew", padx=4)

        # Path (Truncated)
        p_str = item.get("path", "")
        if len(p_str) > 48:
            p_str = p_str[:22] + "..." + p_str[-23:]
        lbl_path = ctk.CTkLabel(
            row,
            text=p_str,
            font=ctk.CTkFont(size=11),
            text_color="#94A3B8",
            anchor="e"
        )
        lbl_path.grid(row=0, column=2, sticky="ew", padx=4)
        lbl_path.bind("<Button-1>", lambda event: messagebox.showinfo("Lokasi lengkap", item.get("path", "")))

    def toggle_all_smart_rows(self):
        val = self.var_smart_master.get()
        for it in self.smart_findings:
            if "var" in it and it["var"] is not None:
                it["var"].set(val)
        self.update_smart_summary()

    def update_smart_summary(self):
        total_found = sum(it.get("size_bytes", 0) for it in self.smart_findings)
        total_selected = sum(it.get("size_bytes", 0) for it in self.smart_findings if it.get("var") and it["var"].get())
        sel_count = sum(1 for it in self.smart_findings if it.get("var") and it["var"].get())
        self.lbl_smart_summary.configure(
            text=f"Total sampah ditemukan: {format_size(total_found)} ({len(self.smart_findings)} items)\nTerpilih untuk dibersihkan: {format_size(total_selected)} ({sel_count} items)"
        )

    def confirm_and_clean_smart(self):
        if not self.acquire_mutation_guard("smart_clean"):
            return
        selected = [it for it in self.smart_findings if it.get("var") and it["var"].get()]
        if not selected:
            self.release_mutation_guard()
            messagebox.showinfo("Informasi", "Pilih minimal satu item untuk dibersihkan.")
            return

        total_sz = sum(it.get("size_bytes", 0) for it in selected)
        msg = f"Anda akan membersihkan {len(selected)} item ({format_size(total_sz)}).\n\n" \
              f"• File cache akan dibersihkan secara aman.\n" \
              f"• Folder proyek (.venv/node_modules) dipindah ke Recycle Bin.\n" \
              f"• Entri registry akan di-backup otomatis (.reg) sebelum dihapus.\n\n" \
              f"Lanjutkan pembersihan?"
        if not messagebox.askyesno("Konfirmasi Pembersihan Smart", msg):
            self.release_mutation_guard()
            return

        self.btn_clean_smart.configure(state="disabled", text="Membersihkan...")
        try:
            self.executor.submit(self._bg_clean_smart, selected)
        except Exception as e:
            self.release_mutation_guard()
            self.btn_clean_smart.configure(state="normal", text="🧹  JALANKAN PEMBERSIHAN")
            self.log(f"Gagal menjalankan thread pembersihan: {e}")

    def _bg_clean_smart(self, items):
        freed = 0
        cleaned_count = 0
        successful_items = []
        reg_items_to_backup = [it for it in items if "reg" in it.get("type", "")]
        backup_path = create_registry_backup(reg_items_to_backup, self.log) if reg_items_to_backup else None
        if reg_items_to_backup and not backup_path:
            self.log("Gagal membuat backup registry; entri registry terpilih dipertahankan.")

        for it in items:
            itype = it.get("type", "")
            ipath = it.get("path", "")
            isz = it.get("size_bytes", 0)
            item_succeeded = False

            try:
                if itype == "thumbcache":
                    if os.path.exists(ipath):
                        files = list(Path(ipath).glob("thumbcache_*.db"))
                        for file_path in files:
                            if file_path.is_file():
                                os.remove(str(file_path))
                        item_succeeded = all(not file_path.exists() for file_path in files)

                elif itype in ("folder", "folder_contents"):
                    if os.path.exists(ipath):
                        for entry in os.scandir(ipath):
                            if entry.is_file(follow_symlinks=False):
                                os.remove(entry.path)
                            elif entry.is_dir(follow_symlinks=False):
                                shutil.rmtree(entry.path)
                        item_succeeded = not any(os.scandir(ipath))

                elif itype == "project_env":
                    if os.path.exists(ipath):
                        send2trash(ipath)
                        item_succeeded = not os.path.exists(ipath)

                elif "reg" in itype and backup_path:
                    root_h = it.get("root")
                    sub_p = it.get("sub_path")
                    if root_h and sub_p:
                        parent_p, key_to_del = sub_p.rsplit("\\", 1)
                        with winreg.OpenKey(root_h, parent_p, 0, winreg.KEY_WRITE) as parent:
                            winreg.DeleteKey(parent, key_to_del)
                        try:
                            with winreg.OpenKey(root_h, sub_p, 0, winreg.KEY_READ):
                                pass
                        except FileNotFoundError:
                            item_succeeded = True

                if item_succeeded:
                    successful_items.append(it)
                    freed += isz
                    cleaned_count += 1
                    self.log(f"Berhasil dibersihkan: {it.get('name', ipath)}")
                else:
                    self.log(f"Item dipertahankan karena gagal/tidak terverifikasi: {it.get('name', ipath)}")
            except Exception as e:
                self.log(f"Peringatan saat membersihkan {it.get('name')}: {e}")

        self.log(f"Pembersihan selesai! {cleaned_count} item dibersihkan. Ruang dibebaskan: ~{format_size(freed)}")

        def _update_ui_after_clean():
            try:
                self.btn_clean_smart.configure(state="normal", text="🧹  JALANKAN PEMBERSIHAN")
                cleaned_set = {id(it) for it in successful_items}
                remaining_findings = []
                for it in self.smart_findings:
                    if id(it) in cleaned_set:
                        w = it.get("row_widget")
                        if w and w.winfo_exists():
                            w.destroy()
                    else:
                        remaining_findings.append(it)
                self.smart_findings = remaining_findings
                self.update_smart_summary()
                if not self.smart_findings:
                    lbl_empty = ctk.CTkLabel(
                        self.smart_scroll,
                        text="Semua item terpilih telah dibersihkan. Sistem Anda bersih!",
                        font=ctk.CTkFont(size=13),
                        text_color="#4ADE80"
                    )
                    lbl_empty.pack(pady=40)
            finally:
                self.release_mutation_guard()

        self.after(0, _update_ui_after_clean)

    # =============================================================
    # VIEW 2: APP MOVER & RESTORE (COMPACT TABLE STYLE)
    # =============================================================
    def setup_app_mover_view(self):
        parent = self.views["app_mover"]

        # Control Bar
        ctrl_bar = ctk.CTkFrame(parent, corner_radius=8, fg_color="#18191C")
        ctrl_bar.pack(fill="x", padx=0, pady=(0, 8))

        self.mover_mode_seg = ctk.CTkSegmentedButton(
            ctrl_bar,
            values=["Pindahkan Aplikasi (C: -> D:)", "Kembalikan Aplikasi (Restore)"],
            command=self.toggle_mover_view
        )
        self.mover_mode_seg.set("Pindahkan Aplikasi (C: -> D:)")
        self.mover_mode_seg.pack(side="left", padx=12, pady=10)

        # Target Drive ComboBox
        ctk.CTkLabel(ctrl_bar, text="Target:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(15, 5))
        drive_opts = get_target_drive_options()
        opt_names = [o[0] for o in drive_opts] if drive_opts else ["D:\\DevApps"]
        self.target_paths_map = {o[0]: o[1] for o in drive_opts} if drive_opts else {"D:\\DevApps": "D:\\DevApps"}

        self.cmb_target_drive = ctk.CTkComboBox(ctrl_bar, values=opt_names, width=220)
        self.cmb_target_drive.set(opt_names[0])
        self.cmb_target_drive.pack(side="left", padx=5)

        btn_browse = ctk.CTkButton(ctrl_bar, text="Folder...", width=75, fg_color="#334155", command=self.browse_custom_target_root)
        btn_browse.pack(side="left", padx=4)

        self.btn_scan_apps = ctk.CTkButton(ctrl_bar, text="Pindai Aplikasi", width=120, fg_color="#0284C7", command=self.scan_installed_apps_async)
        self.btn_scan_apps.pack(side="left", padx=8)

        self.btn_move_apps = ctk.CTkButton(
            ctrl_bar,
            text="Pindahkan Terpilih (Junction)",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.confirm_and_move_selected
        )
        self.btn_move_apps.pack(side="right", padx=12, pady=10)

        # Compact Table Header Bar for App Mover
        app_header = ctk.CTkFrame(parent, height=32, corner_radius=6, fg_color="#0F172A")
        app_header.pack(fill="x", padx=0, pady=(0, 4))
        app_header.pack_propagate(False)

        self.var_app_master = tk.BooleanVar(value=False)
        chk_app_master = ctk.CTkCheckBox(app_header, text="", variable=self.var_app_master, width=25, checkbox_width=18, checkbox_height=18, command=self.toggle_all_app_rows)
        chk_app_master.pack(side="left", padx=(10, 5))

        ctk.CTkLabel(app_header, text="Nama Aplikasi", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=10)
        ctk.CTkLabel(app_header, text="Status Kelayakan", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=(5, 15))
        ctk.CTkLabel(app_header, text="Ukuran Disk", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=25)
        ctk.CTkLabel(app_header, text="Path Asal (C:)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=40)

        # Main Move Scroll Frame
        self.move_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.move_scroll.pack(fill="both", expand=True)

        # Restore Container (Hidden initially)
        self.restore_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.restore_scroll = ctk.CTkScrollableFrame(self.restore_frame, fg_color="transparent")
        self.restore_scroll.pack(fill="both", expand=True)

    def toggle_mover_view(self, choice):
        if "Pindahkan" in choice:
            self.restore_frame.pack_forget()
            self.move_scroll.pack(fill="both", expand=True)
            self.btn_move_apps._toolbar_hidden = False
            self.btn_move_apps.master._reflow()
        else:
            self.move_scroll.pack_forget()
            self.btn_move_apps._toolbar_hidden = True
            self.btn_move_apps.grid_remove()
            self.btn_move_apps.master._reflow()
            self.restore_frame.pack(fill="both", expand=True)
            self.refresh_restore_list()

    def browse_custom_target_root(self):
        chosen = filedialog.askdirectory(title="Pilih Folder Root Tujuan di Drive Non-C (Contoh: D:\\DevApps)")
        if chosen:
            if chosen.upper().startswith("C:"):
                messagebox.showwarning("Peringatan", "Folder tujuan harus berada di luar drive C:!")
                return
            label = f"{chosen} (Custom)"
            self.target_paths_map[label] = chosen
            self.cmb_target_drive.configure(values=list(self.target_paths_map.keys()))
            self.cmb_target_drive.set(label)

    def get_selected_target_root(self):
        cur = self.cmb_target_drive.get()
        return self.target_paths_map.get(cur, cur.split(" ")[0])

    def test_app_safety(self, name, path):
        path_lower = path.lower()
        if not path_lower.startswith("c:"):
            return False, "Bukan di Drive C:"
        for sys_dir in [r'c:\windows', r'c:\program files\common files', r'c:\program files (x86)\common files']:
            if path_lower.startswith(sys_dir):
                return False, "Sistem Windows / Core"
        for pat in BLOCKED_APP_PATTERNS:
            if re.search(pat, name, re.IGNORECASE) or re.search(pat, path, re.IGNORECASE):
                return False, "Komponen Kritis / Driver / Shell"
        return True, "AMAN / SIAP DIPINDAH"

    def scan_installed_apps_async(self):
        if getattr(self, "active_mutation", None) is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; pemindaian aplikasi ditunda.")
            return
        if getattr(self, "is_scanning_apps", False):
            self.log("Peringatan: Pemindaian aplikasi sedang berjalan. Mohon tunggu...")
            return
        self.is_scanning_apps = True
        if hasattr(self, "btn_scan_apps"):
            self.btn_scan_apps.configure(state="disabled", text="Memindai...")

        self.log("Memindai daftar aplikasi terinstal di drive C:...")
        for w in self.move_scroll.winfo_children():
            w.destroy()
        self.app_items.clear()
        self.executor.submit(self._bg_scan_apps)

    def _bg_scan_apps(self):
        try:
            apps = []
            roots = [
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
            ]

            seen_paths = set()
            history = load_moves_history()
            moved_orig_paths = set(h.get("original_path", "").strip().lower() for h in history if h.get("original_path"))

            for root_h, sub in roots:
                try:
                    k = winreg.OpenKey(root_h, sub)
                    for i in range(winreg.QueryInfoKey(k)[0]):
                        try:
                            subname = winreg.EnumKey(k, i)
                            sk = winreg.OpenKey(k, subname)
                            try:
                                name, _ = winreg.QueryValueEx(sk, "DisplayName")
                                loc = ""
                                try:
                                    loc, _ = winreg.QueryValueEx(sk, "InstallLocation")
                                    loc = loc.strip('"').strip()
                                except OSError:
                                    pass

                                uninst = ""
                                try:
                                    uninst, _ = winreg.QueryValueEx(sk, "UninstallString")
                                    uninst = uninst.strip()
                                except OSError:
                                    pass

                                found_dir = None
                                if loc and os.path.exists(loc) and loc.lower().startswith("c:"):
                                    found_dir = loc
                                elif uninst:
                                    m = re.search(r'"([^"]+\.exe)"', uninst)
                                    if m and os.path.exists(m.group(1)):
                                        d = os.path.dirname(m.group(1))
                                        if os.path.exists(d) and d.lower().startswith("c:"):
                                            found_dir = d
                                    else:
                                        p = uninst.split()[0].strip('"')
                                        if os.path.exists(p) and p.lower().endswith(".exe"):
                                            d = os.path.dirname(p)
                                            if os.path.exists(d) and d.lower().startswith("c:"):
                                                found_dir = d

                                if found_dir:
                                    raw_norm = os.path.normpath(found_dir).lower()
                                    # 1. Cek apakah path C: ini sendiri adalah NTFS junction
                                    if is_junction(found_dir):
                                        continue
                                    # 2. Cek apakah sudah ada dalam catatan pemindahan
                                    if raw_norm in moved_orig_paths:
                                        continue

                                    loc_resolved = str(Path(found_dir).resolve())
                                    loc_lower = loc_resolved.lower()
                                    # 3. Cek apakah setelah di-resolve mengarah ke target lain atau sudah tercatat
                                    if loc_lower in moved_orig_paths or raw_norm in seen_paths or loc_lower in seen_paths:
                                        continue
                                    seen_paths.add(raw_norm)
                                    seen_paths.add(loc_lower)

                                    is_safe, reason = self.test_app_safety(name, found_dir)
                                    sz = get_directory_size_bytes(found_dir)
                                    if sz > 1024 * 1024:  # > 1 MB
                                        item = {
                                            "name": name,
                                            "path": found_dir,
                                            "size_bytes": sz,
                                            "is_safe": is_safe,
                                            "reason": reason,
                                            "var": None
                                        }
                                        apps.append(item)
                                        self._render_app_row(item)
                            except OSError:
                                pass
                        except OSError:
                            pass
                except Exception:
                    pass

            self.app_items = apps
            self.log(f"Pemindaian aplikasi selesai. Ditemukan {len(apps)} aplikasi di drive C:.")
        finally:
            self.is_scanning_apps = False
            if hasattr(self, "btn_scan_apps"):
                self.after(0, lambda: self.btn_scan_apps.configure(state="normal", text="Pindai Aplikasi"))

    def _render_app_row(self, item):
        def _render():
            row = ctk.CTkFrame(self.move_scroll, corner_radius=4, fg_color="#18191C", height=38)
            row.pack(fill="x", padx=0, pady=2)
            row.pack_propagate(False)

            var = tk.BooleanVar(value=False)
            item["var"] = var
            item["row_widget"] = row

            chk = ctk.CTkCheckBox(row, text="", variable=var, width=25, checkbox_width=18, checkbox_height=18)
            if not item["is_safe"]:
                chk.configure(state="disabled")
            chk.pack(side="left", padx=(10, 5))

            lbl_name = ctk.CTkLabel(row, text=item["name"], font=ctk.CTkFont(size=12, weight="bold"), anchor="w", width=220)
            lbl_name.pack(side="left", padx=5)

            # Badge Status
            badge_text = "[SIAP DIPINDAH]" if item["is_safe"] else "[DILINDUNGI]"
            badge_color = "#16A34A" if item["is_safe"] else "#DC2626"
            lbl_badge = ctk.CTkLabel(row, text=badge_text, font=ctk.CTkFont(size=10, weight="bold"), fg_color=badge_color, corner_radius=4, text_color="#FFFFFF", width=110, height=22)
            lbl_badge.pack(side="right", padx=(5, 12))

            # Ukuran
            lbl_sz = ctk.CTkLabel(row, text=format_size(item["size_bytes"]), font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8", width=90, anchor="e")
            lbl_sz.pack(side="right", padx=15)

            # Path
            p_str = item["path"]
            if len(p_str) > 45:
                p_str = p_str[:20] + "..." + p_str[-22:]
            lbl_p = ctk.CTkLabel(row, text=p_str, font=ctk.CTkFont(size=11), text_color="#94A3B8", anchor="e")
            lbl_p.pack(side="right", padx=15)

        self.after(0, _render)

    def toggle_all_app_rows(self):
        val = self.var_app_master.get()
        for it in self.app_items:
            if it.get("is_safe") and it.get("var"):
                it["var"].set(val)

    def confirm_and_move_selected(self):
        if not self.acquire_mutation_guard("app_move"):
            return
        if not is_user_admin():
            self.release_mutation_guard()
            messagebox.showerror(
                "Memerlukan Akses Administrator",
                "Memindahkan aplikasi dari folder sistem C:\\Program Files dan membuat NTFS Directory Junction (mklink /J) "
                "memerlukan hak Administrator.\n\n"
                "Silakan restart aplikasi ini dengan klik kanan -> 'Run as administrator'."
            )
            return

        selected = [it for it in self.app_items if it.get("var") and it["var"].get() and it.get("is_safe")]
        if not selected:
            self.release_mutation_guard()
            messagebox.showinfo("Informasi", "Pilih minimal satu aplikasi aman untuk dipindahkan.")
            return

        target_root = self.get_selected_target_root()
        total_sz = sum(it["size_bytes"] for it in selected)

        # Space Check di Target
        try:
            drive_letter = os.path.splitdrive(target_root)[0]
            usage = psutil.disk_usage(drive_letter + "\\")
            if usage.free < (total_sz + 1024 * 1024 * 1024):  # buffer 1 GB
                self.release_mutation_guard()
                messagebox.showerror("Error Ruang Disk", f"Ruang disk di {drive_letter} tidak mencukupi!\nDibutuhkan: {format_size(total_sz + 1024*1024*1024)}\nTersedia: {format_size(usage.free)}")
                return
        except Exception:
            pass

        msg = f"Anda akan memindahkan {len(selected)} aplikasi ({format_size(total_sz)}) ke:\n{target_root}\n\n" \
              f"• File akan disalin menggunakan Robocopy.\n" \
              f"• Folder asal di C: akan digantikan dengan NTFS Directory Junction (mklink /J).\n" \
              f"• Aplikasi tidak akan crash dan shortcut tetap bekerja normal.\n\n" \
              f"Lanjutkan pemindahan?"
        if not messagebox.askyesno("Konfirmasi Pindah Aplikasi", msg):
            self.release_mutation_guard()
            return

        self.btn_move_apps.configure(state="disabled", text="Memindahkan...")
        try:
            self.executor.submit(self._bg_move_apps, selected, target_root)
        except Exception as e:
            self.release_mutation_guard()
            self.btn_move_apps.configure(state="normal", text="Pindahkan Terpilih (Junction)")
            self.log(f"Gagal menjalankan thread pemindahan aplikasi: {e}")

    def _bg_move_apps(self, items, target_root):
        moved_success = []
        try:
            os.makedirs(target_root, exist_ok=True)
            for item in items:
                src = item["path"]
                dest = os.path.join(target_root, os.path.basename(os.path.normpath(src)))
                stage = None
                backup_container = None
                backup = None
                committed = False
                try:
                    if not os.path.isdir(src) or is_junction(src) or os.path.islink(src):
                        raise OSError("Folder asal tidak valid atau sudah berupa junction.")
                    if os.path.lexists(dest):
                        raise OSError(f"Tujuan sudah ada; tidak ditimpa: {dest}")
                    try:
                        common = os.path.commonpath([os.path.realpath(src), os.path.realpath(target_root)])
                    except ValueError:
                        common = None
                    if common in (os.path.realpath(src), os.path.realpath(dest)):
                        raise OSError("Folder tujuan tidak boleh bersarang dengan asal.")
                    stop_processes_in_folder(src)
                    before = directory_manifest(src)
                    stage = tempfile.mkdtemp(prefix=".mover-copy-", dir=target_root)
                    result = subprocess.run(
                        ["robocopy", src, stage, "/E", "/COPY:DAT", "/DCOPY:DAT", "/R:3", "/W:1", "/NP", "/NFL", "/NDL", "/XJ"],
                        capture_output=True, text=True, timeout=3600,
                        creationflags=hidden_console_creation_flags())
                    if not 0 <= result.returncode < 8:
                        raise OSError(f"Robocopy gagal ({result.returncode}): {result.stderr or result.stdout}")
                    if directory_manifest(stage) != before or directory_manifest(src) != before:
                        raise OSError("Isi salinan tidak cocok atau folder asal berubah.")
                    os.rename(stage, dest)
                    stage = None
                    backup_container = tempfile.mkdtemp(prefix=".mover-backup-", dir=os.path.dirname(src))
                    backup = os.path.join(backup_container, "original")
                    os.rename(src, backup)
                    result = subprocess.run(["cmd", "/c", "mklink", "/J", src, dest],
                                            capture_output=True, text=True,
                                            creationflags=hidden_console_creation_flags())
                    if result.returncode != 0 or not is_junction(src) or not os.path.samefile(src, dest):
                        raise OSError(f"Junction belum terverifikasi: {result.stderr or result.stdout}")
                    if directory_manifest(backup) != before or directory_manifest(dest) != before:
                        raise OSError("Isi aplikasi berubah selama pemindahan.")
                    history = [record for record in load_moves_history() if record.get("original_path") != src]
                    history.append({"name": item["name"], "original_path": src,
                                    "target_path": dest, "size_bytes": item["size_bytes"],
                                    "date": time.strftime("%Y-%m-%d %H:%M:%S")})
                    save_moves_history(history)
                    committed = True
                    shutil.rmtree(backup)
                    backup = None
                    moved_success.append(item)
                    self.log(f"SUKSES: {item['name']} dipindahkan; isi dan junction terverifikasi.")
                except Exception as error:
                    self.log(f"Pemindahan {item['name']} belum selesai: {error}")
                    if backup and os.path.isdir(backup) and not committed:
                        try:
                            if os.path.lexists(src):
                                if not is_junction(src) or not os.path.samefile(src, dest):
                                    raise OSError("Lokasi asal berubah; rollback otomatis dibatalkan.")
                                os.rmdir(src)
                            os.rename(backup, src)
                            backup = None
                            self.log(f"Folder asal dipulihkan: {src}. Salinan tujuan dipertahankan di {dest}.")
                        except Exception as rollback_error:
                            self.log(f"ERROR rollback: {rollback_error}. Backup dipertahankan di {backup}.")
                finally:
                    if stage:
                        try:
                            shutil.rmtree(stage)
                        except OSError as error:
                            self.log(f"Staging dipertahankan di {stage}: {error}")
                    if backup_container and backup is None:
                        try:
                            os.rmdir(backup_container)
                        except OSError as error:
                            self.log(f"Folder backup dipertahankan di {backup_container}: {error}")
        except Exception as error:
            self.log(f"Gagal memulai pemindahan: {error}")
        finally:
            def _finish_move():
                try:
                    successful_ids = {id(item) for item in moved_success}
                    self.app_items = [item for item in self.app_items if id(item) not in successful_ids]
                    for item in moved_success:
                        row = item.get("row_widget")
                        if row and row.winfo_exists():
                            row.destroy()
                    self.btn_move_apps.configure(state="normal", text="Pindahkan Terpilih (Junction)")
                    self.refresh_restore_list()
                finally:
                    self.release_mutation_guard()
            self.after(0, _finish_move)

    def refresh_restore_list(self):
        for w in self.restore_scroll.winfo_children():
            w.destroy()

        history = load_moves_history()
        if not history:
            lbl_empty = ctk.CTkLabel(self.restore_scroll, text="Belum ada aplikasi yang dipindahkan menggunakan App Mover.", font=ctk.CTkFont(size=13))
            lbl_empty.pack(pady=40)
            return

        for record in history:
            row = ctk.CTkFrame(self.restore_scroll, corner_radius=6, fg_color="#18191C", height=50)
            row.pack(fill="x", padx=0, pady=4)
            row.pack_propagate(False)

            is_junc = is_junction(record["original_path"])
            status_text = "[Junction Aktif]" if is_junc else "[Junction Terputus]"
            status_color = "#16A34A" if is_junc else "#DC2626"
            pending_cleanup = record.get("phase") == "restored_pending_cleanup"
            if pending_cleanup:
                status_text = "[Dipulihkan — pembersihan tertunda]"
                status_color = "#EA580C"

            lbl_name = ctk.CTkLabel(row, text=record["name"], font=ctk.CTkFont(size=13, weight="bold"), anchor="w", width=220)
            lbl_name.pack(side="left", padx=15)

            btn_res = ctk.CTkButton(
                row,
                text="Coba Bersihkan Target" if pending_cleanup else "Kembalikan (Restore)",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#0284C7",
                hover_color="#0369A1",
                width=140,
                height=30,
                command=lambda r=record: self.confirm_and_restore_app(r)
            )
            btn_res.pack(side="right", padx=15)

            lbl_sz = ctk.CTkLabel(row, text=format_size(record.get("size_bytes", 0)), font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8", width=90, anchor="e")
            lbl_sz.pack(side="right", padx=15)

            lbl_st = ctk.CTkLabel(row, text=status_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=status_color, width=130)
            lbl_st.pack(side="right", padx=15)

    def confirm_and_restore_app(self, record):
        if not self.acquire_mutation_guard("app_restore"):
            return
        if not is_user_admin():
            self.release_mutation_guard()
            messagebox.showerror(
                "Memerlukan Akses Administrator",
                "Mengembalikan aplikasi ke C:\\ dan melepas NTFS Junction memerlukan hak Administrator.\n\n"
                "Silakan restart aplikasi ini dengan klik kanan -> 'Run as administrator'."
            )
            return

        orig = record["original_path"]
        target = record["target_path"]
        sz = record.get("size_bytes", 0)

        if record.get("phase") == "restored_pending_cleanup":
            if messagebox.askyesno("Pembersihan Restore", f"Coba bersihkan salinan target '{record['name']}'?\nFolder asal akan diverifikasi ulang sebelum penghapusan."):
                try:
                    self.executor.submit(self._bg_retry_restore_cleanup, record)
                except Exception as e:
                    self.release_mutation_guard()
                    self.log(f"Gagal menjalankan pembersihan retry: {e}")
            else:
                self.release_mutation_guard()
            return

        # Space Check di C:
        try:
            usage = psutil.disk_usage("C:\\")
            if usage.free < (sz + 1024 * 1024 * 1024):
                self.release_mutation_guard()
                messagebox.showerror("Error", f"Drive C: tidak memiliki ruang cukup untuk restore!\nDibutuhkan: {format_size(sz + 1024*1024*1024)}\nTersedia: {format_size(usage.free)}")
                return
        except Exception:
            pass

        if not messagebox.askyesno("Konfirmasi Restore", f"Kembalikan '{record['name']}' ke drive C: ({orig})?"):
            self.release_mutation_guard()
            return

        try:
            self.executor.submit(self._bg_restore_app, record)
        except Exception as e:
            self.release_mutation_guard()
            self.log(f"Gagal menjalankan restore: {e}")

    def _bg_retry_restore_cleanup(self, record):
        try:
            history = load_moves_history()
            matches = [entry for entry in history
                       if entry.get("original_path") == record.get("original_path")]
            if len(matches) != 1 or matches[0] != record:
                raise OSError("Catatan recovery berubah; buka ulang daftar pemulihan.")
            pending = matches[0]
            if pending.get("phase") != "restored_pending_cleanup" or "manifest" not in pending:
                raise OSError("Catatan pembersihan tertunda tidak valid.")
            cleanup_verified_copy(pending["original_path"], pending["target_path"], pending["manifest"])
            save_moves_history([entry for entry in history if entry is not pending])
        except Exception as error:
            self.log(f"Pembersihan restore masih tertunda: {error}. Catatan recovery dipertahankan.")
            return
        finally:
            self.release_mutation_guard()
        self.log(f"Pembersihan restore selesai: {record['name']}.")
        self.after(0, self.refresh_restore_list)

    def _bg_restore_app(self, record):
        orig = record["original_path"]
        target = record["target_path"]
        self.log(f"Memulai proses restore: {record['name']}...")

        stage_path = None
        junction_removed = False
        cleanup_pending = False
        try:
            if not os.path.isdir(target) or is_junction(target) or os.path.islink(target):
                raise OSError("Folder target restore tidak valid.")
            if os.path.lexists(orig):
                if not is_junction(orig) or not os.path.samefile(orig, target):
                    raise OSError("Lokasi asal bukan junction ke target yang tercatat.")
            try:
                common = os.path.commonpath([os.path.abspath(orig), os.path.abspath(target)])
            except ValueError:
                common = None  # Different drives cannot contain one another.
            if common in (os.path.abspath(orig), os.path.abspath(target)):
                raise OSError("Lokasi asal dan target tidak boleh saling bersarang.")
            stop_processes_in_folder(orig)
            stop_processes_in_folder(target)
            before = directory_manifest(target)
            stage_path = tempfile.mkdtemp(prefix=".mover-restore-", dir=os.path.dirname(orig))
            cmd = ["robocopy", target, stage_path, "/E", "/COPY:DAT", "/DCOPY:DAT", "/R:3", "/W:1", "/NP", "/NFL", "/NDL", "/XJ"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=3600,
                                 creationflags=hidden_console_creation_flags())
            if not 0 <= res.returncode < 8:
                raise OSError(f"Robocopy restore gagal (Exit code {res.returncode})")
            if before != directory_manifest(stage_path) or before != directory_manifest(target):
                raise OSError("Isi salinan restore tidak cocok atau target berubah; restore dibatalkan.")
            if os.path.lexists(orig):
                if not is_junction(orig) or not os.path.samefile(orig, target):
                    raise OSError("Lokasi asal berubah selama restore.")
                os.rmdir(orig)
                junction_removed = True
            try:
                os.rename(stage_path, orig)
                stage_path = None
            except OSError:
                if junction_removed and not os.path.lexists(orig):
                    rollback = subprocess.run(["cmd", "/c", "mklink", "/J", orig, target],
                                              capture_output=True, text=True,
                                              creationflags=hidden_console_creation_flags())
                    if rollback.returncode != 0 or not is_junction(orig) or not os.path.samefile(orig, target):
                        self.log(f"ERROR: Rollback junction gagal. Data tetap tersedia di {target}.")
                raise
            history = [h for h in load_moves_history() if h.get("original_path") != orig]
            pending = dict(record, phase="restored_pending_cleanup", manifest=before)
            # Persist recovery bookkeeping before removing the redundant target copy.
            try:
                save_moves_history(history + [pending])
                cleanup_pending = True
            except Exception:
                # Only roll back the copy we installed, never a changed application folder.
                if (not is_junction(orig) and not os.path.islink(orig)
                        and directory_manifest(orig) == before
                        and directory_manifest(target) == before):
                    stage_path = tempfile.mkdtemp(prefix=".mover-restore-", dir=os.path.dirname(orig))
                    os.rmdir(stage_path)
                    os.rename(orig, stage_path)
                    if junction_removed:
                        rollback = subprocess.run(["cmd", "/c", "mklink", "/J", orig, target],
                                                  capture_output=True, text=True, timeout=30,
                                                  creationflags=hidden_console_creation_flags())
                        if (rollback.returncode != 0 or not is_junction(orig)
                                or not os.path.samefile(orig, target)):
                            self.log(f"ERROR: Rollback junction gagal. Data tetap tersedia di {target}.")
                else:
                    self.log(f"Lokasi asal berubah; pemulihan manual diperlukan: {orig}. Target disimpan: {target}.")
                raise
            cleanup_verified_copy(orig, target, before)
            save_moves_history(history)
        except Exception as error:
            self.log(f"Restore belum selesai: {error}. Data pemulihan dipertahankan.")
            if cleanup_pending:
                self.after(0, self.refresh_restore_list)
            self.release_mutation_guard()
            return
        finally:
            if stage_path is not None:
                try:
                    shutil.rmtree(stage_path)
                except OSError as error:
                    self.log(f"Staging restore dipertahankan di {stage_path}: {error}")

        def _finish_restore():
            try:
                if not any(item.get("path") == orig for item in self.app_items):
                    safe, reason = self.test_app_safety(record["name"], orig)
                    item = {"name": record["name"], "path": orig,
                            "size_bytes": record.get("size_bytes", 0),
                            "is_safe": safe, "reason": reason, "var": None}
                    self.app_items.append(item)
                    self._render_app_row(item)
                self.refresh_restore_list()
            finally:
                self.release_mutation_guard()
        self.log(f"SUKSES: {record['name']} berhasil dikembalikan dan isi salinan terverifikasi.")
        self.after(0, _finish_restore)

    # =============================================================
    # VIEW 3: PYTHON LIBRARY MANAGER (COMPACT TABLE STYLE)
    # =============================================================
    def setup_py_libs_view(self):
        parent = self.views["py_libs"]

        # Control Bar
        ctrl_bar = ctk.CTkFrame(parent, corner_radius=8, fg_color="#18191C")
        ctrl_bar.pack(fill="x", padx=0, pady=(0, 8))

        # Python Environment Selector Dropdown
        ctk.CTkLabel(ctrl_bar, text="Environment:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(12, 4))
        self.py_envs = discover_python_environments()
        env_labels = list(self.py_envs.keys()) if self.py_envs else ["Python System"]
        self.cmb_py_env = ctk.CTkComboBox(ctrl_bar, values=env_labels, width=190, command=lambda _: self.scan_libs_async())
        if env_labels:
            self.cmb_py_env.set(env_labels[0])
        self.cmb_py_env.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl_bar, text="Cari:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(8, 4))
        self.ent_lib_search = ctk.CTkEntry(ctrl_bar, placeholder_text="Ketik nama library...", width=160)
        self.ent_lib_search.pack(side="left", padx=4)
        self.ent_lib_search.bind("<KeyRelease>", self.filter_libs)

        self.btn_scan_libs = ctk.CTkButton(ctrl_bar, text="Pindai Ulang Library", width=140, fg_color="#0284C7", command=self.scan_libs_async)
        self.btn_scan_libs.pack(side="left", padx=8)

        self.btn_uninstall_libs = ctk.CTkButton(
            ctrl_bar,
            text="Uninstall Terpilih",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.confirm_and_uninstall_libs
        )
        self.btn_uninstall_libs.pack(side="right", padx=12, pady=10)

        # Compact Table Header Bar
        lib_header = ctk.CTkFrame(parent, height=32, corner_radius=6, fg_color="#0F172A")
        lib_header.pack(fill="x", padx=0, pady=(0, 4))
        lib_header.pack_propagate(False)

        self.var_lib_master = tk.BooleanVar(value=False)
        chk_lib_master = ctk.CTkCheckBox(lib_header, text="", variable=self.var_lib_master, width=25, checkbox_width=18, checkbox_height=18, command=self.toggle_all_lib_rows)
        chk_lib_master.pack(side="left", padx=(10, 5))

        ctk.CTkLabel(lib_header, text="Nama Package & Versi", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=10)
        ctk.CTkLabel(lib_header, text="Status Dependensi (Required By)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=(5, 15))
        ctk.CTkLabel(lib_header, text="Ukuran Disk", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=30)

        self.lib_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.lib_scroll.pack(fill="both", expand=True)

    def scan_libs_async(self):
        if getattr(self, "active_mutation", None) is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; pemindaian library ditunda.")
            return
        if getattr(self, "is_scanning_libs", False):
            self.log("Peringatan: Pemindaian library sedang berjalan. Mohon tunggu...")
            return
        target_python = self._get_active_python_exe()
        if not target_python:
            self.log("Interpreter terpilih tidak ditemukan; pilih environment yang valid.")
            return
        self.is_scanning_libs = True
        if hasattr(self, "btn_scan_libs"):
            self.btn_scan_libs.configure(state="disabled", text="Memindai...")

        self.log("Memindai Python packages dan menghitung ukuran di disk...")
        self.executor.submit(self._bg_scan_libs, target_python)

    def _get_active_python_exe(self):
        if hasattr(self, "cmb_py_env") and hasattr(self, "py_envs"):
            sel = self.cmb_py_env.get()
            exe = self.py_envs.get(sel)
            if exe and os.path.exists(exe):
                return exe
            return None
        if hasattr(self, "py_envs") and self.py_envs:
            for exe in self.py_envs.values():
                if os.path.exists(exe):
                    return exe
        return sys.executable

    def _bg_scan_libs(self, target_python):
        try:
            msg_init = f"Menggunakan Python environment: {target_python}"
            self.log(msg_init)
            log_py_debug("=== Memulai Scan Library ===")
            log_py_debug(f"Active Python: {target_python}")

            libs = []
            proc_success = False

            extract_script = (
                "import json, os, re, sys\n"
                "res = []\n"
                "try:\n"
                "    try:\n"
                "        import importlib.metadata as md\n"
                "        dists = list(md.distributions())\n"
                "        unique = {}\n"
                "        for d in dists:\n"
                "            try:\n"
                "                n = d.metadata['Name']\n"
                "                if n.lower() not in unique:\n"
                "                    unique[n.lower()] = d\n"
                "            except Exception:\n"
                "                pass\n"
                "        dep_map = {}\n"
                "        for d in unique.values():\n"
                "            try:\n"
                "                n = d.metadata['Name']\n"
                "                for r in (d.requires or []):\n"
                "                    clean_r = re.split(r'[; \\(\\)<>=!]', r)[0].strip().lower()\n"
                "                    if clean_r:\n"
                "                        dep_map.setdefault(clean_r, []).append(n)\n"
                "            except Exception:\n"
                "                pass\n"
                "        for d in unique.values():\n"
                "            try:\n"
                "                name = d.metadata['Name']\n"
                "                ver = d.version\n"
                "                sz = 0\n"
                "                if d.files:\n"
                "                    for f in d.files:\n"
                "                        try:\n"
                "                            fp = d.locate_file(f)\n"
                "                            if os.path.exists(fp) and os.path.isfile(fp):\n"
                "                                sz += os.path.getsize(fp)\n"
                "                        except Exception:\n"
                "                            pass\n"
                "                res.append({'name': name, 'version': ver, 'size_bytes': sz, 'used_by': dep_map.get(name.lower(), [])})\n"
                "            except Exception:\n"
                "                pass\n"
                "    except (ImportError, AttributeError):\n"
                "        import pkg_resources\n"
                "        for d in pkg_resources.working_set:\n"
                "            res.append({'name': d.project_name, 'version': d.version, 'size_bytes': 0, 'used_by': []})\n"
                "except Exception as e:\n"
                "    pass\n"
                "print(json.dumps(res))\n"
            )

            if target_python and os.path.exists(target_python):
                try:
                    log_py_debug(f"Menjalankan subprocess scan pada: {target_python}")
                    cmd = [target_python, "-c", extract_script]
                    p = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                                       creationflags=hidden_console_creation_flags())
                    log_py_debug(f"Subprocess returncode: {p.returncode}")
                    if p.returncode == 0 and p.stdout.strip():
                        raw_data = json.loads(p.stdout.strip())
                        if isinstance(raw_data, list):
                            for item in raw_data:
                                name = item.get("name", "")
                                libs.append({
                                    "name": name,
                                    "version": item.get("version", ""),
                                    "size_bytes": item.get("size_bytes", 0),
                                    "used_by": item.get("used_by", []),
                                    "is_core": name.lower() in PROTECTED_PACKAGES,
                                    "python_exe": target_python,
                                    "var": None
                                })
                            proc_success = True
                            log_py_debug(f"Subprocess scan berhasil mengekstrak {len(libs)} paket.")
                        else:
                            log_py_debug("Subprocess scan menghasilkan data kosong atau bukan list.")
                    else:
                        log_py_debug(f"Subprocess scan non-zero code atau output kosong. Stderr: {p.stderr}")
                except Exception as pe:
                    log_py_debug(f"Subprocess scan exception: {pe}")
                    self.log(f"Subprocess scan info: {pe}")
            else:
                log_py_debug(f"target_python tidak valid atau tidak ditemukan: {target_python}")

            if not proc_success:
                raise RuntimeError("Pemindaian interpreter terpilih gagal; paket dari environment lain tidak digunakan.")

            libs.sort(key=lambda x: x["size_bytes"], reverse=True)
            def _apply_library_scan():
                for widget in self.lib_scroll.winfo_children():
                    widget.destroy()
                self.lib_items = libs
                for item in libs:
                    self._render_lib_row(item)
            self.after(0, _apply_library_scan)

            success_msg = f"Pemindaian selesai. Terpasang {len(libs)} packages."
            self.log(success_msg)
            log_py_debug(f"{success_msg} (Log disimpan di: {PY_LIBS_DEBUG_LOG})")
        except Exception as e:
            err_msg = f"Error memindai libraries: {e}"
            self.log(err_msg)
            log_py_debug(f"FATAL EXCEPTION in _bg_scan_libs: {e}")
        finally:
            self.is_scanning_libs = False
            if hasattr(self, "btn_scan_libs"):
                self.after(0, lambda: self.btn_scan_libs.configure(state="normal", text="Pindai Ulang Library"))

    def _render_lib_row(self, item):
        def _render():
            row = ctk.CTkFrame(self.lib_scroll, corner_radius=4, fg_color="#18191C", height=38)
            row.pack(fill="x", padx=0, pady=2)
            row.pack_propagate(False)

            var = tk.BooleanVar(value=False)
            item["var"] = var
            item["row_widget"] = row

            chk = ctk.CTkCheckBox(row, text="", variable=var, width=25, checkbox_width=18, checkbox_height=18)
            if item["is_core"]:
                chk.configure(state="disabled")
            chk.pack(side="left", padx=(10, 5))

            lbl_name = ctk.CTkLabel(row, text=f"{item['name']} ({item['version']})", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", width=220)
            lbl_name.pack(side="left", padx=5)

            # Dependensi Status
            if item["is_core"]:
                dep_text = "[Paket Inti / Dilindungi]"
                dep_color = "#DC2626"
            elif item["used_by"]:
                dep_text = f"Dipakai: {', '.join(item['used_by'][:2])}"
                dep_color = "#EA580C"
            else:
                dep_text = "[Bebas Dependensi]"
                dep_color = "#16A34A"

            lbl_dep = ctk.CTkLabel(row, text=dep_text, font=ctk.CTkFont(size=11), text_color=dep_color, anchor="e", width=240)
            lbl_dep.pack(side="right", padx=15)

            lbl_sz = ctk.CTkLabel(row, text=format_size(item["size_bytes"]), font=ctk.CTkFont(size=12, weight="bold"), text_color="#38BDF8", width=90, anchor="e")
            lbl_sz.pack(side="right", padx=25)

        self.after(0, _render)

    def filter_libs(self, event=None):
        q = self.ent_lib_search.get().lower()
        for it in self.lib_items:
            w = it.get("row_widget")
            if w:
                if q in it["name"].lower():
                    w.pack(fill="x", padx=0, pady=2)
                else:
                    w.pack_forget()

    def toggle_all_lib_rows(self):
        val = self.var_lib_master.get()
        for it in self.lib_items:
            if not it["is_core"] and it.get("var"):
                it["var"].set(val)

    def confirm_and_uninstall_libs(self):
        if not self.acquire_mutation_guard("lib_uninstall"):
            return
        selected = [it for it in self.lib_items if it.get("var") and it["var"].get() and not it["is_core"]]
        if not selected:
            self.release_mutation_guard()
            messagebox.showinfo("Informasi", "Pilih minimal satu library yang tidak dilindungi untuk di-uninstall.")
            return

        names = [it["name"] for it in selected]
        if not messagebox.askyesno("Konfirmasi Uninstall", f"Uninstall {len(names)} package berikut?\n{', '.join(names[:5])}"):
            self.release_mutation_guard()
            return

        interpreters = {item.get("python_exe") for item in selected}
        if len(interpreters) != 1 or None in interpreters:
            self.release_mutation_guard()
            self.log("Interpreter hasil scan tidak valid; pindai ulang secara manual sebelum uninstall.")
            return
        target_py = interpreters.pop()
        try:
            self.executor.submit(self._bg_uninstall_libs, selected, target_py)
        except Exception as e:
            self.release_mutation_guard()
            self.log(f"Gagal menjalankan thread uninstall library: {e}")

    def _bg_uninstall_libs(self, selected_items, target_py):
        removed_names = set()
        removed_ids = set()
        for item in selected_items:
            name = item["name"]
            self.log(f"Menjalankan: pip uninstall -y {name} melalui {target_py}...")
            cmd = [target_py, "-m", "pip", "uninstall", "-y", name]
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    creationflags=hidden_console_creation_flags()
                )
                verify = subprocess.run(
                    [target_py, "-c", "import importlib.metadata as m, json, re, sys; "
                     "norm = lambda n: re.sub(r'[-_.]+', '-', n).lower(); "
                     "print(json.dumps(any(norm(d.metadata.get('Name', '')) == norm(sys.argv[1]) "
                     "for d in m.distributions())))", name],
                    capture_output=True, text=True,
                    creationflags=hidden_console_creation_flags()
                )
                if result.returncode == 0 and verify.returncode == 0 and json.loads(verify.stdout) is False:
                    removed_names.add(name)
                    removed_ids.add(id(item))
                    self.log(f"Terverifikasi terhapus dari {target_py}: {name}")
                else:
                    self.log(f"Uninstall {name} belum terverifikasi (pip exit {result.returncode}); item dipertahankan.")
                    if result.stderr.strip():
                        self.log(result.stderr.strip())
            except Exception as error:
                self.log(f"Gagal uninstall/verifikasi {name}: {error}")

        def _update_library_state():
            try:
                self.lib_items = [it for it in self.lib_items if id(it) not in removed_ids]
                for item in selected_items:
                    if id(item) in removed_ids:
                        row = item.get("row_widget")
                        if row and row.winfo_exists():
                            row.destroy()
                if hasattr(self, "ent_lib_search"):
                    self.filter_libs()
            finally:
                self.release_mutation_guard()

        self.after(0, _update_library_state)
        log_py_debug(f"Package removal verified for interpreter {target_py}: {sorted(removed_names)}")

    # =============================================================
    # VIEW 4: STARTUP & WINDOWS SERVICES MANAGER
    # =============================================================
    def setup_startup_svc_view(self):
        parent = self.views["startup_svc"]

        # Control Bar
        ctrl_bar = ctk.CTkFrame(parent, corner_radius=8, fg_color="#18191C")
        ctrl_bar.pack(fill="x", padx=0, pady=(0, 8))

        self.seg_startup_svc = ctk.CTkSegmentedButton(
            ctrl_bar,
            values=["Startup Programs (Aplikasi Otomatis)", "Windows Services (Layanan Latar Belakang)"],
            command=self.toggle_startup_svc_view
        )
        self.seg_startup_svc.set("Startup Programs (Aplikasi Otomatis)")
        self.seg_startup_svc.pack(side="left", padx=12, pady=10)

        self.btn_refresh_startup_svc = ctk.CTkButton(ctrl_bar, text="Segarkan Data", width=120, fg_color="#0284C7", command=self.refresh_startup_svc_async)
        self.btn_refresh_startup_svc.pack(side="left", padx=10)

        # Container for Startup Table
        self.startup_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.startup_container.pack(fill="both", expand=True)

        st_header = ctk.CTkFrame(self.startup_container, height=32, corner_radius=6, fg_color="#0F172A")
        st_header.pack(fill="x", padx=0, pady=(0, 4))
        st_header.pack_propagate(False)

        ctk.CTkLabel(st_header, text="Nama Program Startup", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=15)
        ctk.CTkLabel(st_header, text="Aksi Cepat", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=25)
        ctk.CTkLabel(st_header, text="Status Saat Ini", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=30)
        ctk.CTkLabel(st_header, text="Perintah Eksekusi / Target Path", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=50)

        self.startup_scroll = ctk.CTkScrollableFrame(self.startup_container, fg_color="transparent")
        self.startup_scroll.pack(fill="both", expand=True)

        # Container for Services Table (Initially Hidden)
        self.svc_container = ctk.CTkFrame(parent, fg_color="transparent")

        svc_header = ctk.CTkFrame(self.svc_container, height=32, corner_radius=6, fg_color="#0F172A")
        svc_header.pack(fill="x", padx=0, pady=(0, 4))
        svc_header.pack_propagate(False)

        ctk.CTkLabel(svc_header, text="Nama Layanan (Service)", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=15)
        ctk.CTkLabel(svc_header, text="Aksi Layanan", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=25)
        ctk.CTkLabel(svc_header, text="Status Layanan", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=35)
        ctk.CTkLabel(svc_header, text="Tipe Startup", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=45)

        self.svc_scroll = ctk.CTkScrollableFrame(self.svc_container, fg_color="transparent")
        self.svc_scroll.pack(fill="both", expand=True)

    def toggle_startup_svc_view(self, choice):
        if "Startup" in choice:
            self.svc_container.pack_forget()
            self.startup_container.pack(fill="both", expand=True)
            self.scan_startup_items_async()
        else:
            self.startup_container.pack_forget()
            self.svc_container.pack(fill="both", expand=True)
            self.scan_services_async()

    def refresh_startup_svc_async(self):
        choice = self.seg_startup_svc.get()
        if "Startup" in choice:
            self.scan_startup_items_async()
        else:
            self.scan_services_async()

    def scan_startup_items_async(self):
        if getattr(self, "active_mutation", None) is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; pemindaian Startup ditunda.")
            return
        if getattr(self, "is_scanning_startup", False):
            self.log("Peringatan: Pemindaian Startup sedang berjalan. Mohon tunggu...")
            return
        self.is_scanning_startup = True
        if hasattr(self, "btn_refresh_startup_svc"):
            self.btn_refresh_startup_svc.configure(state="disabled", text="Memindai...")

        self.log("Memindai entri Startup programs di registry Windows...")
        for w in self.startup_scroll.winfo_children():
            w.destroy()
        self.startup_items.clear()
        self.executor.submit(self._bg_scan_startup)

    def _bg_scan_startup(self):
        try:
            items = []
            roots = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM")
            ]

            # Baca status StartupApproved
            disabled_set = set()
            for root_h, base_sub, tag in roots:
                appr_sub = rf"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
                try:
                    ak = winreg.OpenKey(root_h, appr_sub)
                    for i in range(winreg.QueryInfoKey(ak)[1]):
                        aname, aval, _ = winreg.EnumValue(ak, i)
                        if len(aval) > 0 and aval[0] in (3, 7):
                            disabled_set.add((tag, aname.lower()))
                except Exception:
                    pass

            for root_h, base_sub, tag in roots:
                try:
                    k = winreg.OpenKey(root_h, base_sub)
                    for i in range(winreg.QueryInfoKey(k)[1]):
                        name, val, _ = winreg.EnumValue(k, i)
                        is_enabled = (tag, name.lower()) not in disabled_set
                        item = {
                            "name": name,
                            "cmd": val,
                            "root_h": root_h,
                            "root_tag": tag,
                            "is_enabled": is_enabled
                        }
                        items.append(item)
                        self._render_startup_row(item)
                except Exception:
                    pass

            self.startup_items = items
            self.log(f"Ditemukan {len(items)} program startup.")
        finally:
            self.is_scanning_startup = False
            if hasattr(self, "btn_refresh_startup_svc"):
                self.after(0, lambda: self.btn_refresh_startup_svc.configure(state="normal", text="Segarkan Data"))

    def _render_startup_row(self, item):
        def _render():
            row = ctk.CTkFrame(self.startup_scroll, corner_radius=4, fg_color="#18191C", height=40)
            row.pack(fill="x", padx=0, pady=2)
            row.pack_propagate(False)

            lbl_name = ctk.CTkLabel(row, text=f"{item['name']} ({item['root_tag']})", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", width=220)
            lbl_name.pack(side="left", padx=15)

            # Tombol Toggle Status
            btn_toggle = ctk.CTkButton(
                row,
                text="Nonaktifkan" if item["is_enabled"] else "Aktifkan",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#EA580C" if item["is_enabled"] else "#16A34A",
                hover_color="#C2410C" if item["is_enabled"] else "#15803D",
                width=110,
                height=26,
                command=lambda it=item: self.toggle_startup_state(it)
            )
            btn_toggle.pack(side="right", padx=15)

            # Status Badge
            st_text = "[AKTIF]" if item["is_enabled"] else "[NONAKTIF]"
            st_color = "#16A34A" if item["is_enabled"] else "#64748B"
            lbl_st = ctk.CTkLabel(row, text=st_text, font=ctk.CTkFont(size=11, weight="bold"), text_color=st_color, width=90)
            lbl_st.pack(side="right", padx=15)
            item["status_widget"] = lbl_st
            item["action_widget"] = btn_toggle

            # Command line truncated
            cmd_str = item["cmd"]
            if len(cmd_str) > 45:
                cmd_str = cmd_str[:20] + "..." + cmd_str[-22:]
            lbl_cmd = ctk.CTkLabel(row, text=cmd_str, font=ctk.CTkFont(size=11), text_color="#94A3B8", anchor="e")
            lbl_cmd.pack(side="right", padx=20)

        self.after(0, _render)

    def toggle_startup_state(self, item):
        if not self.acquire_mutation_guard("startup_toggle"):
            return
        root_h = item["root_h"]
        name = item["name"]
        new_state = not item["is_enabled"]
        appr_sub = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"

        try:
            val_bytes = (b'\x02' if new_state else b'\x03') + bytes(11)
            with winreg.OpenKey(root_h, appr_sub, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, val_bytes)
                actual, value_type = winreg.QueryValueEx(key, name)
                if value_type != winreg.REG_BINARY or actual != val_bytes:
                    raise OSError("Nilai StartupApproved tidak cocok setelah ditulis.")
            item["is_enabled"] = new_state
            status = item.get("status_widget")
            button = item.get("action_widget")
            if status and status.winfo_exists():
                status.configure(text="[AKTIF]" if new_state else "[NONAKTIF]",
                                 text_color="#16A34A" if new_state else "#64748B")
            if button and button.winfo_exists():
                button.configure(text="Nonaktifkan" if new_state else "Aktifkan",
                                 fg_color="#EA580C" if new_state else "#16A34A",
                                 hover_color="#C2410C" if new_state else "#15803D")
            st_msg = "diaktifkan" if new_state else "dinonaktifkan"
            self.log(f"Startup item '{name}' berhasil {st_msg}.")
        except Exception as e:
            self.log(f"Gagal mengubah status startup '{name}': {e}")
            messagebox.showerror("Error", f"Gagal mengubah status startup:\n{e}\nPastikan aplikasi dijalankan dengan hak Administrator.")
        finally:
            self.release_mutation_guard()

    def scan_services_async(self):
        if getattr(self, "active_mutation", None) is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; pemindaian Services ditunda.")
            return
        if getattr(self, "is_scanning_services", False):
            self.log("Peringatan: Pemindaian Services sedang berjalan. Mohon tunggu...")
            return
        self.is_scanning_services = True
        if hasattr(self, "btn_refresh_startup_svc"):
            self.btn_refresh_startup_svc.configure(state="disabled", text="Memindai...")

        self.log("Memindai layanan Windows (Services) pihak ketiga / aplikasi...")
        for w in self.svc_scroll.winfo_children():
            w.destroy()
        self.service_items.clear()
        self.executor.submit(self._bg_scan_services)

    def _bg_scan_services(self):
        try:
            svcs = []
            try:
                for s in psutil.win_service_iter():
                    try:
                        s_name = s.name()
                        s_disp = s.display_name()
                        s_status = s.status()
                        s_type = s.start_type()

                        # Filter layanan kritis Windows dasar
                        if s_name.lower().startswith(("rpcss", "dcomlaunch", "lsass", "samss", "winlogon")):
                            continue

                        item = {
                            "name": s_name,
                            "disp": s_disp,
                            "status": s_status,
                            "start_type": s_type
                        }
                        svcs.append(item)
                        self._render_service_row(item)
                    except Exception:
                        pass
            except Exception as e:
                self.log(f"Error memindai services: {e}")

            self.service_items = svcs
            self.log(f"Ditemukan {len(svcs)} layanan Windows.")
        finally:
            self.is_scanning_services = False
            if hasattr(self, "btn_refresh_startup_svc"):
                self.after(0, lambda: self.btn_refresh_startup_svc.configure(state="normal", text="Segarkan Data"))

    def _render_service_row(self, item):
        def _render():
            row = ctk.CTkFrame(self.svc_scroll, corner_radius=4, fg_color="#18191C", height=40)
            row.pack(fill="x", padx=0, pady=2)
            row.pack_propagate(False)

            lbl_name = ctk.CTkLabel(row, text=f"{item['disp']} ({item['name']})", font=ctk.CTkFont(size=12, weight="bold"), anchor="w", width=250)
            lbl_name.pack(side="left", padx=15)

            is_running = item["status"] == "running"
            btn_act = ctk.CTkButton(
                row,
                text="Stop Service" if is_running else "Start Service",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#DC2626" if is_running else "#16A34A",
                hover_color="#B91C1C" if is_running else "#15803D",
                width=110,
                height=26,
                command=lambda it=item: self.toggle_service_state(it)
            )
            btn_act.pack(side="right", padx=15)

            st_color = "#16A34A" if is_running else "#64748B"
            lbl_st = ctk.CTkLabel(row, text=f"[{item['status'].upper()}]", font=ctk.CTkFont(size=11, weight="bold"), text_color=st_color, width=95)
            lbl_st.pack(side="right", padx=15)
            item["status_widget"] = lbl_st
            item["action_widget"] = btn_act

            lbl_type = ctk.CTkLabel(row, text=f"Startup: {item['start_type']}", font=ctk.CTkFont(size=11), text_color="#94A3B8", width=120, anchor="e")
            lbl_type.pack(side="right", padx=15)

        self.after(0, _render)

    def toggle_service_state(self, item):
        if not self.acquire_mutation_guard("service_toggle"):
            return
        name = item["name"]
        is_running = item["status"] == "running"
        action = "stop" if is_running else "start"
        self.log(f"Menjalankan: sc.exe {action} {name}...")

        def _bg():
            try:
                res = subprocess.run(
                    ["sc.exe", action, name], capture_output=True, text=True,
                    creationflags=hidden_console_creation_flags()
                )
                if res.returncode != 0:
                    self.log(f"Peringatan sc.exe: {res.stdout.strip() or res.stderr.strip()}")
                    return
                expected = "stopped" if action == "stop" else "running"
                actual = psutil.win_service_get(name).status()
                if actual != expected:
                    self.log(f"Status layanan '{name}' belum terverifikasi ({actual}); gunakan Segarkan Data untuk memeriksa lagi.")
                    return
                def _update():
                    item["status"] = actual
                    running = actual == "running"
                    status = item.get("status_widget")
                    button = item.get("action_widget")
                    if status and status.winfo_exists():
                        status.configure(text=f"[{actual.upper()}]", text_color="#16A34A" if running else "#64748B")
                    if button and button.winfo_exists():
                        button.configure(text="Stop Service" if running else "Start Service",
                                         fg_color="#DC2626" if running else "#16A34A",
                                         hover_color="#B91C1C" if running else "#15803D")
                self.after(0, _update)
                self.log(f"Layanan '{name}' berhasil di-{action}!")
            except Exception as error:
                self.log(f"Gagal menjalankan/verifikasi layanan '{name}': {error}")
            finally:
                self.release_mutation_guard()

        try:
            self.executor.submit(_bg)
        except Exception as e:
            self.release_mutation_guard()
            self.log(f"Gagal menjalankan thread toggle service: {e}")

    # =============================================================
    # VIEW: DUPLICATE FILE FINDER (SAFE RECYCLE BIN & AUTO-SELECT)
    # =============================================================
    def setup_dup_finder_view(self):
        parent = self.views["dup_finder"]

        # Control Bar
        ctrl_bar = ctk.CTkFrame(parent, corner_radius=8, fg_color="#18191C")
        ctrl_bar.pack(fill="x", padx=0, pady=(0, 8))

        ctk.CTkLabel(ctrl_bar, text="Folder Scan:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(12, 4))
        self.lbl_dup_path = ctk.CTkLabel(ctrl_bar, text=self.dup_target_dir, font=ctk.CTkFont(size=11), text_color="#38BDF8", width=180, anchor="w")
        self.lbl_dup_path.pack(side="left", padx=4)

        btn_browse = ctk.CTkButton(ctrl_bar, text="Pilih Folder...", width=100, height=28, fg_color="#334155", command=self.browse_dup_folder)
        btn_browse.pack(side="left", padx=5)

        self.btn_dup_scan = ctk.CTkButton(ctrl_bar, text="Mulai Scan Duplikat", width=140, height=28, fg_color="#0284C7", command=self.start_dup_scan_async)
        self.btn_dup_scan.pack(side="left", padx=8)

        # Dropdown Auto-Select Mode
        ctk.CTkLabel(ctrl_bar, text="Pilih Otomatis:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(10, 4))
        self.opt_dup_auto = ctk.CTkOptionMenu(
            ctrl_bar,
            values=["Pilih Duplikat Terbaru (Default)", "Pilih Duplikat Terlama", "Kosongkan Pilihan"],
            width=190,
            height=28,
            command=self.on_dup_auto_select_change
        )
        self.opt_dup_auto.set("Pilih Duplikat Terbaru (Default)")
        self.opt_dup_auto.pack(side="left", padx=4)

        # Delete Action Button
        self.btn_dup_delete = ctk.CTkButton(
            ctrl_bar,
            text="Hapus Terpilih ke Recycle Bin",
            font=ctk.CTkFont(weight="bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            height=28,
            command=self.confirm_and_delete_duplicates
        )
        self.btn_dup_delete.pack(side="right", padx=12, pady=8)

        # Stats & Recycle Bin Retention Bar
        retention_bar = ctk.CTkFrame(parent, corner_radius=6, fg_color="#111827", height=32)
        retention_bar.pack(fill="x", padx=0, pady=(0, 6))
        retention_bar.pack_propagate(False)

        self.lbl_dup_summary = ctk.CTkLabel(
            retention_bar,
            text="Duplikat: 0 file | Terpilih: 0 file (0 B siap dihemat)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4ADE80"
        )
        self.lbl_dup_summary.pack(side="left", padx=12)

        # Storage Sense 30-day Retention Toggle
        self.var_recycle_reminder = tk.BooleanVar(value=True)
        self.chk_recycle_reminder = ctk.CTkCheckBox(
            retention_bar,
            text="Windows Storage Sense 30 Hari (Auto Bersih Tong Sampah)",
            variable=self.var_recycle_reminder,
            font=ctk.CTkFont(size=11),
            checkbox_width=16,
            checkbox_height=16,
            command=self.toggle_recycle_reminder_policy
        )
        self.chk_recycle_reminder.pack(side="right", padx=12)
        self._init_storage_sense_state()

        # Table Header
        header = ctk.CTkFrame(parent, height=32, corner_radius=6, fg_color="#0F172A")
        header.pack(fill="x", padx=0, pady=(0, 4))
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Pilih", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=(10, 5))
        ctk.CTkLabel(header, text="Nama File & Lokasi Path Lengkap", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Aksi Lokasi", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=20)
        ctk.CTkLabel(header, text="Status", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=30)
        ctk.CTkLabel(header, text="Waktu Dibuat", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=35)
        ctk.CTkLabel(header, text="Ukuran", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8").pack(side="right", padx=45)

        self.dup_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.dup_scroll.pack(fill="both", expand=True)

    def browse_dup_folder(self):
        d = filedialog.askdirectory(initialdir=self.dup_target_dir, title="Pilih Folder untuk Scan Duplikat")
        if d:
            self.dup_target_dir = d
            disp = d
            if len(disp) > 28:
                disp = disp[:12] + "..." + disp[-13:]
            self.lbl_dup_path.configure(text=disp)
            self.log(f"Folder target duplikat disetel ke: {d}")

    def _init_storage_sense_state(self):
        try:
            reg_p = r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy"
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_p, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(k, "128") # Policy retention days
            enabled, _ = winreg.QueryValueEx(k, "01")
            if enabled == 1 and val in (30, 14, 60):
                self.var_recycle_reminder.set(True)
            else:
                self.var_recycle_reminder.set(False)
        except Exception:
            self.var_recycle_reminder.set(False)

    def toggle_recycle_reminder_policy(self):
        enable = self.var_recycle_reminder.get()
        reg_p = r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy"
        try:
            k = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_p, 0, winreg.KEY_SET_VALUE)
            if enable:
                winreg.SetValueEx(k, "01", 0, winreg.REG_DWORD, 1) # Enable Storage Sense
                winreg.SetValueEx(k, "128", 0, winreg.REG_DWORD, 30) # 30 Days Recycle Bin retention
                winreg.SetValueEx(k, "04", 0, winreg.REG_DWORD, 1)
                self.log("Storage Sense: Auto hapus Recycle Bin setelah 30 hari DIAKTIFKAN.")
                messagebox.showinfo("Storage Sense", "Kebijakan Windows Storage Sense disetel:\nFile di Recycle Bin akan otomatis dibersihkan setelah 30 hari.")
            else:
                winreg.SetValueEx(k, "128", 0, winreg.REG_DWORD, 0) # Never auto delete
                self.log("Storage Sense: Auto hapus Recycle Bin dinonaktifkan (Simpan selamanya sampai dikosongkan manual).")
        except Exception as e:
            self.log(f"Gagal mengatur Storage Sense registry: {e}")

    def start_dup_scan_async(self):
        if getattr(self, "active_mutation", None) is not None:
            self.log(f"Operasi '{self.active_mutation}' sedang berlangsung; pemindaian file duplikat ditunda.")
            return
        if getattr(self, "is_scanning_dup", False):
            self.log("Peringatan: Pemindaian file duplikat sedang berjalan. Mohon tunggu proses selesai.")
            return

        target = self.dup_target_dir
        if not os.path.exists(target):
            messagebox.showerror("Error", "Folder target tidak ditemukan!")
            return

        self.is_scanning_dup = True
        self.btn_dup_scan.configure(state="disabled", text="⏳  MEMINDAI...")

        for w in self.dup_scroll.winfo_children():
            w.destroy()

        self.dup_groups.clear()
        self.dup_items.clear()
        self.lbl_dup_summary.configure(text="Sedang memindai file dan memverifikasi hash...")
        self.log(f"Memulai pemindaian file duplikat di: {target}...")
        self.executor.submit(self._bg_dup_scan, target)

    def _bg_dup_scan(self, target_folder):
        size_dict = {}
        scanned_count = 0
        last_ui_update = time.time()

        # Step 1: Grouping by size (Aman dari junction & reparse points)
        try:
            for root, dirs, files in os.walk(target_folder, followlinks=False):
                if any(b in root.lower() for b in BLOCKED_DIRS):
                    continue
                # Prune junctions / reparse points agar tidak circular loop
                dirs[:] = [d for d in dirs if not is_junction(os.path.join(root, d))]

                for f in files:
                    scanned_count += 1
                    fp = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(fp)
                        if sz > 1024:  # Filter file sangat kecil < 1KB
                            size_dict.setdefault(sz, []).append(fp)
                    except (OSError, PermissionError):
                        pass

                    now = time.time()
                    if now - last_ui_update > 0.4:
                        last_ui_update = now
                        cur_cnt = scanned_count
                        self.after(0, lambda c=cur_cnt: self.lbl_dup_summary.configure(
                            text=f"Memindai direktori... ({c:,} file diperiksa)"
                        ))

            # Step 2: 2-Phase Hash Verification
            # Phase 2a: Fast Hash (first 64KB) for size collisions
            fast_hash_dict = {}
            candidates = [fps for fps in size_dict.values() if len(fps) > 1]
            total_cand_files = sum(len(fps) for fps in candidates)
            hashed_cand = 0

            for fps in candidates:
                for fp in fps:
                    hashed_cand += 1
                    try:
                        hasher = hashlib.md5()
                        with open(fp, "rb") as fh:
                            buf = fh.read(65536)  # Check initial 64KB for speed
                            hasher.update(buf)
                        fh_val = hasher.hexdigest()
                        sz = os.path.getsize(fp)
                        fast_hash_dict.setdefault((sz, fh_val), []).append(fp)
                    except Exception:
                        pass

                    now = time.time()
                    if now - last_ui_update > 0.4:
                        last_ui_update = now
                        hc = hashed_cand
                        self.after(0, lambda c=hc, t=total_cand_files: self.lbl_dup_summary.configure(
                            text=f"Verifikasi hash cepat... ({c:,}/{t:,} kandidat)"
                        ))

            # Phase 2b: Full Hash for exact match on matching fast hashes (> 64KB)
            final_hash_dict = {}
            for (sz, fh_val), fps in fast_hash_dict.items():
                if len(fps) < 2:
                    continue
                if sz <= 65536:
                    # Sudah terhash penuh
                    final_hash_dict.setdefault((sz, fh_val), []).extend(fps)
                else:
                    for fp in fps:
                        try:
                            full_hasher = hashlib.md5()
                            with open(fp, "rb") as fh:
                                while True:
                                    chunk = fh.read(262144)  # 256 KB chunk
                                    if not chunk:
                                        break
                                    full_hasher.update(chunk)
                            final_h = full_hasher.hexdigest()
                            final_hash_dict.setdefault((sz, final_h), []).append(fp)
                        except Exception:
                            pass

            dup_groups = []
            all_dup_items = []
            group_idx = 1

            for (sz, h), fps in final_hash_dict.items():
                if len(fps) > 1:
                    sorted_files = []
                    for p in fps:
                        try:
                            mtime = os.path.getmtime(p)
                        except OSError:
                            mtime = 0
                        sorted_files.append((p, mtime))
                    sorted_files.sort(key=lambda x: x[1])

                    group_info = {
                        "group_id": group_idx,
                        "size_bytes": sz,
                        "items": []
                    }

                    for idx, (p, mtime) in enumerate(sorted_files):
                        is_newest = (idx == len(sorted_files) - 1)
                        is_oldest = (idx == 0)
                        item = {
                            "group_id": group_idx,
                            "path": p,
                            "name": os.path.basename(p),
                            "size_bytes": sz,
                            "mtime": mtime,
                            "is_newest": is_newest,
                            "is_oldest": is_oldest,
                            "var": None
                        }
                        group_info["items"].append(item)
                        all_dup_items.append(item)

                    dup_groups.append(group_info)
                    group_idx += 1

            self.dup_groups = dup_groups
            self.dup_items = all_dup_items

        except Exception as e:
            self.log(f"Error saat scan duplikat: {e}")
        finally:
            def _finish_dup_scan():
                self.is_scanning_dup = False
                self.btn_dup_scan.configure(state="normal", text="Mulai Scan Duplikat")
                self._render_all_dup_groups()
            self.after(0, _finish_dup_scan)

    def _render_all_dup_groups(self):
        for w in self.dup_scroll.winfo_children():
            w.destroy()

        if not self.dup_groups:
            self.lbl_dup_summary.configure(text="Tidak ditemukan file duplikat di folder ini. Ruang disk bersih!")
            lbl_empty = ctk.CTkLabel(self.dup_scroll, text="Tidak ada file duplikat yang terdeteksi.", font=ctk.CTkFont(size=13), text_color="#94A3B8")
            lbl_empty.pack(pady=40)
            return

        # Render bertahap agar UI responsif jika terdapat ratusan grup
        MAX_INITIAL_GROUPS = 60
        groups_to_render = self.dup_groups[:MAX_INITIAL_GROUPS]

        for group in groups_to_render:
            grp_frame = ctk.CTkFrame(self.dup_scroll, corner_radius=6, fg_color="#18191C")
            grp_frame.pack(fill="x", padx=0, pady=4)

            grp_hdr = ctk.CTkFrame(grp_frame, fg_color="#1E293B", height=26, corner_radius=4)
            grp_hdr.pack(fill="x", padx=4, pady=3)
            grp_hdr.pack_propagate(False)

            ctk.CTkLabel(
                grp_hdr,
                text=f"Group Duplikat #{group['group_id']} ({len(group['items'])} File Identik) - Ukuran Satuan: {format_size(group['size_bytes'])}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#38BDF8"
            ).pack(side="left", padx=8)

            for item in group["items"]:
                row = ctk.CTkFrame(grp_frame, corner_radius=4, fg_color="#131417", height=38)
                row.pack(fill="x", padx=4, pady=2)
                row.pack_propagate(False)

                var = item.get("var")
                if var is None:
                    var = tk.BooleanVar(value=item["is_newest"]) # Default select newest
                item["var"] = var
                chk = ctk.CTkCheckBox(row, text="", variable=var, width=25, checkbox_width=18, checkbox_height=18, command=self.update_dup_savings_counter)
                chk.pack(side="left", padx=(10, 5))

                p_str = item["path"]
                if len(p_str) > 55:
                    p_str = p_str[:25] + "..." + p_str[-26:]
                lbl_name = ctk.CTkLabel(row, text=f"{item['name']}  ({p_str})", font=ctk.CTkFont(size=11), anchor="w")
                lbl_name.pack(side="left", padx=6)

                # Open Location Button
                btn_open = ctk.CTkButton(
                    row,
                    text="Buka Folder",
                    width=90,
                    height=22,
                    fg_color="#334155",
                    font=ctk.CTkFont(size=10),
                    command=lambda p=item["path"]: self.open_in_file_explorer(p)
                )
                btn_open.pack(side="right", padx=(5, 10))

                badge_txt = "[TERBARU]" if item["is_newest"] else ("[TERLAMA]" if item["is_oldest"] else "[DUPLIKAT]")
                badge_bg = "#0284C7" if item["is_newest"] else ("#64748B" if item["is_oldest"] else "#475569")
                lbl_badge = ctk.CTkLabel(row, text=badge_txt, font=ctk.CTkFont(size=9, weight="bold"), fg_color=badge_bg, corner_radius=4, text_color="#FFFFFF", width=80, height=20)
                lbl_badge.pack(side="right", padx=10)

                mtime_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(item["mtime"]))
                lbl_time = ctk.CTkLabel(row, text=mtime_str, font=ctk.CTkFont(size=10), text_color="#94A3B8", width=110)
                lbl_time.pack(side="right", padx=10)

                lbl_sz = ctk.CTkLabel(row, text=format_size(item["size_bytes"]), font=ctk.CTkFont(size=11, weight="bold"), text_color="#38BDF8", width=80, anchor="e")
                lbl_sz.pack(side="right", padx=10)

        if len(self.dup_groups) > MAX_INITIAL_GROUPS:
            remaining_groups = len(self.dup_groups) - MAX_INITIAL_GROUPS
            lbl_more = ctk.CTkLabel(
                self.dup_scroll,
                text=f"... dan {remaining_groups} grup duplikat lainnya telah dideteksi (Total {len(self.dup_items)} file).",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#F59E0B"
            )
            lbl_more.pack(pady=10)

        self.update_dup_savings_counter()
        self.log(f"Pemindaian selesai: Ditemukan {len(self.dup_groups)} grup duplikat ({len(self.dup_items)} file).")

    def on_dup_auto_select_change(self, choice):
        if "Terbaru" in choice:
            for it in self.dup_items:
                if it.get("var"):
                    it["var"].set(it["is_newest"])
        elif "Terlama" in choice:
            for it in self.dup_items:
                if it.get("var"):
                    it["var"].set(it["is_oldest"])
        else: # Kosongkan
            for it in self.dup_items:
                if it.get("var"):
                    it["var"].set(False)
        self.update_dup_savings_counter()

    def update_dup_savings_counter(self):
        sel_count = sum(1 for it in self.dup_items if it.get("var") and it["var"].get())
        sel_bytes = sum(it["size_bytes"] for it in self.dup_items if it.get("var") and it["var"].get())
        total_dups = len(self.dup_items)
        self.lbl_dup_summary.configure(
            text=f"Total Duplikat: {total_dups} file | Terpilih: {sel_count} file ({format_size(sel_bytes)} siap dihemat via Recycle Bin)"
        )

    def open_in_file_explorer(self, file_path):
        try:
            if os.path.exists(file_path):
                subprocess.Popen(f'explorer /select,"{os.path.normpath(file_path)}"')
            else:
                messagebox.showerror("Error", "File tidak ditemukan di disk.")
        except Exception as e:
            self.log(f"Error membuka file di explorer: {e}")

    def confirm_and_delete_duplicates(self):
        if not self.acquire_mutation_guard("dup_delete"):
            return
        selected = [it for it in self.dup_items if it.get("var") and it["var"].get()]
        if not selected:
            self.release_mutation_guard()
            messagebox.showinfo("Informasi", "Pilih minimal satu file duplikat untuk dibersihkan.")
            return

        total_bytes = sum(it["size_bytes"] for it in selected)
        msg = (
            f"Anda akan menghapus {len(selected)} file duplikat terpilih senilai {format_size(total_bytes)}.\n\n"
            "KEAMANAN TERJAMIN:\n"
            "File akan dipindahkan ke RECYCLE BIN Windows (Bukan hapus permanen).\n"
            "Data masih bisa direstore kapan saja jika dibutuhkan.\n\n"
            "Lanjutkan penghapusan aman?"
        )
        if not messagebox.askyesno("Konfirmasi Safe Duplicate Cleaner", msg):
            self.release_mutation_guard()
            return

        self.btn_dup_delete.configure(state="disabled")
        self.log(f"Memindahkan {len(selected)} file duplikat ke Recycle Bin...")
        try:
            self.executor.submit(self._bg_delete_duplicates, selected)
        except Exception as e:
            self.release_mutation_guard()
            self.btn_dup_delete.configure(state="normal")
            self.log(f"Gagal menjalankan thread delete duplikat: {e}")

    def _bg_delete_duplicates(self, selected_items):
        successful_paths = set()
        saved_bytes = 0

        for it in selected_items:
            fp = it["path"]
            try:
                if not os.path.exists(fp):
                    self.log(f"File tidak ditemukan; dipertahankan dalam daftar: {fp}")
                    continue
                send2trash(fp)
                if os.path.exists(fp):
                    self.log(f"File masih ada setelah dikirim ke Recycle Bin; dipertahankan: {fp}")
                    continue
                successful_paths.add(fp)
                saved_bytes += it["size_bytes"]
                self.log(f"Ke Recycle Bin: {os.path.basename(fp)}")
            except Exception as e:
                self.log(f"Gagal memindahkan {fp} ke Recycle Bin: {e}")

        self.log(f"PEMBERSIHAN SELESAI: {len(successful_paths)} file duplikat dipindahkan. {format_size(saved_bytes)} ruang disk dihemat!")

        def _update_duplicate_state():
            try:
                self.dup_items = [it for it in self.dup_items if it.get("path") not in successful_paths]
                self.dup_groups = [
                    {**group, "items": [it for it in group["items"] if it.get("path") not in successful_paths]}
                    for group in self.dup_groups
                ]
                self.dup_groups = [group for group in self.dup_groups if group["items"]]
                self.btn_dup_delete.configure(state="normal")
                self._render_all_dup_groups()
            finally:
                self.release_mutation_guard()

        self.after(0, _update_duplicate_state)

    # =============================================================
    # VIEW: SYSTEM TOOLBOX (TWEAKS, REPAIRS, RUNTIMES & REPO TRACKER)
    # =============================================================
    def setup_ghost_toolbox_view(self):
        parent = self.views["ghost_toolbox"]

        # Control Bar
        ctrl_bar = ctk.CTkFrame(parent, corner_radius=8, fg_color="#18191C")
        ctrl_bar.pack(fill="x", padx=0, pady=(0, 8))

        self.seg_ghost = ctk.CTkSegmentedButton(
            ctrl_bar,
            values=[
                "📥 App Setup (Cleaner Native)",
                "⚡ Windows Tweaks",
                "🩺 System Health & WinSxS",
                "📦 Essential Runtimes",
                "🔗 App Link Checker"
            ],
            command=self.toggle_ghost_subview
        )
        self.seg_ghost.set("📥 App Setup (Cleaner Native)")
        self.seg_ghost.pack(side="left", padx=12, pady=10)

        btn_launch_cmd = ctk.CTkButton(
            ctrl_bar,
            text="📥 Buka Installer Folder",
            width=210,
            fg_color="#0284C7",
            hover_color="#0369A1",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._open_cleaner_downloads_folder
        )
        btn_launch_cmd.pack(side="right", padx=12, pady=10)

        # 5 Sub-Containers (100% Native Cleaner, Tanpa Ketergantungan CMD & Repo Eksternal)
        self.ghost_frames = {
            "native_setup": ctk.CTkFrame(parent, fg_color="transparent"),
            "tweaks": ctk.CTkScrollableFrame(parent, fg_color="transparent"),
            "health": ctk.CTkScrollableFrame(parent, fg_color="transparent"),
            "runtimes": ctk.CTkScrollableFrame(parent, fg_color="transparent"),
            "link_checker": ctk.CTkFrame(parent, fg_color="transparent")
        }

        self._setup_ghost_native_setup_view()
        self._setup_ghost_tweaks_view()
        self._setup_ghost_health_view()
        self._setup_ghost_runtimes_view()
        self._setup_ghost_link_checker_view()

        # Show initial subview
        self.ghost_frames["native_setup"].pack(fill="both", expand=True)

    def toggle_ghost_subview(self, choice):
        for f in self.ghost_frames.values():
            f.pack_forget()

        if "App Setup" in choice:
            self.ghost_frames["native_setup"].pack(fill="both", expand=True)
        elif "Tweaks" in choice:
            self.ghost_frames["tweaks"].pack(fill="both", expand=True)
        elif "System Health" in choice:
            self.ghost_frames["health"].pack(fill="both", expand=True)
        elif "Runtimes" in choice:
            self.ghost_frames["runtimes"].pack(fill="both", expand=True)
        elif "Link Checker" in choice:
            self.ghost_frames["link_checker"].pack(fill="both", expand=True)

    def _setup_ghost_tweaks_view(self):
        container = self.ghost_frames["tweaks"]

        tweaks = [
            (
                "Ultimate Performance Power Plan",
                "Buka dan aktifkan skema daya 'Ultimate Performance' bawaan Windows untuk latensi minimum CPU.",
                "Aktifkan Plan",
                self.apply_ultimate_performance,
                "#16A34A"
            ),
            (
                "GameDVR & Background Recording",
                "Matikan perekaman latar belakang GameDVR Xbox yang memakan FPS dan disk I/O.",
                "Matikan GameDVR",
                self.disable_gamedvr,
                "#0284C7"
            ),
            (
                "Telemetry & Diagnostic Tracking",
                "Nonaktifkan pengumpulan telemetri data Windows dan matikan background service DiagTrack.",
                "Matikan Telemetri",
                self.disable_telemetry,
                "#9333EA"
            ),
            (
                "Bing Web Search di Start Menu",
                "Hentikan pencarian web Bing di Start Menu Windows agar pencarian file lokal jauh lebih cepat.",
                "Matikan Bing Start",
                self.disable_bing_start,
                "#0284C7"
            ),
            (
                "Flush DNS & Reset IP Cache",
                "Bersihkan cache DNS resolver Windows untuk menyegarkan koneksi internet dan gaming.",
                "Flush DNS Now",
                self.apply_dns_flush,
                "#CA8A04"
            )
        ]

        for title, desc, btn_txt, cmd, btn_col in tweaks:
            card = ctk.CTkFrame(container, corner_radius=6, fg_color="#18191C", height=65)
            card.pack(fill="x", padx=0, pady=4)
            card.pack_propagate(False)

            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", padx=15, pady=8)

            lbl_t = ctk.CTkLabel(info_f, text=title, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            lbl_t.pack(anchor="w")

            lbl_d = ctk.CTkLabel(info_f, text=desc, font=ctk.CTkFont(size=11), text_color="#94A3B8", anchor="w")
            lbl_d.pack(anchor="w")

            btn = ctk.CTkButton(
                card,
                text=btn_txt,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=btn_col,
                width=135,
                height=30,
                command=cmd
            )
            btn.pack(side="right", padx=15, pady=16)

    def _setup_ghost_health_view(self):
        container = self.ghost_frames["health"]

        repairs = [
            (
                "Pembersihan Toko Komponen WinSxS (DISM Component Cleanup)",
                "Menjalankan DISM ResetBase untuk menghapus versi update lama di C:\\Windows\\WinSxS dan menghemat GB-an ruang disk.",
                "Jalankan DISM Clean",
                self.run_dism_cleanup,
                "#16A34A"
            ),
            (
                "SFC Integrity Scan & Auto Repair",
                "Menjalankan sfc /scannow untuk memeriksa dan memperbaiki file sistem Windows yang korup secara otomatis.",
                "Jalankan SFC Scan",
                self.run_sfc_scan,
                "#0284C7"
            ),
            (
                "Windows Update Repair",
                "Mendiagnosis dan memperbaiki komponen update Windows menggunakan service dan utility bawaan.",
                "Perbaiki Update",
                self.repair_windows_update,
                "#0284C7"
            ),
            (
                "Repair Microsoft Store",
                "Reset cache Microsoft Store melalui utility wsreset bawaan Windows.",
                "Reset Store",
                self.reset_store_cache,
                "#9333EA"
            ),
            (
                "Windows Activation Status",
                "Tampilkan informasi status aktivasi Windows menggunakan slmgr bawaan.",
                "Cek Aktivasi",
                self.check_activation_status,
                "#CA8A04"
            )
        ]

        for title, desc, btn_txt, cmd, btn_col in repairs:
            card = ctk.CTkFrame(container, corner_radius=6, fg_color="#18191C", height=65)
            card.pack(fill="x", padx=0, pady=4)
            card.pack_propagate(False)

            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", padx=15, pady=8)

            ctk.CTkLabel(info_f, text=title, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(info_f, text=desc, font=ctk.CTkFont(size=11), text_color="#94A3B8", anchor="w").pack(anchor="w")

            btn = ctk.CTkButton(card, text=btn_txt, font=ctk.CTkFont(size=11, weight="bold"), fg_color=btn_col, width=135, height=30, command=cmd)
            btn.pack(side="right", padx=15, pady=16)

    def _setup_ghost_runtimes_view(self):
        container = self.ghost_frames["runtimes"]

        runtimes = [
            (
                "Essential Runtime Checker",
                "Periksa runtime .NET, Visual C++, DirectX, dan Java yang tersedia di sistem.",
                "Cek Runtime",
                self.check_essential_runtimes,
                "#16A34A"
            ),
            (
                "Install Visual C++ Redistributable",
                "Buka sumber resmi Microsoft untuk mengunduh runtime Visual C++ terbaru.",
                "Buka Download",
                self.open_vcredist_download,
                "#0284C7"
            ),
            (
                "Install .NET Desktop Runtime",
                "Buka sumber resmi Microsoft untuk memilih .NET Desktop Runtime.",
                "Buka Download",
                self.open_dotnet_download,
                "#9333EA"
            ),
            (
                "Install DirectX Runtime",
                "Buka sumber resmi Microsoft untuk mengunduh DirectX End-User Runtime.",
                "Buka Download",
                self.open_directx_download,
                "#CA8A04"
            ),
            (
                "Install Java Runtime",
                "Buka sumber resmi Adoptium untuk mengunduh Eclipse Temurin.",
                "Buka Download",
                self.open_java_download,
                "#16A34A"
            )
        ]

        for title, desc, btn_txt, cmd, btn_col in runtimes:
            card = ctk.CTkFrame(container, corner_radius=6, fg_color="#18191C", height=65)
            card.pack(fill="x", padx=0, pady=4)
            card.pack_propagate(False)

            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", padx=15, pady=8)

            ctk.CTkLabel(info_f, text=title, font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(anchor="w")
            ctk.CTkLabel(info_f, text=desc, font=ctk.CTkFont(size=11), text_color="#94A3B8", anchor="w").pack(anchor="w")

            btn = ctk.CTkButton(card, text=btn_txt, font=ctk.CTkFont(size=11, weight="bold"), fg_color=btn_col, width=135, height=30, command=cmd)
            btn.pack(side="right", padx=15, pady=16)

    def _setup_ghost_link_checker_view(self):
        container = self.ghost_frames["link_checker"]

        self.link_checker_url_var = tk.StringVar()
        self.link_checker_status = tk.StringVar(value="Ready")

        ctk.CTkLabel(container, text="Link Checker", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkLabel(container, text="Masukkan URL untuk memeriksa ketersediaan link.", font=ctk.CTkFont(size=12), text_color="#94A3B8").pack(anchor="w", padx=12, pady=4)

        self.ent_link_checker = ctk.CTkEntry(container, textvariable=self.link_checker_url_var, placeholder_text="https://example.com", width=420)
        self.ent_link_checker.pack(anchor="w", padx=12, pady=8)

        self.btn_link_checker = ctk.CTkButton(container, text="Cek Link", command=self.check_link)
        self.btn_link_checker.pack(anchor="w", padx=12, pady=4)

        self.lbl_link_checker_status = ctk.CTkLabel(container, textvariable=self.link_checker_status, font=ctk.CTkFont(size=11), text_color="#94A3B8")
        self.lbl_link_checker_status.pack(anchor="w", padx=12, pady=4)

    def check_link(self):
        url = self.link_checker_url_var.get().strip()
        if not url:
            self.link_checker_status.set("Masukkan URL terlebih dahulu")
            return

        self.link_checker_status.set("Memeriksa...")
        self.executor.submit(self._bg_check_link, url)

    def _bg_check_link(self, url):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "DevAICleaner/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                code = response.status
                final_url = response.geturl()
            text = f"HTTP {code} — {final_url}"
        except urllib.error.HTTPError as error:
            text = f"HTTP {error.code} — {url}"
        except Exception as error:
            text = f"Gagal: {error}"

        self.after(0, lambda t=text: self.link_checker_status.set(t))

    def open_vcredist_download(self):
        webbrowser.open("https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist")

    def open_dotnet_download(self):
        webbrowser.open("https://dotnet.microsoft.com/download/dotnet")

    def open_directx_download(self):
        webbrowser.open("https://www.microsoft.com/download/details.aspx?id=35")

    def open_java_download(self):
        webbrowser.open("https://adoptium.net/temurin/releases/")

    def check_essential_runtimes(self):
        checks = []
        try:
            proc = subprocess.run(["dotnet", "--list-runtimes"], capture_output=True, text=True, creationflags=hidden_console_creation_flags())
            if proc.returncode == 0:
                checks.append(".NET: " + (proc.stdout.strip().replace("\n", ", ") or "tidak ada runtime"))
            else:
                checks.append(".NET: tidak tersedia")
        except FileNotFoundError:
            checks.append(".NET: tidak tersedia")
        except Exception as error:
            checks.append(f".NET: gagal diperiksa ({error})")

        self.log("Pemeriksaan runtime: " + " | ".join(checks))
        messagebox.showinfo("Essential Runtimes", "\n".join(checks))

    def run_dism_cleanup(self):
        if not messagebox.askyesno("Konfirmasi DISM", "Jalankan DISM Component Cleanup? Operasi ini mungkin memerlukan waktu dan hak Administrator."):
            return
        self.executor.submit(self._run_console_tool, ["dism", "/Online", "/Cleanup-Image", "/StartComponentCleanup"])

    def run_sfc_scan(self):
        self.executor.submit(self._run_console_tool, ["sfc", "/scannow"])

    def _run_console_tool(self, cmd):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=hidden_console_creation_flags())
            output = proc.stdout.strip() or proc.stderr.strip()
            if output:
                self.log(output)
            self.log(f"Perintah selesai dengan exit code {proc.returncode}: {' '.join(cmd)}")
        except Exception as error:
            self.log(f"Gagal menjalankan {' '.join(cmd)}: {error}")

    def disable_telemetry(self):
        def _bg():
            for cmd in (["sc.exe", "stop", "DiagTrack"], ["sc.exe", "config", "DiagTrack", "start=", "disabled"]):
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=hidden_console_creation_flags())
                    if proc.returncode:
                        self.log(proc.stdout.strip() or proc.stderr.strip())
                except Exception as error:
                    self.log(f"Gagal menjalankan {' '.join(cmd)}: {error}")
        self.executor.submit(_bg)

    def apply_dns_flush(self):
        self.executor.submit(self._run_console_tool, ["ipconfig", "/flushdns"])

    def repair_windows_update(self):
        cmds = (["sc.exe", "stop", "wuauserv"], ["sc.exe", "start", "wuauserv"])
        self.executor.submit(self._run_console_sequence, cmds)

    def _run_console_sequence(self, commands):
        for cmd in commands:
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, creationflags=hidden_console_creation_flags())
                if proc.returncode:
                    self.log(proc.stdout.strip() or proc.stderr.strip())
            except Exception as error:
                self.log(f"Gagal menjalankan {' '.join(cmd)}: {error}")

    def apply_ultimate_performance(self):
        self.executor.submit(self._run_console_tool, ["powercfg", "/duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"])

    def disable_gamedvr(self):
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0)
            self.log("GameDVR background recording dinonaktifkan.")
        except Exception as error:
            self.log(f"Gagal mengubah GameDVR: {error}")

    def disable_bing_start(self):
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\Explorer", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisableSearchBoxSuggestions", 0, winreg.REG_DWORD, 1)
            self.log("Bing web search Start Menu dinonaktifkan.")
        except Exception as error:
            self.log(f"Gagal mengubah kebijakan Bing Start: {error}")

    def reset_store_cache(self):
        self.executor.submit(self._run_console_tool, ["wsreset.exe"])

    def check_activation_status(self):
        self.executor.submit(self._run_console_tool, ["cscript.exe", "//Nologo", "slmgr.vbs", "/xpr"])

    def _save_startup_scan_preference(self):
        if not save_startup_scan_preference(STARTUP_SCAN_PREFERENCE_FILE, self.startup_scan_var.get()):
            self.log("Preferensi Smart Scan startup gagal disimpan; pemindaian otomatis saat startup dinonaktifkan.")

    def auto_initial_scan(self):
        if self.__dict__.get("_startup_scan_dispatched", False):
            return
        self._startup_scan_dispatched = True
        if getattr(self, "startup_scan_var", None) and self.startup_scan_var.get():
            self.start_smart_scan_async()
        else:
            self.log("Smart Scan startup dinonaktifkan; mulai scan secara manual bila diperlukan.")


    def _setup_ghost_native_setup_view(self):
        container = self.ghost_frames["native_setup"]

        # Control Bar: Search & Category Filter
        ctrl = ctk.CTkFrame(container, corner_radius=6, fg_color="#18191C", height=46)
        ctrl.pack(fill="x", padx=0, pady=(0, 6))

        ctk.CTkLabel(
            ctrl,
            text="Installer Mandiri (Download & Setup):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38BDF8"
        ).pack(side="left", padx=12, pady=10)

        # Search Entry
        self.native_app_search = ctk.CTkEntry(
            ctrl,
            placeholder_text="Cari software...",
            width=200,
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.native_app_search.pack(side="left", padx=6, pady=9)
        self.native_app_search.bind("<KeyRelease>", lambda e: self._filter_native_apps())

        # Category Filter
        self.native_app_cat = ctk.CTkComboBox(
            ctrl,
            values=["Semua Kategori", "Web Browsers", "Essential Runtimes", "Utilities & Tools", "Gaming & Social", "Media & Streaming", "Cloud & Downloaders"],
            width=165,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda v: self._filter_native_apps()
        )
        self.native_app_cat.set("Semua Kategori")
        self.native_app_cat.pack(side="left", padx=6, pady=9)

        # Open Downloads Folder
        btn_open_dl = ctk.CTkButton(
            ctrl,
            text="📂 Buka Folder",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            width=115,
            height=28,
            command=self._open_cleaner_downloads_folder
        )
        btn_open_dl.pack(side="right", padx=(4, 10), pady=9)

        # Refresh Registry & Installed Apps Button
        btn_refresh_apps = ctk.CTkButton(
            ctrl,
            text="🔄 Segarkan Status",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#0369A1",
            hover_color="#0284C7",
            width=135,
            height=28,
            command=self._load_native_catalog
        )
        btn_refresh_apps.pack(side="right", padx=(4, 4), pady=9)

        # Header Columns
        col_hdr = ctk.CTkFrame(container, corner_radius=4, fg_color="#0F172A", height=28)
        col_hdr.pack(fill="x", padx=0, pady=(0, 2))
        col_hdr.pack_propagate(False)

        ctk.CTkLabel(col_hdr, text="Kategori", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B", width=140, anchor="w").pack(side="left", padx=(12, 4))
        ctk.CTkLabel(col_hdr, text="Aplikasi & Deskripsi", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B", anchor="w").pack(side="left", fill="x", expand=True, padx=4)
        ctk.CTkLabel(col_hdr, text="Status Sistem", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B", width=160, anchor="center").pack(side="right", padx=(4, 230))
        ctk.CTkLabel(col_hdr, text="Aksi Instalasi & Uninstall", font=ctk.CTkFont(size=11, weight="bold"), text_color="#64748B", width=220, anchor="center").pack(side="right", padx=(4, 12))

        # Scrollable Cards Area
        self.native_app_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.native_app_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self.native_app_data = []
        self.native_app_status_labels = {}
        self.native_app_buttons = {}
        self.native_app_uninstall_buttons = {}
        self.native_app_cancel_buttons = {}
        self.active_installer_processes = {}  # {app_id: subprocess.Popen}
        self.active_download_cancellations = {} # {app_id: bool}
        self._load_native_catalog()


    def _get_cleaner_downloads_dir(self):
        dl_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Cleaner_App_Installers")
        os.makedirs(dl_dir, exist_ok=True)
        return dl_dir


    def _open_cleaner_downloads_folder(self):
        dl_dir = self._get_cleaner_downloads_dir()
        os.startfile(dl_dir)


    def _scan_installed_registry_apps(self):
        """Memindai registry Windows untuk mendeteksi software yang terpasang di sistem."""
        roots = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        installed = {}
        for root, path in roots:
            try:
                k = winreg.OpenKey(root, path)
                num_subkeys = winreg.QueryInfoKey(k)[0]
                for i in range(num_subkeys):
                    try:
                        sk_name = winreg.EnumKey(k, i)
                        sk = winreg.OpenKey(k, sk_name)
                        disp_name = None
                        disp_ver = ""
                        try:
                            disp_name, _ = winreg.QueryValueEx(sk, "DisplayName")
                        except Exception:
                            pass
                        try:
                            disp_ver, _ = winreg.QueryValueEx(sk, "DisplayVersion")
                        except Exception:
                            pass

                        if disp_name and disp_name.strip():
                            name_clean = disp_name.strip()
                            uninst = None
                            quiet_uninst = None
                            try:
                                uninst, _ = winreg.QueryValueEx(sk, "UninstallString")
                            except Exception:
                                pass
                            try:
                                quiet_uninst, _ = winreg.QueryValueEx(sk, "QuietUninstallString")
                            except Exception:
                                pass

                            installed[name_clean.lower()] = {
                                "display_name": name_clean,
                                "version": str(disp_ver),
                                "uninstall_string": uninst,
                                "quiet_uninstall_string": quiet_uninst,
                                "key": sk_name
                            }
                        winreg.CloseKey(sk)
                    except Exception:
                        continue
                winreg.CloseKey(k)
            except Exception:
                continue

        return installed


    def _load_native_catalog(self):
        cat_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_catalog.json")
        self.native_app_data = []
        if os.path.exists(cat_file):
            try:
                with open(cat_file, "r", encoding="utf-8") as f:
                    items = json.load(f)
                if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
                    raise ValueError("Katalog harus berupa daftar objek aplikasi")
                self.native_app_data = items
            except Exception as e:
                self.log(f"Gagal membaca app_catalog.json: {e}")
        else:
            self.log("Katalog App Setup tidak tersedia; daftar aplikasi kosong.")

        # Pindai registry Windows untuk deteksi status & perintah uninstall
        self.installed_registry_map = self._scan_installed_registry_apps()
        self._render_native_apps(self.native_app_data)


    def _render_native_apps(self, items):
        for w in self.native_app_scroll.winfo_children():
            w.destroy()

        self.native_app_status_labels.clear()
        self.native_app_buttons.clear()
        self.native_app_uninstall_buttons.clear()

        dl_dir = self._get_cleaner_downloads_dir()

        for idx, item in enumerate(items):
            app_id = item.get("id", "")
            name = item.get("name", "Software")
            cat = item.get("category", "General")
            desc = item.get("desc", "")
            fname = item.get("filename", "")
            url = item.get("url", "")
            pat = item.get("reg_pattern", "").lower()
            default_uninst = item.get("default_uninstall", "")
            target_path = os.path.join(dl_dir, fname)

            # Cek kecocokan di registry Windows
            reg_match = None
            if pat and hasattr(self, 'installed_registry_map'):
                for rk, rv in self.installed_registry_map.items():
                    if pat in rk:
                        reg_match = rv
                        break

            is_installed = reg_match is not None
            is_downloaded = os.path.exists(target_path)

            card = ctk.CTkFrame(self.native_app_scroll, corner_radius=6, fg_color="#18191C" if idx % 2 == 0 else "#141517", height=60)
            card.pack(fill="x", padx=0, pady=2)
            card.pack_propagate(False)

            # Category badge
            ctk.CTkLabel(
                card,
                text=cat,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#38BDF8",
                width=140,
                anchor="w"
            ).pack(side="left", padx=(12, 4))

            # Title & Desc
            info_f = ctk.CTkFrame(card, fg_color="transparent")
            info_f.pack(side="left", fill="both", expand=True, padx=4, pady=6)

            title_txt = name
            if is_installed and reg_match.get("version"):
                title_txt += f"  (v{reg_match.get('version')})"

            lbl_t = ctk.CTkLabel(info_f, text=title_txt, font=ctk.CTkFont(size=12, weight="bold"), text_color="#F8FAFC", anchor="w")
            lbl_t.pack(anchor="w")

            lbl_d = ctk.CTkLabel(info_f, text=desc[:85] + ("..." if len(desc) > 85 else ""), font=ctk.CTkFont(size=10), text_color="#94A3B8", anchor="w")
            lbl_d.pack(anchor="w")

            # Action Buttons Container (Right side)
            btn_box = ctk.CTkFrame(card, fg_color="transparent")
            btn_box.pack(side="right", padx=(4, 12), pady=12)

            is_portable = item.get("is_portable", False)
            local_src = item.get("local_source", "")

            # Tombol Batal / Cancel (Awalnya tersembunyi / disabled)
            btn_cancel = ctk.CTkButton(
                btn_box,
                text="✕ Batal",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#64748B",
                hover_color="#475569",
                width=75,
                height=28,
                state="disabled",
                command=lambda aid=app_id, it=item: self._cancel_native_app_action(aid, it)
            )
            btn_cancel.pack(side="right", padx=(4, 0))
            self.native_app_cancel_buttons[app_id] = btn_cancel

            # Tombol Uninstall (jika terpasang & bukan portable)
            if not is_portable and (is_installed or default_uninst):
                btn_uninst = ctk.CTkButton(
                    btn_box,
                    text="Copot / Uninstall",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    fg_color="#DC2626" if is_installed else "#475569",
                    hover_color="#B91C1C" if is_installed else "#334155",
                    width=110,
                    height=28,
                    state="normal" if is_installed else "disabled",
                    command=lambda it=item, rm=reg_match: self._uninstall_native_app_async(it, rm)
                )
                btn_uninst.pack(side="right", padx=(4, 0))
                self.native_app_uninstall_buttons[app_id] = btn_uninst

            # Tombol Install / Download / Jalankan Portable
            if is_portable:
                install_btn_text = "🚀 Buka Portable"
                install_btn_fg = "#059669"
                install_btn_hover = "#047857"
            else:
                install_btn_text = "Pasang Lagi" if is_installed else ("Pasang / Install" if is_downloaded else "Unduh & Pasang")
                install_btn_fg = "#16A34A" if is_downloaded else "#0284C7"
                install_btn_hover = "#15803D" if is_downloaded else "#0369A1"

            btn_action = ctk.CTkButton(
                btn_box,
                text=install_btn_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=install_btn_fg,
                hover_color=install_btn_hover,
                width=110,
                height=28,
                command=lambda it=item: self._download_and_install_native_app_async(it)
            )
            btn_action.pack(side="right", padx=(0, 4))
            self.native_app_buttons[app_id] = btn_action

            # Status Label
            if is_portable:
                init_status = "✓ Siap Pakai (Portable)"
                init_color = "#34D399"
            elif is_installed:
                init_status = "✓ Terpasang di OS"
                init_color = "#4ADE80"
            elif is_downloaded:
                init_status = "File Tersedia (Siap)"
                init_color = "#38BDF8"
            else:
                init_status = "Belum Terpasang"
                init_color = "#94A3B8"

            lbl_st = ctk.CTkLabel(
                card,
                text=init_status,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=init_color,
                width=160,
                anchor="center"
            )
            lbl_st.pack(side="right", padx=(4, 10))
            self.native_app_status_labels[app_id] = lbl_st


    def _filter_native_apps(self):
        q = self.native_app_search.get().lower().strip()
        cat = self.native_app_cat.get()

        res = []
        for it in self.native_app_data:
            if cat != "Semua Kategori" and it.get("category") != cat:
                continue
            if q:
                if q not in it.get("name", "").lower() and q not in it.get("desc", "").lower():
                    continue
            res.append(it)
        self._render_native_apps(res)


    def _uninstall_native_app_async(self, item, reg_match=None):
        name = item.get("name", "Software")
        app_id = item.get("id", "")
        default_uninst = item.get("default_uninstall", "")

        # Tentukan perintah uninstalasi yang valid
        uninst_cmd = None
        if reg_match:
            uninst_cmd = reg_match.get("quiet_uninstall_string") or reg_match.get("uninstall_string")

        if not uninst_cmd:
            uninst_cmd = default_uninst

        if not uninst_cmd:
            messagebox.showwarning("Uninstall", f"Tidak ditemukan perintah uninstalasi resmi untuk {name}.")
            return

        confirm = messagebox.askyesno(
            "Konfirmasi Copot Pemasangan",
            f"Apakah Anda yakin ingin mencopot (uninstall) {name} secara native tanpa CMD?\n\nPerintah:\n{uninst_cmd}"
        )
        if not confirm:
            return

        lbl = self.native_app_status_labels.get(app_id)
        btn_uninst = self.native_app_uninstall_buttons.get(app_id)
        if btn_uninst and btn_uninst.winfo_exists():
            btn_uninst.configure(state="disabled")

        if lbl and lbl.winfo_exists():
            lbl.configure(text="Mencopot...", text_color="#EF4444")

        def _worker():
            self.log(f"Menjalankan uninstaller native di background: {uninst_cmd}...")
            try:
                # Menjalankan uninstaller di background tanpa membuka jendela CMD (CREATE_NO_WINDOW)
                proc = subprocess.run(
                    uninst_cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    creationflags=hidden_console_creation_flags()
                )
                self.log(f"Proses uninstall {name} selesai dengan returncode: {proc.returncode}")

                # Refresh registry status
                self.installed_registry_map = self._scan_installed_registry_apps()
                self.after(0, self._filter_native_apps)

                messagebox.showinfo("Copot Berhasil", f"Proses uninstalasi {name} telah selesai dijalankan.")
            except Exception as e:
                self.log(f"Gagal mencopot {name}: {e}")
                if lbl and lbl.winfo_exists():
                    self.after(0, lambda: lbl.configure(text="Gagal Uninstall", text_color="#EF4444"))
                if btn_uninst and btn_uninst.winfo_exists():
                    self.after(0, lambda: btn_uninst.configure(state="normal"))
                messagebox.showerror("Gagal Uninstall", f"Terjadi kesalahan saat mencopot {name}:\n{e}")

        self.executor.submit(_worker)


    def _cancel_native_app_action(self, app_id, item):
        name = item.get("name", "Software")
        self.log(f"Tombol Batal ditekan untuk: {name} (ID: {app_id})")

        # 1. Tandai flag download cancellation
        self.active_download_cancellations[app_id] = True

        # 2. Hentikan proses installer aktif jika ada
        proc = self.active_installer_processes.get(app_id)
        if proc:
            try:
                p = psutil.Process(proc.pid)
                children = p.children(recursive=True)
                for child in children:
                    try:
                        self.log(f"Mematikan child process: PID {child.pid} ({child.name()})")
                        child.kill()
                    except Exception:
                        pass
                p.kill()
                self.log(f"Proses installer {name} (PID: {proc.pid}) berhasil dihentikan!")
            except Exception as e:
                self.log(f"Info/error saat menghentikan proses installer {name}: {e}")

        lbl = self.native_app_status_labels.get(app_id)
        if lbl and lbl.winfo_exists():
            lbl.configure(text="Dibatalkan", text_color="#EF4444")

        btn = self.native_app_buttons.get(app_id)
        if btn and btn.winfo_exists():
            btn.configure(state="normal")

        btn_cancel = self.native_app_cancel_buttons.get(app_id)
        if btn_cancel and btn_cancel.winfo_exists():
            btn_cancel.configure(state="disabled")


    def _download_and_install_native_app_async(self, item):
        app_id = item.get("id")
        name = item.get("name")
        url = item.get("url")
        fname = item.get("filename")
        app_type = item.get("type", "exe")
        silent_args = item.get("silent_args", "")
        is_portable = item.get("is_portable", False)
        local_src = item.get("local_source", "")
        local_setup = item.get("local_setup", "")
        executable = item.get("executable", fname)

        # Handle Portable Application Directly
        if is_portable:
            exe_target = os.path.join(local_src, executable) if local_src else fname
            if not os.path.exists(exe_target):
                messagebox.showerror("File Tidak Ditemukan", f"Executable portable tidak ditemukan di:\n{exe_target}")
                return
            self.log(f"Meluncurkan aplikasi portable: {exe_target}...")
            try:
                subprocess.Popen(
                    [exe_target],
                    cwd=local_src if local_src else None,
                    shell=False
                )
                lbl = self.native_app_status_labels.get(app_id)
                if lbl and lbl.winfo_exists():
                    lbl.configure(text="✓ Berjalan (Portable)", text_color="#34D399")
                self.log(f"Aplikasi portable {name} berhasil dibuka!")
            except Exception as e:
                self.log(f"Gagal membuka aplikasi portable {name}: {e}")
                messagebox.showerror("Gagal Membuka", f"Gagal menjalankan portable:\n{e}")
            return

        dl_dir = self._get_cleaner_downloads_dir()
        dest_file = os.path.join(dl_dir, fname)

        lbl = self.native_app_status_labels.get(app_id)
        btn = self.native_app_buttons.get(app_id)
        btn_cancel = self.native_app_cancel_buttons.get(app_id)

        if btn and btn.winfo_exists():
            btn.configure(state="disabled")

        if btn_cancel and btn_cancel.winfo_exists():
            btn_cancel.configure(state="normal", fg_color="#DC2626", hover_color="#B91C1C")

        # Reset cancel flag
        self.active_download_cancellations[app_id] = False

        def _worker():
            try:
                # Step 1: Download or copy from local_setup
                if local_setup and os.path.exists(local_setup):
                    installer_file = local_setup
                    self.log(f"Menggunakan biner setup lokal: {installer_file}")
                else:
                    installer_file = dest_file
                    if not os.path.exists(dest_file) or os.path.getsize(dest_file) < 1024:
                        if not url:
                            self.log(f"Gagal: URL untuk {name} kosong dan file lokal tidak ditemukan.")
                            if lbl and lbl.winfo_exists():
                                self.after(0, lambda: lbl.configure(text="Setup Tidak Ada", text_color="#EF4444"))
                            if btn and btn.winfo_exists():
                                self.after(0, lambda: btn.configure(state="normal"))
                            if btn_cancel and btn_cancel.winfo_exists():
                                self.after(0, lambda: btn_cancel.configure(state="disabled", fg_color="#64748B"))
                            return

                        self.log(f"Memulai pengunduhan mandiri: {name} dari {url}...")
                        if lbl and lbl.winfo_exists():
                            self.after(0, lambda: lbl.configure(text="Mengunduh... 0%", text_color="#38BDF8"))

                        try:
                            req = urllib.request.Request(
                                url,
                                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                            )
                            with urllib.request.urlopen(req, timeout=30) as resp:
                                total_length = resp.headers.get("content-length")
                                total_length = int(total_length) if total_length else None

                                downloaded = 0
                                block_size = 64 * 1024
                                with open(dest_file, "wb") as f_out:
                                    while True:
                                        if self.active_download_cancellations.get(app_id, False):
                                            self.log(f"Pengunduhan {name} dibatalkan oleh pengguna.")
                                            f_out.close()
                                            try:
                                                os.remove(dest_file)
                                            except Exception:
                                                pass
                                            return
                                        chunk = resp.read(block_size)
                                        if not chunk:
                                            break
                                        f_out.write(chunk)
                                        downloaded += len(chunk)
                                        if total_length and total_length > 0:
                                            pct = int((downloaded / total_length) * 100)
                                            if lbl and lbl.winfo_exists():
                                                self.after(0, lambda p=pct: lbl.configure(text=f"Mengunduh... {p}%", text_color="#38BDF8"))

                            self.log(f"Pengunduhan selesai: {dest_file} ({downloaded // 1024} KB)")
                        except Exception as e:
                            if self.active_download_cancellations.get(app_id, False):
                                return
                            self.log(f"Gagal mengunduh {name}: {e}")
                            if lbl and lbl.winfo_exists():
                                self.after(0, lambda: lbl.configure(text="Gagal Unduh", text_color="#EF4444"))
                            if btn and btn.winfo_exists():
                                self.after(0, lambda: btn.configure(state="normal"))
                            if btn_cancel and btn_cancel.winfo_exists():
                                self.after(0, lambda: btn_cancel.configure(state="disabled", fg_color="#64748B"))
                            messagebox.showerror("Gagal Unduh", f"Tidak dapat mengunduh installer {name}.\nError: {e}")
                            return

                # Check cancellation before setup
                if self.active_download_cancellations.get(app_id, False):
                    return

                # Step 2: Install Execution
                if lbl and lbl.winfo_exists():
                    self.after(0, lambda: lbl.configure(text="Memasang (Setup)...", text_color="#FDE047"))
                self.log(f"Menjalankan installer setup: {installer_file} {silent_args}...")

                try:
                    if app_type == "msi":
                        cmd = f'msiexec.exe /i "{installer_file}" {silent_args}'
                    else:
                        cmd = f'"{installer_file}" {silent_args}'

                    proc = subprocess.Popen(
                        cmd,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=0x08000000 if os.name == 'nt' else 0
                    )
                    self.active_installer_processes[app_id] = proc
                    stdout, stderr = proc.communicate()
                    returncode = proc.returncode
                    self.active_installer_processes.pop(app_id, None)

                    if self.active_download_cancellations.get(app_id, False):
                        self.log(f"Instalasi {name} dibatalkan.")
                        return

                    self.log(f"Setup {name} selesai dengan return code: {returncode}")

                    # Update status registry
                    self.installed_registry_map = self._scan_installed_registry_apps()
                    self.after(0, self._filter_native_apps)

                    if returncode == 0:
                        messagebox.showinfo("Setup Selesai", f"Aplikasi {name} berhasil dipasang di komputer!")

                except Exception as e:
                    self.log(f"Gagal menjalankan installer {name}: {e}")
                    if lbl and lbl.winfo_exists():
                        self.after(0, lambda: lbl.configure(text="Error Setup", text_color="#EF4444"))
                    if btn and btn.winfo_exists():
                        self.after(0, lambda: btn.configure(state="normal"))
            finally:
                if btn_cancel and btn_cancel.winfo_exists():
                    self.after(0, lambda: btn_cancel.configure(state="disabled", fg_color="#64748B"))

        self.executor.submit(_worker)


    def run_dism_restorehealth(self):
        if not messagebox.askyesno("DISM RestoreHealth", "Jalankan 'dism /online /cleanup-image /restorehealth' untuk memperbaiki Windows Image via online?"):
            return
        self.log("Memulai dism /online /cleanup-image /restorehealth...")
        def _bg():
            p = subprocess.Popen(
                ["dism.exe", "/online", "/cleanup-image", "/restorehealth"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=hidden_console_creation_flags()
            )
            for line in iter(p.stdout.readline, ''):
                if line.strip():
                    self.log(f"[DISM] {line.strip()}")
            p.stdout.close()
            p.wait()
            self.log(f"DISM RestoreHealth selesai dengan kode status: {p.returncode}")
            messagebox.showinfo("DISM RestoreHealth", "Perbaikan citra sistem Windows selesai!")
        self.executor.submit(_bg)


    def clean_windows_update_cache(self):
        self.log("Membersihkan cache instalasi Windows Update...")
        def _bg():
            try:
                subprocess.run(["sc.exe", "stop", "wuauserv"], capture_output=True, creationflags=hidden_console_creation_flags())
                time.sleep(1)
                cache_dir = os.path.join(os.getenv("WINDIR", "C:\\Windows"), "SoftwareDistribution", "Download")
                freed = 0
                if os.path.exists(cache_dir):
                    freed = get_directory_size_bytes(cache_dir)
                    for root, dirs, files in os.walk(cache_dir, topdown=False):
                        for f in files:
                            try:
                                os.remove(os.path.join(root, f))
                            except Exception:
                                pass
                        for d in dirs:
                            try:
                                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                            except Exception:
                                pass
                subprocess.run(["sc.exe", "start", "wuauserv"], capture_output=True, creationflags=hidden_console_creation_flags())
                self.log(f"SUKSES: Cache update dibersihkan ({format_size(freed)} ruang disk dihemat).")
                messagebox.showinfo("Windows Update Cache", f"Cache update berhasil dibersihkan! {format_size(freed)} dihemat.")
            except Exception as e:
                self.log(f"Gagal membersihkan cache update: {e}")
        self.executor.submit(_bg)


    def check_vcredist_status(self):
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(k, "Installed")
            if val == 1:
                return "Terinstal (x64)"
        except Exception:
            pass
        return "Belum Terdeteksi"


    def check_dotnet_status(self):
        try:
            res = subprocess.run(["dotnet", "--list-runtimes"], capture_output=True, text=True, creationflags=hidden_console_creation_flags())
            if res.returncode == 0 and "Microsoft.WindowsDesktop.App" in res.stdout:
                return "Terinstal (.NET Desktop)"
        except Exception:
            pass
        return "Siap Diinstal"


    def _load_ghost_urls_data(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ghost_toolbox_urls.json")
        if not os.path.exists(json_path):
            json_path = r"D:\coding\Cleaner_Windows\ghost_toolbox_urls.json"

        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.ghost_url_data = json.load(f)
            except Exception as e:
                self.log(f"Gagal membaca ghost_toolbox_urls.json: {e}")
                self.ghost_url_data = []

        self._render_ghost_url_table(self.ghost_url_data)


    def _render_ghost_url_table(self, items):
        for widget in self.ghost_url_table_frame.winfo_children():
            widget.destroy()

        self.ghost_url_status_labels.clear()
        self.lbl_ghost_url_count.configure(text=f"{len(items)} / {len(self.ghost_url_data)} URL")

        # Display first 150 items to keep UI snappy, or all if filtered
        display_items = items[:120] if len(items) > 120 and self.ghost_url_search.get() == "" else items

        for idx, it in enumerate(display_items):
            url = it.get("url", "")
            cat = it.get("category", "Tools & Tweaks")
            name = it.get("name", "Toolbox Item")

            row = ctk.CTkFrame(self.ghost_url_table_frame, corner_radius=4, fg_color="#18191C" if idx % 2 == 0 else "#141517", height=34)
            row.pack(fill="x", padx=0, pady=1)
            row.pack_propagate(False)

            # Category
            ctk.CTkLabel(
                row,
                text=cat,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#38BDF8",
                width=120,
                anchor="w"
            ).pack(side="left", padx=(10, 4))

            # Name
            ctk.CTkLabel(
                row,
                text=name[:32],
                font=ctk.CTkFont(size=11),
                text_color="#F1F5F9",
                width=220,
                anchor="w"
            ).pack(side="left", padx=4)

            # URL
            lbl_u = ctk.CTkLabel(
                row,
                text=url,
                font=ctk.CTkFont(family="Consolas", size=10),
                text_color="#94A3B8",
                anchor="w"
            )
            lbl_u.pack(side="left", fill="x", expand=True, padx=4)

            # Open Button
            btn_open = ctk.CTkButton(
                row,
                text="Buka Link",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#334155",
                hover_color="#475569",
                width=75,
                height=22,
                command=lambda u=url: webbrowser.open(u)
            )
            btn_open.pack(side="right", padx=(4, 10))

            # Status Badge
            lbl_st = ctk.CTkLabel(
                row,
                text="Belum Dicek",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#64748B",
                width=90,
                anchor="center"
            )
            lbl_st.pack(side="right", padx=(4, 10))
            self.ghost_url_status_labels[url] = lbl_st

        if len(items) > len(display_items):
            info_lbl = ctk.CTkLabel(
                self.ghost_url_table_frame,
                text=f"... Menampilkan {len(display_items)} dari total {len(items)} URL. Gunakan kolom pencarian di atas untuk memfilter secara spesifik ...",
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="#64748B"
            )
            info_lbl.pack(pady=8)


    def _filter_ghost_url_table(self):
        query = self.ghost_url_search.get().lower().strip()
        cat = self.ghost_url_cat_filter.get()

        filtered = []
        for it in self.ghost_url_data:
            if cat != "Semua Kategori" and it.get("category") != cat:
                continue
            if query:
                if query not in it.get("name", "").lower() and query not in it.get("url", "").lower() and query not in it.get("category", "").lower():
                    continue
            filtered.append(it)

        self._render_ghost_url_table(filtered)


    def check_all_ghost_urls_async(self):
        self.log("Memulai pengecekan live vs dead link untuk URL System Toolbox...")
        visible_urls = list(self.ghost_url_status_labels.keys())
        if not visible_urls:
            messagebox.showinfo("Info", "Tidak ada URL yang ditampilkan untuk dicek.")
            return

        def _check_worker():
            for u in visible_urls:
                try:
                    req = urllib.request.Request(
                        u,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    )
                    # Use timeout of 4 seconds
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        code = resp.getcode()
                        if code in (200, 301, 302, 303, 307, 308):
                            st_text = f"AKTIF ({code})"
                            color = "#4ADE80"
                        else:
                            st_text = f"HTTP {code}"
                            color = "#FDE047"
                except Exception as e:
                    err_str = str(e).lower()
                    if "404" in err_str or "not found" in err_str:
                        st_text = "DEAD (404)"
                        color = "#F87171"
                    elif "timeout" in err_str:
                        st_text = "TIMEOUT"
                        color = "#F97316"
                    else:
                        st_text = "ERROR"
                        color = "#EF4444"

                lbl = self.ghost_url_status_labels.get(u)
                if lbl and lbl.winfo_exists():
                    self.after(0, lambda l=lbl, t=st_text, c=color: l.configure(text=t, text_color=c))

            self.log("Pemeriksaan status URL System Toolbox selesai.")

        self.executor.submit(_check_worker)


    def install_runtime_winget(self, pkg_id):
        self.log(f"Menjalankan instalasi paket runtime: winget install {pkg_id}...")
        def _bg():
            cmd = f'winget install --id {pkg_id} --exact --accept-package-agreements --accept-source-agreements'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                self.log(f"SUKSES: {pkg_id} berhasil diinstal!")
                messagebox.showinfo("Instalasi Selesai", f"Paket {pkg_id} berhasil diinstal!")
            else:
                self.log(f"Winget: {res.stdout.strip() or res.stderr.strip()}")
                messagebox.showinfo("Info Winget", f"Proses installer telah dijalankan.\n{res.stdout[:150]}")
        self.executor.submit(_bg)


    def setup_log_drawer(self):
        log_frame = ctk.CTkFrame(self.content_area, corner_radius=8, fg_color="#18191C", height=100)
        log_frame.pack(side="bottom", fill="x", padx=12, pady=(6, 10))
        log_frame.pack_propagate(False)

        top_bar = ctk.CTkFrame(log_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(4, 0))

        lbl_log = ctk.CTkLabel(top_bar, text="Log Aktivitas & Eksekusi Real-time:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#94A3B8")
        lbl_log.pack(side="left")

        btn_clr = ctk.CTkButton(top_bar, text="Bersihkan Log", width=80, height=20, fg_color="#334155", font=ctk.CTkFont(size=10), command=self.clear_log)
        btn_clr.pack(side="right")

        self.log_box = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=10), fg_color="#0F172A", text_color="#CBD5E1")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(2, 6))


    def log(self, text):
        def _append():
            ts = time.strftime("%H:%M:%S")
            self.log_box.insert("end", f"[{ts}] {text}\n")
            self.log_box.see("end")
        self.after(0, _append)


    def clear_log(self):
        self.log_box.delete("1.0", "end")


if __name__ == "__main__":
    app = DevAICleanerApp()
    app.mainloop()
