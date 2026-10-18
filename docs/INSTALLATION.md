# Instalasi, pengujian, dan build

## Prasyarat

- Target Windows 10/11 x64, Python 3.10+ x64 dengan Tkinter/Tcl/Tk. Lingkungan yang diamati: Python 3.11.9 AMD64 pada Windows 11 build 26300.
- Akses tulis ke checkout, virtual environment, dan direktori data lokal. Untuk sebagian operasi sistem dibutuhkan Administrator; tidak diperlukan untuk sekadar memasang paket ke virtual environment.
- Jaringan untuk instalasi pip dan tindakan daring. Pemindaian inti tidak membutuhkan katalog daring.
- Tool Windows sesuai fitur: `robocopy`, `cmd.exe`/`mklink`, `reg.exe`, `sc.exe`, `dism`, `sfc`, `powercfg`, `ipconfig`, `wsreset.exe`, serta `cscript.exe`. Tidak semuanya dibutuhkan untuk membuka GUI.

Windows 10, VM bersih, ARM/32-bit, dan variasi DPI belum diverifikasi. Tidak ada minimum RAM/ruang universal yang sudah diukur; operasi copy/restore membutuhkan ruang untuk staging dan salinan, bukan hanya ukuran akhir.

## Menjalankan sumber

Buka direktori proyek di PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ttkbootstrap psutil send2trash
.\.venv\Scripts\python.exe dev_cleaner.py
```

`py -3` memakai Python 3 default pada launcher Windows. Periksa versi/arsitektur interpreter yang dipilih sebelum membuat environment; pilih instalasi x64 yang sesuai. Jika `py` tidak tersedia, gunakan path lengkap `python.exe` instalasi Anda. Perintah tidak memerlukan aktivasi `.venv` atau pelonggaran kebijakan skrip PowerShell.

Dependensi runtime langsung:

| Paket | Peran |
|---|---|
| `ttkbootstrap` | Widget desktop/Tk melalui adapter kompatibilitas CTk |
| `psutil` | Informasi disk/proses dan integrasi layanan |
| `send2trash` | Recycle Bin pada alur yang mendukungnya |

Pip memasang dependensi transitif yang diminta paket, termasuk Pillow pada lingkungan yang diamati. `tkinter` dan `winreg` bukan paket yang dipasang dengan pip; keduanya berasal dari distribusi Python yang sesuai.

Belum ada lockfile/requirements berversi yang otoritatif. Versi teramati di [Tech Stack](TECH_STACK.md) adalah snapshot mesin pengembangan, bukan pin yang telah lolos pengujian lintas mesin. Simpan inventaris environment untuk reproduksi bug:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip list
```

### Launcher GUI

```powershell
.\.venv\Scripts\pythonw.exe Run-Dev-Cleaner.pyw
```

Launcher `.pyw` mencoba menampilkan dialog error startup tanpa konsol. Untuk diagnosis awal, gunakan `python.exe dev_cleaner.py` agar traceback terlihat. `Run-Dev-Cleaner.bat` lama memasang `customtkinter` dan `send2trash` secara tidak terkunci, tetapi belum mencakup seluruh runtime saat ini; jangan menganggapnya installer lengkap atau rute build reproduktif.

## Menjalankan tes

Dari root proyek, dengan runtime terpasang:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Suite menggunakan `unittest` (standard library); tidak perlu memasang pytest hanya untuk perintah ini. Baseline yang dilaporkan sebelum perubahan publikasi: **74 tes lulus** pada lingkungan lokal, sekitar 15,923 detik pada satu eksekusi. Waktu itu bukan benchmark. Catat hasil terbaru setelah perubahan; jangan menyatakan jumlah baseline sebagai hasil run Anda.

Mock/stub menguji banyak alur tanpa melakukan seluruh operasi sistem nyata. Lulus unit test tidak membuktikan kompatibilitas semua volume NTFS, layanan, installer, atau aplikasi. Smoke GUI hanya memverifikasi peluncuran/interaksi yang diamati.

## Build executable Windows

Tambahkan dependensi khusus spec/build:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller customtkinter darkdetect pywin32
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm Dev-AI-Cleaner.spec
```

- Spec mengoleksi `ttkbootstrap`, `customtkinter`, `darkdetect`, serta hidden imports Windows (`win32api`, `win32con`, `win32process`, `win32gui`), `psutil`, `send2trash`, dan `importlib.metadata`.
- CustomTkinter/darkdetect tetap dibutuhkan oleh **spec saat ini**, walau implementasi widget utama memakai ttkbootstrap. `pywin32` menyediakan modul `win32*` untuk paket Windows.
- Spec menghasilkan executable satu berkas `dist/Dev-AI-Cleaner.exe` dengan `console=False`; file sementara PyInstaller dapat diekstrak saat executable berjalan.
- `build/` dan `dist/` adalah keluaran lokal, bukan sumber atau bukti rilis resmi. Jangan commit installer/download/cache.
- `upx=True` di spec bukan bukti UPX tersedia atau dipakai. Tidak ada proses signing yang terverifikasi; jangan memberi badge signing/CI/rilis.
- Build bukan cross-compile: gunakan Windows dan arsitektur Python target. Uji executable pada mesin/VM terpisah tanpa environment pengembangan sebelum mendistribusikan.

Sebelum distribusi, audit inventaris dependency/transitif, lisensi Python/Tcl/Tk, native DLL, hook PyInstaller, dan semua aset yang benar-benar masuk bundel. Baca [third-party notices](THIRD_PARTY_NOTICES.md) dan [checklist publikasi](PUBLICATION_CHECKLIST.md). Dokumen MIT proyek tidak melisensikan ulang dependensi atau menyelesaikan masalah provenance.

## Memperbarui atau menghapus instalasi sumber

Tutup aplikasi sebelum memperbarui checkout/environment. Simpan backup state lokal dan catat environment yang dipakai. Menghapus `.venv`/checkout tidak otomatis mengembalikan registry, layanan, paket Python lain, atau aplikasi yang telah dipindahkan. Pulihkan App Mover terlebih dahulu bila ingin menghentikan penggunaannya, dan simpan riwayat hingga pemulihan benar-benar selesai.
