# Keselamatan dan privasi

Dev & AI Cleaner adalah utilitas pemeliharaan dengan kemampuan mengubah sistem, bukan backup, antivirus, secure eraser, atau jaminan optimasi. Cadangkan data dan gunakan data/mesin uji untuk mencoba tindakan pertama kali. Jangan menjalankan semua tombol sebagai rangkaian “optimasi”.

## Peta risiko dan pemulihan

| Tindakan | Dampak dan batas pemulihan |
|---|---|
| Cache/temp/model/biner developer | Penghapusan tertentu permanen; cache/model dapat perlu unduhan ulang. Tidak semua data bisa direkonstruksi. |
| Dependensi proyek | Dapat menghapus environment atau dependensi lokal; beberapa alur memakai Recycle Bin, tetapi jangan mengandalkannya sebagai backup. Simpan manifest dan kode yang tidak tergenerasi. |
| Registry yatim | Heuristik dapat salah. Ekspor `.reg` diverifikasi sebelum penghapusan terpilih; backup bukan snapshot sistem lengkap. Impor ulang hanya setelah meninjau key dan dampaknya. |
| Recycle Bin | Mengosongkan bin atau mengaktifkan retensi Storage Sense menghilangkan jalur pemulihan biasa. Ruang bebas fisik bisa berbeda dari ukuran yang ditampilkan. |
| App Mover/restore | Copy, staging, penghentian proses dan junction dapat mengganggu aplikasi. Simpan `moves.json`, kedua lokasi, dan staging saat terjadi kegagalan. Tidak ada jaminan kompatibilitas updater/service/DRM. |
| Duplikat | Pemindahan terpilih ke Recycle Bin mempunyai filter, tetapi file yang identik bisa tetap dibutuhkan di dua lokasi. Verifikasi salinan sebelum mengosongkan bin. |
| Uninstall paket Python | Dapat memutus dependensi proyek; daftar protected bukan dependency resolver. Jalur pemulihan umumnya memasang ulang versi yang benar pada interpreter yang benar. |
| Startup/layanan/tweaks | Dapat memutus jaringan, login, updater, atau layanan aplikasi. Tidak semua tindakan mempunyai backup/undo otomatis. Catat konfigurasi awal. |
| DISM/SFC/Store/Update tools | Memanggil utilitas Windows dengan hak dan konsekuensinya sendiri. Exit code/log perlu dibaca; bukan bukti semua kerusakan telah pulih. |
| Installer/portable lokal | Menjalankan kode pihak ketiga, mungkin dengan hak tinggi. Cancel tidak menjamin rollback. Katalog publik tidak disertakan dan pengunduhan bukan verifikasi keamanan. |

Pengaman mutasi mengoordinasikan alur inti scan/mutasi; tidak menjamin semua aksi toolbox atau program eksternal saling terkunci. Hindari menjalankan pemeliharaan lain secara bersamaan. Jangan menutup paksa proses saat copy/restore berlangsung.

## Izin

Gunakan akun biasa untuk peluncuran/inspeksi jika memungkinkan. App Mover, registry mesin, layanan tertentu, DISM/SFC, dan pengaturan sistem mungkin memerlukan Administrator. Jangan mematikan antivirus/SmartScreen atau menurunkan kebijakan keamanan agar operasi berjalan. Pada perangkat organisasi, kebijakan admin dapat mengalahkan perubahan dan harus dihormati.

## Lokasi data lokal

