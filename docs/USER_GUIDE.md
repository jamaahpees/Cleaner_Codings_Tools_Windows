# Panduan pengguna

Panduan ini memakai nama menu publik. Baca [keselamatan dan privasi](SAFETY_AND_PRIVACY.md) dahulu. Persiapkan backup, tutup aplikasi terkait, dan mulai dari folder uji kecil. Jangan menggunakan komputer produksi sebagai percobaan pertama.

## Pola kerja bersama

1. Pilih menu, lokasi, kategori, atau interpreter yang benar.
2. Jalankan pemindaian/refresh secara sadar; pemindaian bukan persetujuan penghapusan.
3. Periksa nama, path, ukuran perkiraan, dan status setiap kandidat.
4. Pilih hanya item yang Anda pahami. Baca dialog konfirmasi bila tersedia.
5. Tunggu selesai, baca log di bagian bawah, lalu verifikasi hasil di sistem/aplikasi terkait.

Alur inti menahan tindakan mutasi ketika scan/mutasi lain aktif. Item yang berhasil diverifikasi diperbarui di tempat, bukan diikuti pemindaian penuh otomatis. Kegagalan tetap perlu ditinjau; jangan menganggap hilangnya pesan error sebagai bukti sukses. Toolbox menjalankan alat lain dengan perilaku tersendiri, dan tidak semua tombol mempunyai konfirmasi atau undo.

## 1. Smart Cleaner

**Tujuan:** menemukan kandidat pembersihan, bukan menentukan semua data aman dihapus.

### Kategori

- **Browser & Windows:** cache Chrome/Edge, user/system temp, thumbnail cache, crash dumps/error logs, dan Recycle Bin. Pengosongan Recycle Bin tidak dipilih pada default.
- **Dev & AI Coding Caches:** pip/uv, npm/pnpm/bun, log alat developer, model Hugging Face/Torch, serta biner Playwright/Puppeteer. Model dan biner dapat memerlukan unduhan besar ketika digunakan lagi.
- **Proyek & Dependencies:** `.venv`/`venv`/`env`, `node_modules`, dan `__pycache__` dalam lokasi proyek yang dipilih. Virtual environment dapat menyimpan paket yang sulit dipasang ulang; simpan manifest dependensi terlebih dahulu.
- **Registry:** kandidat sisa uninstall dan App Paths dengan target hilang. “Yatim” adalah hasil heuristik, bukan kepastian bahwa entri tidak lagi berguna.

### Langkah

1. Tinjau checklist; preset semua/default/batal mengubah cakupan, bukan langsung membersihkan.
2. Periksa folder proyek yang ditampilkan dan ubah bila salah. Jangan mengandalkan lokasi default.
3. Jalankan **SMART SCAN (ANALISIS)**, lalu tinjau hasil.
4. Pilih kandidat tertentu dan jalankan pembersihan setelah memahami konsekuensinya.
5. Periksa log. Backup `.reg` harus berhasil sebelum registry terpilih dibersihkan; backup gagal berarti entri dipertahankan.

**Smart Scan saat startup:** default OFF, tersimpan di `preferences.json`. Bila diaktifkan, analisis dijalankan satu kali saat aplikasi dibuka dengan kategori yang aktif saat itu. Ini tidak menambahkan scheduled task, layanan resident, atau pembersihan otomatis. Pengaturan ini tidak berarti semua pilihan kategori/folder disimpan antar sesi.

Pembersihan cache/temp tertentu bersifat permanen; hanya alur tertentu menggunakan Recycle Bin. Lihat [peta risiko](SAFETY_AND_PRIVACY.md).

## 2. App Mover & Restore

**Tujuan:** memindahkan folder aplikasi yang memenuhi filter dari drive C: ke lokasi tujuan, lalu mempertahankan akses melalui junction NTFS. Ini bukan migrasi instalasi lintas PC atau pengganti installer resmi.

### Daftar aplikasi/pemindahan

