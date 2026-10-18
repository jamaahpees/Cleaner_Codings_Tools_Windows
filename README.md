# Dev & AI Cleaner

Utilitas desktop Windows untuk meninjau sampah/cache, memindahkan dan memulihkan folder aplikasi, mencari duplikat, mengelola paket Python, serta mengakses pengaturan startup, layanan, dan alat Windows. Antarmuka menggunakan **Tkinter/ttkbootstrap dengan adapter kompatibilitas CTk**, bukan aplikasi web.

> **Tinjau sebelum bertindak.** Aplikasi dapat menghapus data, mengubah registry/layanan, mencopot paket, dan memindahkan folder aplikasi. Label “Safe” menunjukkan adanya pembatasan, bukan jaminan bebas risiko. Cadangkan data dan uji pada data nonproduksi.

## Enam menu utama

| Menu | Cakupan |
|---|---|
| **Smart Cleaner** | Analisis kategori browser/Windows, cache developer, dependensi proyek, dan kandidat registry yatim; pembersihan item terpilih. Smart Scan saat startup bersifat opsional, default **OFF**, satu kali per peluncuran. |
| **App Mover & Restore** | Kandidat folder aplikasi, pemindahan dengan Robocopy dan junction NTFS, riwayat lokal, restore, serta retry pembersihan pemulihan tertunda. |
| **Duplicate File Finder (Safe)** | Pemindaian folder terpilih dan pemindahan duplikat terpilih ke Recycle Bin dengan pembatasan file/lokasi. |
| **Python Library Manager** | Penemuan interpreter, daftar paket/dependensi, dan uninstall melalui interpreter yang dipilih, dengan verifikasi setelah tindakan. |
| **Startup & Windows Services** | Subview program startup dan layanan Windows; tindakan yang tersedia bergantung pada izin dan status aktual. |
| **System Toolbox (Tweaks & Tools)** | App Setup, Windows Tweaks, System Health & WinSxS, Essential Runtimes, dan App Link Checker. |

**Katalog publik tidak dibundel.** App Setup dapat tampil kosong pada checkout bersih; ini bukan katalog unduhan yang hilang karena instalasi gagal. Jangan mengambil katalog privat atau installer tidak tepercaya untuk mengisinya. Lihat [panduan pengguna](docs/USER_GUIDE.md).

## Tampilan aplikasi

UI asli dengan data demonstrasi. Angka, nama berkas, dan hasil pada gambar bukan hasil pengukuran perangkat Anda.

![Smart Cleaner — UI asli dengan data demonstrasi](docs/images/smart-cleaner.png)

<details>
<summary>Lihat lima menu lainnya</summary>

### App Mover & Restore
![App Mover & Restore — UI asli dengan data demonstrasi](docs/images/app-mover.png)

### Duplicate File Finder (Safe)
![Duplicate File Finder (Safe) — UI asli dengan data demonstrasi](docs/images/duplicates.png)

### Python Library Manager
![Python Library Manager — UI asli dengan data demonstrasi](docs/images/python-libraries.png)

### Startup & Windows Services
![Startup & Windows Services — UI asli dengan data demonstrasi](docs/images/startup-services.png)

### System Toolbox (Tweaks & Tools)
![System Toolbox — UI asli dengan data demonstrasi](docs/images/system-toolbox.png)

</details>

Konteks pengambilan gambar tersedia di [catatan screenshot](docs/SCREENSHOTS.md).

## Status dukungan dan verifikasi

- **Target:** Windows 10/11 **x64**, Python 3.10+ untuk menjalankan sumber. Gunakan Python x64 dengan Tkinter tersedia.
- **Lingkungan yang diamati:** Windows 11 build 26300, Python 3.11.9 AMD64; GUI smoke lokal, bukan sertifikasi seluruh fitur.
- **Baseline pengujian:** 74 tes otomatis lulus pada baseline sebelum perubahan publikasi ini; jumlah itu bukan bukti pengujian seluruh operasi Windows nyata. Hasil perubahan terbaru perlu dicatat oleh kontributor.
- **Belum diverifikasi:** Windows 10 secara langsung, VM bersih, ARM/32-bit, variasi DPI/multimonitor, serta kompatibilitas semua aplikasi yang dipindahkan.
- Tidak ada klaim peningkatan performa, penghematan RAM universal, build reproduktif, executable bertanda tangan, atau pipeline CI yang terverifikasi.

