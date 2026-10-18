# PRD — Dev & AI Cleaner

**Snapshot:** 18 Oktober 2026 · **Status:** baseline implementasi dan batas verifikasi, bukan sertifikasi rilis.

## Produk dan pengguna

Utilitas desktop Windows lokal untuk pengguna tingkat lanjut/developer yang perlu meninjau cache, folder aplikasi, duplikat, environment Python, startup/layanan, dan alat pemeliharaan Windows dalam satu antarmuka. Produk mengutamakan peninjauan kandidat dan hasil tindakan, bukan pembersihan sistem tanpa pengawasan.

## Tujuan

1. Menyediakan enam menu publik dengan scope/target dan konsekuensi yang jelas.
2. Memisahkan scan dari mutasi; membutuhkan pilihan/konfirmasi pada alur destruktif inti.
3. Mempertahankan item gagal/tidak terverifikasi, dengan pembaruan lokal setelah sukses tanpa full rescan otomatis.
4. Menyediakan jalur pemulihan terbatas melalui Recycle Bin, backup registry, serta riwayat App Mover yang tahan kegagalan.
5. Menyediakan dokumentasi publik berbahasa Indonesia yang jujur tentang dukungan, jaringan, dependensi dan risiko.

## Bukan tujuan

- Menggantikan backup, antivirus, manajemen perangkat organisasi, installer vendor, atau alat recovery profesional.
- Menjanjikan semua cache/registry yatim aman dihapus atau semua aplikasi dapat dipindahkan.
- Menjamin peningkatan performa, angka penggunaan RAM universal, atau kompatibilitas seluruh Windows/arsitektur.
- Membundel katalog software publik, installer komersial, mekanisme bypass aktivasi, atau mengimpor katalog privat.
- Menganggap keberadaan lisensi MIT proyek menyelesaikan lisensi/provenance kode eksternal.

## Cakupan fungsi saat ini

| Menu | Persyaratan perilaku dan batas |
|---|---|
| Smart Cleaner | Kategori browser/Windows, developer/cache/model, dependensi proyek, registry yatim; analisis lalu pilihan pembersihan. Startup Smart Scan opsional default OFF, tersimpan lokal, satu kali per launch, tanpa auto-clean atau layanan resident. Registry memerlukan ekspor backup berhasil. |
| App Mover & Restore | Kandidat folder aplikasi dari registry, filter risiko, tujuan non-C:, Robocopy/staging/verifikasi dan junction NTFS. Riwayat atomik lokal; fase `restored_pending_cleanup` dan retry tanpa menyalin ulang. Tidak memerlukan riwayat/instalasi aplikasi eksternal. |
| Duplicate File Finder (Safe) | Scan folder terpilih, pembandingan kandidat berdasarkan isi, pembatasan scope/pilihan dan pemindahan terpilih ke Recycle Bin. Filter bukan jaminan semua data aman. |
| Python Library Manager | Penemuan interpreter umum/registry, daftar paket dan metadata/dependensi, paket inti protected; uninstall serta verifikasi metadata melalui interpreter yang sama. Penemuan environment tidak menyeluruh. |
| Startup & Windows Services | Dua subview untuk entri startup registry dan layanan, aksi yang tersedia serta status terverifikasi; refresh manual untuk perubahan eksternal/transisi. Bukan inventaris semua autostart. |
| System Toolbox (Tweaks & Tools) | Lima subview: App Setup, Windows Tweaks, System Health & WinSxS, Essential Runtimes, App Link Checker. App Setup kosong tanpa katalog; alat lain memanggil utilitas OS/halaman resmi. Tidak semua aksi memiliki undo/konfirmasi atau berada dalam pengaman mutasi inti. |

Nama/kunci internal lama tidak merupakan nama pemasaran atau kontrak kompatibilitas publik. Detail tindakan aktual dijelaskan dalam [panduan pengguna](USER_GUIDE.md), termasuk batas checker .NET, DISM tanpa ResetBase, dan restart layanan update yang bukan diagnosis lengkap.

## Persyaratan nonfungsional