1. Jalankan dengan Administrator ketika hendak move/restore.
2. Pindai kandidat, lalu baca status kelayakan dan path. Filter dapat menolak runtime, keamanan, driver, komponen sistem, atau folder berisiko; jangan mengakali filter.
3. Tutup aplikasi terkait dan simpan pekerjaan. Proses dari folder aplikasi dapat dihentikan oleh alur pemindahan.
4. Pilih drive tujuan yang memiliki ruang cukup; pilihan default memakai folder `DevApps` pada drive non-C:. Gunakan volume lokal yang stabil dan mendukung kebutuhan junction/izin, bukan removable/network drive tanpa pengujian.
5. Konfirmasikan pilihan. Jangan mematikan aplikasi/PC atau melepas drive saat proses berlangsung.
6. Verifikasi aplikasi masih berjalan normal sebelum mengandalkan hasilnya.

Robocopy, manifest/verifikasi isi, staging, dan junction membantu mengurangi risiko, tetapi tidak menjamin semua metadata, updater, service, lisensi aplikasi, atau antivirus kompatibel dengan pemindahan. Installer/update aplikasi di kemudian hari dapat mengubah hasil.

### Riwayat/restore

- Riwayat berada di `%LOCALAPPDATA%\DevAICleaner\moves.json`; **simpan berkas ini bersama backup Anda**. Aplikasi memakai riwayat lokalnya sendiri dan tidak membutuhkan instalasi aplikasi lain.
- Pilih catatan yang benar dan gunakan restore. Pastikan drive tujuan tetap tersedia dan ruang di drive asal cukup.
- Status `restored_pending_cleanup` berarti pemulihan asal telah dicatat tetapi pembersihan salinan tujuan belum selesai. Gunakan retry pembersihan yang disediakan; jangan mengulang copy atau menghapus direktori secara spekulatif.
- Jika path berubah, verifikasi gagal, atau rollback bermasalah, hentikan tindakan lanjutan. Simpan kedua salinan/staging serta `moves.json`, lalu lakukan pemeriksaan manual. Jangan mengedit riwayat agar status terlihat berhasil.

## 3. Duplicate File Finder (Safe)

1. Pilih folder spesifik berisi data uji atau data yang sudah dicadangkan; jangan mulai dari seluruh drive.
2. Jalankan scan. Kandidat dibandingkan berdasarkan isi/hash sesuai alur pemindai, bukan sekadar nama yang sama.
3. Periksa grup, lokasi, dan salinan yang akan disimpan; gunakan buka lokasi untuk memeriksa file.
4. Pilih duplikat dengan hati-hati dan kirim ke **Recycle Bin** setelah konfirmasi. Pembatasan mencegah pilihan tertentu, tetapi Anda tetap harus menjaga salinan yang dibutuhkan.
5. Verifikasi sebelum mengosongkan Recycle Bin. Pemulihan menggunakan Recycle Bin Windows selama item masih tersedia.

Ada pembatasan ekstensi kode/data dan direktori sistem; hasil tidak mewakili seluruh file dalam komputer. File dapat berubah setelah scan. Tidak ditemukannya file bukan selalu bukti bahwa aplikasi berhasil menghapusnya.

**Pengaturan Recycle Bin/Storage Sense:** kontrol terkait retensi 30 hari mengubah konfigurasi Windows, bukan hanya tampilan aplikasi. Jangan mengaktifkannya bila Anda mengandalkan Recycle Bin sebagai jalur pemulihan jangka panjang.

## 4. Python Library Manager

1. Pilih interpreter/environment dari daftar yang ditemukan. Penemuan registry/lokasi umum tidak menjamin semua virtual environment terdeteksi.
2. Periksa path interpreter dan pindai paket pada environment itu.
3. Tinjau versi, ukuran perkiraan, dan dependensi. Paket yang tampak tidak digunakan masih dapat diperlukan proyek lain.
4. Pilih paket non-protected dan konfirmasikan uninstall.
5. Uninstall dijalankan melalui interpreter hasil scan dan diverifikasi memakai `importlib.metadata` pada interpreter yang sama. Paket yang gagal/tidak terverifikasi tetap ditampilkan.

Paket inti tertentu dilindungi dari pilihan uninstall. Perlindungan bukan dependency solver: uninstall dapat merusak proyek. Simpan `pip freeze` dari interpreter terkait bila perlu; jangan mencopot paket Python global hanya untuk mengurangi angka ukuran. Pemasangan ulang melalui pip dapat membutuhkan jaringan.