## Mulai dari sumber

Jalankan perintah berikut di **PowerShell**, dari direktori proyek. Cara ini tidak membutuhkan aktivasi virtual environment atau perubahan execution policy.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install ttkbootstrap psutil send2trash
.\.venv\Scripts\python.exe dev_cleaner.py
```

Paket diunduh dari indeks pip yang dikonfigurasi. Versi belum dikunci; baca [instalasi dan build](docs/INSTALLATION.md) untuk batas reproduktibilitas dan dependensi build tambahan. Jalankan awalnya tanpa hak Administrator. Beberapa tindakan, khususnya App Mover dan perubahan sistem, membutuhkan elevasi.

Untuk peluncuran tanpa terminal setelah dependensi tersedia:

```powershell
.\.venv\Scripts\pythonw.exe Run-Dev-Cleaner.pyw
```

Launcher `.bat` lama memasang sebagian dependensi melalui pip dan belum mencakup runtime ttkbootstrap/psutil secara lengkap. Gunakan langkah virtual environment di atas sebagai rute utama.

## Build lokal (opsional)

PyInstaller adalah **dependensi build**, bukan syarat menjalankan sumber. Spec saat ini juga mengoleksi CustomTkinter/darkdetect dan modul pywin32 walaupun widget utama memakai adapter ttkbootstrap.

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller customtkinter darkdetect pywin32
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm Dev-AI-Cleaner.spec
```

Keluaran yang dikonfigurasi: `dist/Dev-AI-Cleaner.exe`, mode GUI (`console=False`). Build harus dijalankan dan diuji di Windows; perintah ini bukan klaim bahwa tersedia rilis biner resmi. Audit lisensi dependensi dan hasil bundel sebelum mendistribusikan executable.

## Keselamatan, data, dan jaringan

Riwayat pemindahan, preferensi, backup registry, dan log diagnostik Python berada di `%LOCALAPPDATA%\DevAICleaner`. Unduhan installer, bila fitur diberi katalog lokal tepercaya, menggunakan `%USERPROFILE%\Downloads\Cleaner_App_Installers`. Jangan menghapus riwayat App Mover saat masih ada folder yang dipindahkan atau pemulihan tertunda.

Pemindaian inti bekerja lokal. Pemeriksaan tautan menghubungi URL yang dimasukkan; tautan runtime membuka browser; pengunduhan/installer dan utilitas Windows dapat menggunakan jaringan serta mempunyai kebijakan sendiri. Tidak ada layanan akun/telemetri aplikasi yang dinyatakan dalam sumber yang ditinjau; ini bukan jaminan bahwa OS, pip, atau alat pihak ketiga tidak berkomunikasi keluar.

Baca [keselamatan dan privasi](docs/SAFETY_AND_PRIVACY.md) sebelum tindakan destruktif. Hasil tindakan yang gagal/tidak terverifikasi dipertahankan pada alur inti; gunakan refresh/pemindaian manual untuk melihat perubahan eksternal. Pengaman mutasi tidak menggantikan backup dan tidak menjamin serialisasi semua alat eksternal pada toolbox.

## Dokumentasi dan kontribusi

- [Panduan pengguna: enam menu dan subview](docs/USER_GUIDE.md)
- [Instalasi, pengujian, dan build](docs/INSTALLATION.md)
- [Keselamatan dan privasi](docs/SAFETY_AND_PRIVACY.md)
- [Pemecahan masalah](docs/TROUBLESHOOTING.md)
- [PRD](docs/PRD.md) · [Tech Stack](docs/TECH_STACK.md)
- [Kontribusi](CONTRIBUTING.md) · [Pelaporan keamanan](SECURITY.md) · [Changelog](CHANGELOG.md)
- [Pemberitahuan pihak ketiga](docs/THIRD_PARTY_NOTICES.md)

## Lisensi

Kontribusi asli proyek dilisensikan dengan [MIT](LICENSE), tanpa jaminan. Dependensi, aset, merek, dan kode pihak ketiga tetap tunduk pada hak/lisensinya sendiri. MIT proyek tidak membuktikan hak atas kode eksternal; pemeriksaan asal-usul dan inventaris bundel tetap merupakan gerbang sebelum publikasi biner.
