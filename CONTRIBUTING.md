# Berkontribusi

Terima kasih telah membantu memperbaiki Dev & AI Cleaner. Perubahan pada utilitas pemeliharaan harus mengutamakan keselamatan data dan klaim yang dapat dibuktikan.

## Sebelum memulai

- Baca [README](README.md), [PRD](docs/PRD.md), [Tech Stack](docs/TECH_STACK.md), dan [keselamatan](docs/SAFETY_AND_PRIVACY.md).
- Laporkan bug biasa dengan template issue dan reproduksi minimum. Untuk kerentanan/data sensitif, ikuti [SECURITY.md](SECURITY.md), bukan issue publik berisi exploit atau data pribadi.
- Diskusikan perubahan besar, dependency baru, format state, atau perilaku destruktif sebelum implementasi. Jangan mengubah visibilitas repo, menulis ulang histori, membuat rilis atau mengunggah biner tanpa persetujuan pemilik.
- Kerjakan branch sendiri; pertahankan perubahan lokal milik orang lain. Jangan reset/clean berkas yang tidak terkait.

## Setup dan validasi

Gunakan environment Windows x64 terpisah sesuai [instalasi](docs/INSTALLATION.md). Jalankan dari root proyek:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Baseline yang dilaporkan adalah 74 tes sebelum perubahan publikasi, bukan jumlah wajib untuk setiap perubahan. Laporkan hasil run aktual, interpreter/OS, dan tes baru yang relevan. Jangan menulis “tested” untuk skenario yang hanya dibaca atau dimock.

Untuk GUI, gunakan data demonstrasi dan jalankan awalnya tanpa Administrator. Jangan menghapus data nyata, mengubah layanan, menjalankan installer atau melakukan move/restore sungguhan hanya untuk menguji layout. Pengujian integrasi destruktif harus disepakati dan dijalankan pada mesin/VM uji dengan backup/snapshot.

## Prinsip implementasi

- Jaga pemisahan scan dan mutasi. Jangan menambahkan auto-clean, auto-uninstall, atau rescan penuh sesudah tindakan inti tanpa keputusan eksplisit.
- Pertahankan pengaman scan/mutasi dan dispatch UI lewat event loop Tk; jangan menganggap thread worker aman mengubah widget langsung.
- Verifikasi hasil sebelum menghapus baris/status sukses; tampilkan kegagalan dan pertahankan data pemulihan.
- Uji kegagalan copy/junction/restore, penyimpanan riwayat, backup registry gagal, interpreter berubah, file terkunci/hilang dan status layanan belum konvergen.
- Jangan melemahkan filter path/protected package, TLS atau proteksi OS untuk mengatasi bug.
- Jangan mengubah kunci internal hanya untuk mengganti label publik. Utamakan label enam menu dalam dokumentasi/screenshot.
- Hindari dependency baru tanpa alasan, lisensi terverifikasi dan pembaruan inventaris. Tidak ada klaim “ringan” atau lebih cepat tanpa pengukuran yang dijelaskan.

## Dokumentasi, privasi, dan hak

- Tulis dokumentasi pengguna dalam bahasa Indonesia yang jelas; nama API/perintah tetap sesuai sumber.
- Screenshot harus **UI asli dengan data demonstrasi**, bukan mockup yang diklaim bukti eksekusi. Redaksi nama akun, path privat, URL bertoken, dan aplikasi/lisensi pribadi.
- Jangan commit `.venv`, `build`, `dist`, installer, katalog privat, backup `.reg`, move history, log diagnostik, credential, atau dataset pengguna.
- Tambahkan hanya materi yang haknya Anda miliki atau lisensinya mengizinkan kontribusi/redistribusi. Pertahankan atribusi pihak ketiga; jangan menyimpulkan hak dari komentar sumber atau menghapus notice karena mengganti nama menu.
- Kontribusi asli yang sengaja diajukan diharapkan tersedia di bawah [MIT proyek](LICENSE); kode/aset pihak ketiga tetap harus diidentifikasi terpisah. Tidak ada persyaratan penyerahan hak cipta pribadi yang dibuat-buat.
- Lihat [third-party notices](docs/THIRD_PARTY_NOTICES.md): metadata CustomTkinter lokal bertentangan dengan teks LICENSE, sehingga distribusi biner memerlukan audit tambahan.

## Pull request

Sertakan masalah yang diselesaikan, scope dan non-scope, perubahan perilaku, risiko/recovery, tes beserta hasil aktual, serta screenshot jika mengubah UI. Tandai pengujian yang belum dilakukan. Perbarui dokumentasi dan [Unreleased](CHANGELOG.md) bila perubahan terlihat oleh pengguna. Jangan membuat versi/tanggal rilis fiktif.

Gerbang publikasi berada di [PUBLICATION_CHECKLIST.md](docs/PUBLICATION_CHECKLIST.md). Perubahan dokumentasi atau unit test lulus tidak otomatis berarti repo/biner siap dipublikasikan; provenance, histori dan pengujian VM bersih tetap harus ditinjau pemilik.

Referensi gaya: [GitHub — About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).