## 5. Startup & Windows Services

### Subview Startup

Pindai entri startup registry, periksa nama/perintah dan statusnya, lalu gunakan aksi enable/disable yang tersedia. Perubahan startup memengaruhi peluncuran pada sesi masuk berikutnya; tidak selalu menghentikan proses yang sedang berjalan. Daftar ini bukan inventaris semua mekanisme autostart Windows (misalnya seluruh scheduled task).

### Subview Windows Services

Segarkan daftar layanan, baca nama/status, lalu gunakan start/stop yang tersedia. Sebagian layanan membutuhkan Administrator. Perubahan dapat memengaruhi jaringan, updater, keamanan, atau aplikasi lain. Transisi layanan dapat memerlukan waktu; bila status belum terverifikasi, periksa kembali dengan refresh manual atau Services Windows. Jangan menonaktifkan layanan hanya karena tidak dikenali.

## 6. System Toolbox (Tweaks & Tools)

Toolbox bukan paket “optimasi sekali klik”. Pilih satu tindakan, pahami dampaknya, lalu periksa log/exit code. Beberapa perubahan tidak mempunyai tombol undo di aplikasi.

| Subview | Cara pakai dan batas |
|---|---|
| **App Setup (Cleaner Native)** | Area pencarian/filter, status aplikasi, dan aksi installer/portable berbasis katalog lokal. **Tidak ada katalog publik yang dibundel** sehingga daftar kosong adalah keadaan normal. Tidak ada rekomendasi mengunduh katalog privat. Metadata katalog dan perintah installer harus dianggap input tepercaya berisiko tinggi, bukan data pasif. |
| **Windows Tweaks** | Opsi power plan, GameDVR, layanan diagnostik Windows, pencarian web Start, serta flush DNS. Power plan menjalankan duplikasi skema; periksa sendiri skema aktif di Windows, jangan menganggap otomatis aktif. Mengubah layanan diagnostik Windows bukan bukti seluruh telemetri Windows mati. Hasil tergantung edisi/kebijakan Windows. |
| **System Health & WinSxS** | DISM component cleanup, SFC, restart layanan Windows Update, reset cache Store, dan status aktivasi. Component cleanup menjalankan `/StartComponentCleanup`, **bukan `/ResetBase`**. Update repair pada alur ini berupa stop/start `wuauserv`, bukan perbaikan menyeluruh semua masalah update. Status aktivasi hanya pemeriksaan, bukan aktivator. |
| **Essential Runtimes** | Tombol checker yang ada saat ini memeriksa keluaran `dotnet --list-runtimes`; jangan menafsirkannya sebagai audit lengkap Visual C++/DirectX/Java. Tombol unduhan membuka halaman Microsoft atau Adoptium untuk memilih runtime secara manual. |
| **App Link Checker** | Masukkan URL yang tidak sensitif lalu pilih **Cek Link**. Permintaan HTTP `HEAD` dapat mengikuti redirect dan menampilkan status/final URL. Status 200 bukan bukti aman; sebagian server menolak HEAD walau halaman bisa dibuka. |

Saat fitur installer lokal digunakan, berkas berada di `%USERPROFILE%\Downloads\Cleaner_App_Installers`. Installer dapat menampilkan UI atau menjalankan proses lain; pembatalan tidak menjamin rollback perubahan yang sudah terjadi. Periksa sumber resmi, signature/hash independen, izin lisensi, dan perilaku installer sebelum menjalankannya.

## Membaca log

Panel **Log Aktivitas & Eksekusi Real-time** memperlihatkan progres dan pesan error. **Bersihkan Log** mengosongkan panel tampilan; tidak berarti menghapus `py_libs_debug.log`, backup registry, riwayat, log Windows, atau mengembalikan tindakan. Hindari membagikan log mentah; samarkan path akun, nama paket privat, URL bertoken, dan perintah sensitif.

Jika ada masalah, gunakan [panduan troubleshooting](TROUBLESHOOTING.md); masalah keamanan mengikuti [SECURITY.md](../SECURITY.md).
