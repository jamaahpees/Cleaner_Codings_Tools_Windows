# Pemecahan masalah

Mulai dengan mencatat versi Windows/Python, arsitektur, langkah reproduksi, menu, dan pesan error. Jangan mengulang tindakan destruktif untuk mendapatkan screenshot. Samarkan path dan informasi pribadi sebelum melaporkan.

| Gejala | Pemeriksaan aman |
|---|---|
| `py`/`python` tidak ditemukan | Gunakan path Python x64 yang terpasang; periksa instalasi resmi dan Windows App Execution Aliases. Jangan menjalankan skrip installer acak. |
| `No module named ttkbootstrap/psutil/send2trash` | Instal runtime melalui interpreter `.venv` yang sama dengan yang menjalankan aplikasi; lihat [instalasi](INSTALLATION.md). Launcher `.bat` lama tidak melengkapi seluruh runtime. |
| `tkinter` tidak tersedia | Perbaiki instalasi Python dengan komponen Tcl/Tk; `pip install tkinter` bukan solusi standar. |
| GUI `.pyw` tidak muncul/menutup | Jalankan `.venv\Scripts\python.exe dev_cleaner.py` dari terminal untuk melihat traceback. `.pyw` tidak memasang dependensi. Jangan membagikan traceback yang memuat path privat tanpa redaksi. |
| Build mengeluh `win32api`/CustomTkinter/darkdetect | Pasang dependensi tambahan spec menggunakan interpreter build yang sama. Periksa versi Python/PyInstaller, bukan menyalin DLL acak dari internet. |
| Antivirus/SmartScreen memperingatkan executable | Jangan menonaktifkan proteksi. Gunakan sumber yang ditinjau atau periksa biner secara independen; tidak ada janji executable ditandatangani. |
| Kontrol terpotong pada DPI tinggi | Perbesar jendela, gunakan scrolling bila ada, catat resolusi/scaling/multimonitor. Variasi DPI belum diverifikasi; jangan menganggap semua layout pasti sesuai. |
| Scan tidak berjalan saat startup | Default memang OFF. Periksa checkbox dan akses tulis `preferences.json`. Scan hanya satu kali per peluncuran; tidak ada layanan background yang perlu dipasang. |
| Scan/mutasi ditolak karena sibuk | Tunggu operasi aktif selesai dan baca log. Jangan memulai instance kedua untuk melewati pengaman. Jika benar-benar macet, simpan bukti/status tanpa menghapus staging/riwayat. |
| Temuan tetap ada setelah pembersihan | Item gagal atau tidak terverifikasi sengaja dipertahankan. Tutup aplikasi yang mengunci file, periksa izin/path, lalu tinjau ulang. Jangan menganggap semua temuan pasti aman dihapus. |
| Daftar tidak mencerminkan perubahan eksternal | Tidak ada full rescan otomatis setelah tindakan inti. Jalankan refresh/scan manual saat tidak ada operasi aktif. |
| Registry tidak dibersihkan | Periksa kegagalan ekspor backup, izin, dan key. Jangan melewati backup untuk memaksa penghapusan. |
| Drive tujuan App Mover kosong | Daftar mengecualikan C:, drive tertentu, dan volume dengan ruang bebas kurang dari ambang sekitar 2 GB. Itu ambang tampilan, bukan jaminan ruang cukup untuk item Anda. |
| Aplikasi tidak memenuhi filter move | Gunakan installer resmi/mekanisme vendor; jangan ubah filter atau riwayat agar komponen sistem diterima. |
| Move/restore gagal atau terputus | Pertahankan asal/tujuan/staging dan `moves.json`. Pastikan drive terhubung dan baca log sebelum tindakan lanjutan. Jangan hapus junction atau salah satu salinan tanpa memahami recovery. |
| `restored_pending_cleanup` | Gunakan retry pembersihan yang tersedia. Jika verifikasi isi mendeteksi perubahan, simpan kedua salinan untuk pemeriksaan manual; jangan menandai sukses dengan mengedit JSON. |
| Riwayat JSON rusak | Backup berkas apa adanya, hentikan move/restore, dan lakukan pemeriksaan manual. Jangan menghapusnya untuk “reset” ketika junction masih aktif. |
| Paket Python tidak terlihat atau uninstall salah target | Periksa path interpreter yang dipilih dan lakukan scan ulang manual sebelum uninstall. Penemuan environment bukan daftar semua Python/venv. |
| pip gagal atau paket masih tercatat | Periksa `py_libs_debug.log` dan keluaran pip dari interpreter yang sama. Izin/dependensi/file terkunci dapat menghambat; baris tidak dihapus bila hasil belum terverifikasi. |
| Startup/layanan tidak berubah | Periksa elevasi, kebijakan organisasi dan status aktual di Windows. Layanan dapat berada dalam status transisi. Gunakan refresh manual; jangan menghentikan layanan yang tidak dipahami. |
| Folder duplikat menghasilkan sedikit/tanpa hasil | Periksa scope, ekstensi/direktori yang dibatasi, izin, serta perubahan file. Pemindai bukan inventaris semua data. |
| File tidak ada dalam Recycle Bin | Hentikan pembersihan lain dan periksa Storage Sense/retensi serta volume terkait. Pemulihan tidak dijamin; jangan melakukan secure erase/overwrite. |
| App Setup kosong | Normal: tidak ada `app_catalog.json` publik yang dibundel. Jangan mengambil katalog privat atau paket tidak berizin. |
| Link Checker mendapat 403/405/timeout | Server mungkin memblokir HEAD, meminta autentikasi, atau sedang tidak terjangkau. Jangan menonaktifkan validasi TLS; respons sukses pun bukan bukti aman. |
| “Essential Runtime Checker” tidak mencakup runtime tertentu | Checker tombol saat ini memeriksa .NET melalui `dotnet --list-runtimes`, bukan audit lengkap semua runtime. Gunakan sumber/vendor resmi untuk kebutuhan lain. |
| DISM/SFC/Windows tool gagal | Baca exit code dan log alat Windows, periksa izin/kebijakan. Jangan menjalankan perintah tambahan yang tidak dimengerti. Perintah dapat memerlukan waktu lama. |

## Meminta bantuan

Untuk bug biasa, gunakan issue bug report dengan hasil yang diharapkan/aktual dan data uji minimum. Jangan unggah installer, katalog privat, riwayat move, backup `.reg`, atau seluruh log mentah. Masalah yang dapat menghapus data di luar pilihan, mengekspos informasi sensitif, atau mengeksekusi input tidak tepercaya mengikuti [SECURITY.md](../SECURITY.md), bukan issue publik dengan exploit rinci.
