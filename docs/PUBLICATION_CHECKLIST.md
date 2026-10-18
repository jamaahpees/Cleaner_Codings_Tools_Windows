# Checklist publikasi

Checklist ini untuk pemilik repository sebelum mengubah visibility GitHub. Dokumentasi, screenshot, dan lisensi tidak dengan sendirinya membuktikan seluruh kode/aset layak didistribusikan.

## Sebelum menjadikan repo publik

- [ ] Tinjau diff akhir dan pastikan source terbaru serta dokumentasi yang sesuai sudah berada pada branch yang akan dipublikasikan.
- [ ] Pastikan hak atas kode dan aset yang dilisensikan MIT; pertahankan atribusi serta lisensi pihak ketiga yang berlaku.
- [ ] Tinjau [catatan pihak ketiga](THIRD_PARTY_NOTICES.md), termasuk ketidaksesuaian metadata dan teks lisensi dependensi. Jangan memasukkan installer/katalog yang asal dan izin redistribusinya belum jelas.
- [ ] Tinjau **seluruh riwayat Git**, bukan hanya working tree. Menghapus kode atau menambahkan `.gitignore` tidak menghapus versi historisnya. Riwayat awal memuat alur auto-patch yang dihapus dari source saat persiapan publikasi; tentukan penanganan riwayat sebelum visibility diubah. Tidak ada rewrite riwayat otomatis dalam pekerjaan ini.
- [ ] Cari kredensial, URL privat, alamat kontak pribadi, nama akun, path mesin, inventaris aplikasi dan log sensitif. Jika secret pernah ter-commit, cabut/rotasi secret terlebih dahulu; menghapus teks saja tidak cukup.
- [ ] Periksa `git ls-files` dan `git status --short`. Jangan memakai `git add .` tanpa review. Jangan stage `build/`, `dist/`, installer, katalog lokal, `.bak`, log, environment, history atau preferensi pengguna.
- [ ] Pastikan semua screenshot sudah ditinjau, hanya berisi UI aplikasi dan data demonstrasi, tanpa desktop/aplikasi lain atau informasi pengguna.
- [ ] Pastikan semua tautan dan gambar relatif dapat dibuka dari README pada branch final.
- [ ] Jalankan `python -m unittest discover -s tests -v`, `python -m py_compile dev_cleaner.py tools/capture_screenshots.py`, dan `git diff --check`; catat hasil nyata.
- [ ] Pastikan panduan tidak menjanjikan seluruh Windows didukung, instalasi selalu aman, semua perubahan dapat dibatalkan, atau binary sudah ditandatangani.
- [ ] Tinjau pengaturan Issues, Security Advisories dan kanal pelaporan privat yang benar-benar tersedia sebelum mengundang laporan keamanan.
- [ ] Pemilik mengubah visibility secara manual setelah seluruh blocker diselesaikan. Pekerjaan dokumentasi ini tidak mengubah visibility atau otomatis melakukan push.

## Sebelum menerbitkan executable sebagai Release

- [ ] Build dari commit/tag yang sudah ditinjau, bukan working tree yang belum jelas asal perubahannya.
- [ ] Catat Python, arsitektur, versi dependensi dan PyInstaller; build lokal saat ini bukan build reproducible yang terkunci.
- [ ] Jalankan smoke test binary pada Windows bersih/VM disposable tanpa Python terpasang; pembukaan GUI pada mesin developer saja tidak membuktikan kompatibilitas clean machine.
- [ ] Uji alur berisiko hanya pada data disposable dan snapshot VM; unit test bermock bukan pengujian sistem nyata.
- [ ] Verifikasi skenario tanpa katalog lokal dan tanpa tools opsional; pengguna harus mendapat empty state/error yang jelas.
- [ ] Uji ukuran layar dan DPI yang hendak dinyatakan didukung; ARM64 dan Windows 32-bit belum tervalidasi.
- [ ] Inventaris seluruh komponen yang dibundel beserta teks lisensinya, termasuk dependensi transitif dan native libraries. Catatan Markdown ringkas bukan pengganti kewajiban distribusi lisensi.
- [ ] Hitung SHA256 untuk aset final dan sediakan release notes beserta batasan dukungan. Jangan menganggap hash membuktikan publisher atau keamanan program.
- [ ] Jelaskan status code signing yang sebenarnya. Jangan meminta pengguna mematikan antivirus atau melewati peringatan keamanan tanpa verifikasi.
- [ ] Upload release hanya atas instruksi pemilik; binary lokal di `dist/` tidak otomatis menjadi aset GitHub Release.

## Batas pemeriksaan awal

Pada persiapan ini, inventaris awal Git memperlihatkan dua commit dengan source, launcher, spec, dokumentasi dan tests; tidak ada binary atau katalog yang terlacak pada inventaris tersebut. Pemeriksaan pola pada 20 blob unik tidak menemukan pola kredensial umum yang dicari atau path akun Windows. Pemeriksaan berbasis pola tersebut **terbatas**, bukan audit keamanan menyeluruh atau bukti tidak ada data sensitif.
