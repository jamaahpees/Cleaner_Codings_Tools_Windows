# Changelog

Perubahan penting bagi pengguna dicatat di sini. Bagian **Unreleased** bukan rilis yang sudah diterbitkan; belum ada nomor versi/tanggal rilis publik yang dinyatakan.

## [Unreleased]

### Added

- Dokumentasi publik berbahasa Indonesia: panduan enam menu/subview, setup/build, troubleshooting, keselamatan/privasi dan notice dependency.
- Lisensi MIT untuk kontribusi asli proyek, kebijakan kontribusi/keamanan, dan template issue/pull request.
- Dokumentasi screenshot UI asli dengan data demonstrasi serta gerbang publikasi yang membedakan hasil uji dari target dukungan.

### Changed

- README, PRD dan Tech Stack menjelaskan implementasi ttkbootstrap melalui adapter kompatibilitas CTk, dependensi runtime versus build, dan App Setup tanpa katalog publik bawaan.
- Nama menu publik diseragamkan menjadi Smart Cleaner, App Mover & Restore, Duplicate File Finder (Safe), Python Library Manager, Startup & Windows Services, serta System Toolbox (Tweaks & Tools); kunci internal tetap.
- Perilaku startup Smart Scan opsional default OFF dan pembaruan hasil mutasi inti tanpa full rescan otomatis didokumentasikan sebagai baseline, bukan roadmap yang belum ada.

### Security

- Batas pengujian Windows, risiko registry/layanan/move/uninstall, jaringan dan state/log lokal dinyatakan tanpa klaim keamanan universal.
- Konflik metadata dan teks lisensi dependency serta perlunya review provenance/histori dicatat sebagai gerbang sebelum distribusi, bukan dinyatakan selesai.

Catatan ini tidak mengklaim bahwa seluruh operasi sistem sudah diuji pada VM bersih atau bahwa executable resmi telah ditandatangani/dipublikasikan.
