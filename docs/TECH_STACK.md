# Tech Stack — Dev & AI Cleaner

**Snapshot:** 18 Oktober 2026. Entry point utama: `dev_cleaner.py`.

## Arsitektur aktual

- **Python:** modul utama berisi helper filesystem/registry/state, pemindai, worker operasi dan kelas `DevAICleanerApp`.
- **GUI:** `tkinter`, `ttk`, **ttkbootstrap**. `_BootstrapUIAdapter` menyediakan nama widget kompatibel CTk (`CTkFrame`, `CTkButton`, dan lainnya) dan menjadi objek `ctk`. Nama `ctk` bukan bukti widget masih dirender CustomTkinter. Ini desktop Tk, bukan Bootstrap web/WebView.
- **Tema/layout:** ttkbootstrap `darkly`, token warna aplikasi, sidebar enam view, toolbar yang dapat mengalir, panel log bawah. Konversi lebar piksel ke satuan karakter dilakukan untuk widget teks tertentu.
- **Concurrency:** `ThreadPoolExecutor(max_workers=4)`, thread dan flag scan, pengaman mutasi inti; pembaruan GUI dijadwalkan melalui `after(...)`. Tidak semua toolbox mengikuti pengaman inti.
- **State:** JSON lokal; riwayat move disimpan lewat temporary file, flush/fsync dan `os.replace`. Preferensi startup menyimpan boolean, bukan seluruh state GUI.
- **Verifikasi:** manifest hash SHA-256 untuk alur copy/restore yang terkait, pengecekan junction/reparse point, verifikasi paket via interpreter yang sama, ekspor `reg.exe` sebelum penghapusan registry, serta verifikasi hasil mutasi sesuai alur.

## Dependensi dan snapshot lokal

Versi berikut diambil dari metadata paket **terpasang pada mesin pengembangan**, bukan dependency lock atau kombinasi yang dijamin di mesin lain.

| Komponen | Versi teramati | Peran |
|---|---|---|
| Python | 3.11.9 AMD64 | Runtime yang diamati; target sumber Python 3.10+ x64 |
| ttkbootstrap | 2.2.3 | Runtime GUI langsung |
| psutil | 7.2.2 | Runtime informasi sistem/proses/layanan |
| Send2Trash | 2.1.0 | Runtime Recycle Bin |
| Pillow | 12.3.0 | Dependency transitif GUI/aset dalam environment teramati |
| CustomTkinter | 6.0.0 | Dikoleksi spec saat ini; bukan implementasi widget utama |
| darkdetect | 0.8.0 | Dikoleksi spec/dukungan dependency terkait |
| pywin32 | 312 | Penyedia hidden imports Windows dalam spec |
| PyInstaller | 6.3.0 | Build, bukan kebutuhan menjalankan sumber |

Standard library mencakup `tkinter`, `winreg`, `ctypes`, `subprocess`, `pathlib`, `tempfile`, `json`, `hashlib`, `importlib.metadata`, `urllib.request`, dan `concurrent.futures`. Tidak dipasang terpisah melalui pip. Paket transitif/native perlu diperiksa kembali untuk setiap build; tabel ini bukan SBOM lengkap. Lisensi metadata tertentu berbeda dari teks yang dikirim paket: lihat [third-party notices](THIRD_PARTY_NOTICES.md).

## Integrasi Windows

- `winreg`: uninstall entries, penemuan Python, kandidat registry yatim, startup, dan tweak tertentu.
- `psutil`: disk/ruang bebas, proses serta layanan Windows. Proses aplikasi terkait dapat dihentikan saat pemindahan.
- `robocopy` dan `cmd.exe / mklink /J`: copy folder dan junction NTFS. Robocopy/junction bukan migrasi instalasi lintas mesin.
- `reg.exe export`: backup `.reg` sebelum penghapusan registry terkait.
- `sc.exe`, DISM, SFC, powercfg, ipconfig, wsreset, cscript: tindakan toolbox/layanan sesuai tombol. Adanya helper tidak berarti semua helper adalah fitur UI publik.
- `urllib`/`webbrowser`: pemeriksaan tautan, unduhan dan pembukaan situs runtime; core scan tidak membutuhkan backend.
- `ctypes.windll.shell32.IsUserAnAdmin`: pemeriksaan privilege. Hak admin tidak membuat target otomatis aman.

## Packaging dan launcher

`Dev-AI-Cleaner.spec` menganalisis `dev_cleaner.py`, memakai `collect_all` untuk ttkbootstrap/CustomTkinter/darkdetect dan hidden imports `win32api`, `win32con`, `win32process`, `win32gui`, `winreg`, `psutil`, `send2trash`, `importlib.metadata`. `EXE(..., console=False)` menghasilkan `dist/Dev-AI-Cleaner.exe`; tidak ada tahap COLLECT terpisah dalam spec saat ini.

`Run-Dev-Cleaner.pyw` adalah launcher Windows tanpa konsol dengan fallback dialog startup error. Launcher `.bat` lama memasang sebagian paket secara tidak terkunci; rute utama setup adalah virtual environment di [panduan instalasi](INSTALLATION.md).

Helper `hidden_console_creation_flags()` memakai `CREATE_NO_WINDOW` untuk subprocess konsol Windows terkait, sambil mempertahankan keluaran/exit status pada jalur yang menangkapnya. Ini bukan jaminan setiap jendela program pihak ketiga tersembunyi; installer/aplikasi interaktif tetap mempunyai lifecycle sendiri.

## State dan katalog

State utama di `%LOCALAPPDATA%\DevAICleaner`: `moves.json`, `preferences.json`, `RegistryBackups`, `py_libs_debug.log`. Riwayat lokal mandiri; tidak membaca riwayat aplikasi eksternal otomatis. Download installer lokal memakai `%USERPROFILE%\Downloads\Cleaner_App_Installers`.

Tidak ada katalog publik `app_catalog.json` atau kumpulan installer yang dibundel. App Setup kosong pada checkout bersih adalah perilaku yang harus dijelaskan, bukan diatasi dengan path fallback ke katalog privat. Katalog lokal/installer harus diperlakukan sebagai input berisiko tinggi. Spec saat ini bukan mekanisme distribusi katalog publik.

## Pengujian dan batas bukti

- `unittest` dalam `tests/` mencakup preferensi/fitur inti, mutasi, move/history/restore, library, registry, duplikat, dan layout/bootstrap sesuai tes yang tersedia.
- Baseline dilaporkan **74 tes lulus**, sekitar 15,923 detik pada satu run. Angka dapat berubah dengan tes baru; lihat hasil run aktual, bukan klaim CI.
- Mesin yang diamati: Windows 11 build 26300 dengan Python 3.11.9 AMD64; GUI smoke lokal saja tidak memverifikasi semua operasi destruktif/bundel.
- Windows 10/VM bersih, ARM/32-bit, variasi DPI, serta semua installer/volume/updater belum terverifikasi.
- Belum ada lockfile otoritatif, CI build terverifikasi, proses signing, inventaris lisensi bundel lengkap atau benchmark RAM/performa yang mendukung klaim universal.

Publikasi harus melewati [checklist publikasi](PUBLICATION_CHECKLIST.md), termasuk konflik lisensi/provenance dan histori, bukan sekadar menjalankan build.