- **Platform:** Windows 10/11 x64 adalah target. Verifikasi GUI lokal yang dilaporkan hanya Windows 11 build 26300, Python 3.11.9 AMD64; Windows 10, VM bersih, ARM/32-bit, dan berbagai DPI belum terverifikasi.
- **Antarmuka:** desktop Tkinter/ttkbootstrap melalui adapter CTk; tidak memerlukan runtime browser.
- **Responsivitas:** worker thread/executor untuk pekerjaan panjang, pembaruan GUI melalui Tk `after`. Tidak ada klaim benchmark atau footprint RAM universal.
- **Koordinasi:** pengaman scan/mutasi inti; jangan menyatakan semua alat eksternal diserialisasi.
- **Privasi:** state/log lokal, tanpa backend akun/telemetri aplikasi yang dinyatakan pada sumber yang ditinjau. Jaringan tetap digunakan oleh pip, link checker, browser, installer, dan utilitas OS tertentu.
- **Packaging:** spec PyInstaller GUI tersedia; dependensi belum dikunci, tidak ada klaim rilis bertanda tangan/CI atau build reproduktif.

## Kriteria penerimaan baseline

- Enam menu dan lima subview toolbox dapat dikenali serta didokumentasikan dengan label publik.
- Smart Scan startup default OFF, satu dispatch saat diaktifkan, tidak melakukan penghapusan otomatis.
- Hasil mutasi inti hanya diperbarui ketika terverifikasi; item gagal tetap terlihat; tidak ada full scan otomatis setelah tindakan.
- App Mover mempertahankan state recovery dan tidak menghapus salinan yang berubah tanpa verifikasi.
- Uninstall paket memakai interpreter hasil scan, bukan interpreter lain yang kebetulan aktif.
- Konsol subprocess internal disembunyikan pada jalur yang mendukungnya, tanpa menyembunyikan error/exit code; aplikasi/installer interaktif dapat tetap menampilkan UI.
- Dokumentasi membedakan runtime/build deps, state/log, jaringan, hasil pengujian dan gap verifikasi.

**Bukti yang dilaporkan:** baseline 74 unit test lulus; smoke GUI lokal Windows 11. Bukti ini tidak menggantikan pengujian operasi destruktif pada VM bersih, inventaris lisensi bundel atau pemeriksaan provenance/histori.

## Risiko utama

| Risiko | Mitigasi dan batas |
|---|---|
| Salah pilihan/heuristik cache dan registry | Preview path/kategori, backup, konfirmasi; tetap mungkin kehilangan data. |
| Copy/junction/restore terputus | Manifest, staging, riwayat atomik, state recovery dan retry; simpan semua salinan bila gagal. |
| Salah interpreter/paket | Tampilkan path, pertahankan interpreter scan, verifikasi metadata; tidak menyelesaikan dependency graph. |
| Pengaturan/layanan merusak sistem | Privilege minimum, satu tindakan per waktu, catat konfigurasi; tidak semua tweak punya undo. |
| Input katalog/installer berbahaya | Tidak bundel katalog publik; jangan memperlakukan metadata executable sebagai input tidak tepercaya yang aman. |
| Klaim publik melebihi bukti | Pisahkan target dari yang diuji, gunakan screenshot UI asli dengan data demonstrasi, tahan publikasi biner sampai audit. |

## Pekerjaan lanjutan (belum dianggap selesai)

- Validasi VM Windows 10/11 x64 bersih, GUI/executable dan recovery kegagalan pada data uji.
- Audit DPI/multimonitor, aksesibilitas, serta lifecycle/thread-safety GUI.
- Kunci dependensi dan inventaris komponen bundel; pertahankan seluruh lisensi/notice.
- Tinjau provenance dan histori sebelum perubahan visibilitas repositori; penghapusan fitur dari working tree tidak menghapusnya dari histori.
- Ukur performa dengan skenario dan baseline yang dapat direproduksi sebelum membuat klaim.

Gerbang publikasi dikelola di [checklist publikasi](PUBLICATION_CHECKLIST.md), bukan disimpulkan otomatis dari dokumen ini.
