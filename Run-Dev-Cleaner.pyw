"""Console-free Windows entrypoint for DevAICleaner."""

from __future__ import annotations

import os
import sys
import traceback

if sys.platform != "win32":
    raise SystemExit("DevAICleaner is designed for Windows environments.")


def main() -> None:
    try:
        import dev_cleaner

        app = dev_cleaner.DevAICleanerApp()
        app.mainloop()
    except Exception as exc:
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()
            error_details = traceback.format_exc()
            messagebox.showerror(
                "Dev & AI CLI Cleaner - Startup Error",
                f"Aplikasi gagal dijalankan:\n\n{exc}\n\nDetail:\n{error_details}",
            )
            root.destroy()
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