| Lokasi | Isi dan perlakuan |
|---|---|
| `%LOCALAPPDATA%\DevAICleaner\preferences.json` | Preferensi boolean `startup_smart_scan`, default OFF bila tidak valid/tidak tersedia. Bukan penyimpanan semua pilihan UI. |
| `%LOCALAPPDATA%\DevAICleaner\moves.json` | Path asal/tujuan, status dan metadata pemindahan/pemulihan. Simpan selama masih ada move atau cleanup tertunda; **jangan hapus untuk mengatasi error**. |
| `%LOCALAPPDATA%\DevAICleaner\RegistryBackups\*.reg` | Ekspor registry sebelum penghapusan terkait. Dapat memuat nama/path dan konfigurasi sensitif; simpan terlindung. |
| `%LOCALAPPDATA%\DevAICleaner\py_libs_debug.log` | Diagnostik paket/interpreter dan hasil/error. Bisa memuat path akun, environment, nama paket privat. Tidak ada klaim rotasi/retensi otomatis. |
| `%USERPROFILE%\Downloads\Cleaner_App_Installers` | Folder unduhan installer lokal bila digunakan; dapat dibuat walau katalog kosong. Bukan karantina atau verifikasi antivirus. |
| Lokasi aplikasi/drive tujuan dan staging | Salinan operasi App Mover, sering di folder `DevApps` pada drive tujuan. Simpan bila pemulihan belum selesai. |
| `build/`, `dist/`, `__pycache__/`, log tes lokal | Hasil pengembangan/build, bukan data yang perlu diunggah ke repositori. |

State utama mengikuti `%LOCALAPPDATA%`; bila variabel lingkungan itu tidak tersedia, kode mempunyai fallback `C:\DevAICleaner`. Jangan mengandalkan fallback ini sebagai konfigurasi normal. Aplikasi memakai riwayat lokalnya sendiri; tidak mengimpor riwayat eksternal secara otomatis.

Panel log GUI adalah tampilan sesi, berbeda dari log diagnostik di disk. Tombol **Bersihkan Log** tidak menghapus seluruh jejak disk atau log utilitas Windows. Tidak ada kontrol “hapus semua data pribadi” terpusat atau enkripsi state aplikasi yang dinyatakan dalam implementasi yang ditinjau.

## Jaringan dan pihak ketiga

- Scan file, registry, startup/layanan, dan inventaris paket inti bekerja terhadap mesin lokal; tidak ada backend akun atau endpoint telemetri aplikasi yang dinyatakan dalam sumber yang ditinjau.
- Instalasi pip memakai indeks/proxy yang dikonfigurasi. Mengikuti panduan setup memerlukan unduhan dependency.
- **App Link Checker** mengirim `HEAD` ke URL pengguna, dapat mengikuti redirect, dan mengirim User-Agent. Server dapat melihat IP, waktu, dan path/query; jangan masukkan token, URL privat, signed URL, atau endpoint intranet sensitif.
- Tombol runtime membuka situs Microsoft/Adoptium lewat browser. Browser, situs tujuan, installer, Windows Update, dan utilitas OS mempunyai komunikasi/kebijakan sendiri.
- Bila katalog lokal ditambahkan secara sadar, installer dapat diunduh dan dijalankan menurut metadatanya. Aplikasi bukan pemeriksa malware, signature, checksum universal, atau penjamin hak redistribusi. Jangan memasukkan katalog/skrip dari sumber tidak tepercaya.
- Status HTTP sukses hanya menandakan respons server, bukan integritas atau keamanan biner. HTTPS sendiri juga bukan jaminan bahwa penerbit file tepercaya.

Tidak ada klaim “100% offline” atau “tidak pernah ada jaringan” untuk seluruh aplikasi. Pengaturan yang menargetkan diagnostik Windows berbeda dari telemetri aplikasi dan tidak menjamin seluruh pengumpulan Windows berhenti.

## Membagikan laporan dengan aman

Samarkan nama akun, path pribadi, nama host/drive, URL/query, lisensi/serial, dan paket privat sebelum membagikan screenshot/log. Kirim hanya potongan minimum yang diperlukan, bukan `moves.json`, `.reg`, dump registry, atau seluruh folder profil. Gunakan fixture/data demonstrasi untuk reproduksi.

Laporan kerentanan mengikuti [kebijakan keamanan](../SECURITY.md). Kesiapan publikasi mengikuti [checklist publikasi](PUBLICATION_CHECKLIST.md); keberadaan dokumentasi bukan sertifikasi keamanan/provenance.
