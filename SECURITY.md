# Kebijakan keamanan

## Cakupan dukungan

Proyek masih dalam pengembangan. Belum ada matriks versi rilis atau janji backport/SLA keamanan. Laporan sebaiknya ditujukan pada checkout terbaru yang dapat direproduksi, dengan commit, Windows, Python/arsitektur, dan scope tindakan yang jelas. Target Windows 10/11 x64 berbeda dari verifikasi GUI lokal Windows 11 yang telah dilaporkan.

## Melaporkan secara bertanggung jawab

**Jangan membuat issue publik yang memuat credential, data pengguna, exploit destruktif rinci, katalog privat, atau file berbahaya.**

1. Jika tab **Security → Advisories → Report a vulnerability** tersedia pada repositori GitHub ini, gunakan private vulnerability reporting tersebut.
2. Bila kanal privat itu tidak tersedia, belum ada alamat email/kanal privat alternatif yang ditetapkan di dokumen ini. Jangan mengarang atau menggunakan alamat pihak ketiga. Bila perlu, buat issue minimal hanya untuk meminta maintainer menyediakan kanal privat, **tanpa rincian kerentanan, target, atau data sensitif**; tunggu kanal disepakati sebelum berbagi detail.
3. Sertakan deskripsi dampak, commit/lingkungan, langkah reproduksi aman menggunakan fixture, hasil yang diharapkan/aktual, serta mitigasi yang diketahui. Jangan uji pada sistem/data orang lain atau melakukan penghapusan sungguhan untuk membuktikan dampak.
4. Redaksi path akun, token, serial/lisensi, host internal dan paket privat. Jangan lampirkan seluruh `moves.json`, `.reg`, direktori profil atau log mentah.

Tidak ada janji waktu respons/perbaikan atau program bounty yang dinyatakan. Kanal privat GitHub harus diaktifkan pemilik; keberadaan dokumen ini bukan bukti fitur itu sudah aktif.

## Contoh masalah keamanan

- Penghapusan atau pemindahan keluar dari scope yang dipilih, bypass filter path/junction, atau rusaknya jalur recovery.
- Eksekusi input tidak tepercaya melalui metadata katalog/perintah, path traversal, atau penggunaan installer dari sumber tak tervalidasi.
- Bocornya data sensitif lewat log, screenshot, unduhan, redirect, atau berkas state.
- Salah interpreter/target ketika uninstall atau perubahan registry/layanan yang melampaui pilihan pengguna.

Bug tampilan biasa dapat memakai issue publik setelah informasi sensitif dihapus. Kasus berpotensi kehilangan data sebaiknya dihentikan dahulu: simpan salinan/staging/state dan jangan mengulang operasi tanpa rencana recovery.

## Model kepercayaan dan keterbatasan

Aplikasi mempunyai kemampuan destruktif dan beberapa fitur memerlukan Administrator. Konfirmasi, filter, backup dan pengaman mutasi bukan sandbox atau batas keamanan terhadap pengguna/input lokal berbahaya. Katalog/installer merupakan input berisiko tinggi dan tidak boleh berasal dari sumber tidak tepercaya; katalog publik tidak dibundel. Respons HTTP/HTTPS tidak menjamin keamanan unduhan. Jangan menonaktifkan antivirus/SmartScreen/TLS untuk mengatasi kegagalan.

Pemindaian inti lokal tidak berarti semua aksi offline. Pip, link checker, browser, installer dan utilitas Windows bisa menggunakan jaringan. Lokasi state dan redaksi laporan dijelaskan pada [keselamatan dan privasi](docs/SAFETY_AND_PRIVACY.md).

Sebelum publikasi, ikuti [checklist publikasi](docs/PUBLICATION_CHECKLIST.md). Pemeriksaan credential/provenance/histori dan lisensi bundel belum boleh disimpulkan tuntas dari dokumentasi. Menghapus fitur dari working tree tidak menghapus kode lama dari Git history; perubahan histori/visibilitas hanya boleh diputuskan pemilik secara eksplisit.
