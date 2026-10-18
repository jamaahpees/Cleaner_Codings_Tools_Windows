# Pemberitahuan pihak ketiga

Lisensi [MIT proyek](../LICENSE) berlaku pada kontribusi asli yang haknya dimiliki kontributor. Lisensi tersebut **tidak** mengganti lisensi dependency/aset, memberi hak merek, atau memastikan provenance kode eksternal. Tidak ada pernyataan afiliasi/endorsement dengan pembuat paket atau vendor Windows.

## Dasar pemeriksaan

Snapshot 18 Oktober 2026 memakai `importlib.metadata` pada paket terpasang dan membaca teks lisensi yang disertakan. Versi lokal bukan pin atau SBOM lengkap. Path di bawah relatif terhadap `site-packages` interpreter terkait; periksa distribusi yang benar-benar Anda bundel. Metadata dapat salah atau tidak lengkap, sehingga teks paket juga dicatat.

| Distribusi | Metadata teramati | Berkas lisensi yang diperiksa dan catatan |
|---|---|---|
| **ttkbootstrap 2.2.3** | `License-Expression: MIT AND (Apache-2.0 OR BSD-2-Clause)` | `ttkbootstrap-2.2.3.dist-info/licenses/LICENSE`: MIT, Copyright (c) 2021–2026 Israel Dryer. `ttkbootstrap/assets/icons/LICENSE`: MIT, Copyright (c) 2019–2024 The Bootstrap Authors. Ekspresi metadata lebih luas daripada dua teks ini; jangan menghilangkan kewajiban komponen lain. |
| **CustomTkinter 6.0.0** | `License: Creative Commons Zero v1.0 Universal`; classifier menyebut MIT | `customtkinter-6.0.0.dist-info/licenses/LICENSE`: **MIT**, Copyright (c) 2023 Tom Schimansky. Ada konflik metadata/teks; jangan menyimpulkan paket bebas atribusi berdasarkan CC0 saja. |
| **darkdetect 0.8.0** | BSD-3-Clause | `darkdetect-0.8.0.dist-info/LICENSE`: Copyright (c) 2019 Alberto Sottile; retain copyright, conditions dan disclaimer; tidak boleh memakai nama untuk endorsement tanpa izin. |
| **psutil 7.2.2** | BSD-3-Clause | `psutil-7.2.2.dist-info/LICENSE`: Copyright (c) 2009 Jay Loden, Dave Daeschler, Giampaolo Rodola; retain copyright, conditions dan disclaimer; larangan endorsement tanpa izin. |
| **Send2Trash 2.1.0** | `License-Expression: BSD-3-Clause` | `send2trash-2.1.0.dist-info/licenses/LICENSE`: Copyright (c) 2017 Virgil Dupras; retain copyright, conditions dan disclaimer; nama Hardcoded Software Inc./kontributor tidak boleh dipakai untuk endorsement tanpa izin. |
| **pywin32 312** | PSF | `pywin32-312.dist-info/licenses/win32/License.txt`: Copyright (c) 1994–2008 Mark Hammond, ketentuan redistribusi dan disclaimer tersendiri. Paket memuat banyak lisensi komponen lain; label metadata PSF bukan pengganti semuanya. |
| **PyInstaller 6.3.0** | GPLv2-or-later dengan pengecualian distribusi khusus | `pyinstaller-6.3.0.dist-info/COPYING.txt`: GPL-2.0-or-later, bootloader exception, runtime hooks Apache-2.0, bagian isolated juga tersedia dengan MIT. Copyright PyInstaller Development Team serta pendahulu tercantum pada berkas lengkap. Pengecualian bootloader bukan relicensing seluruh dependency menjadi MIT. |
| **Pillow 12.3.0** | `License-Expression: MIT-CMU` | `pillow-12.3.0.dist-info/licenses/LICENSE`: PIL Copyright 1997–2011 Secret Labs AB; 1995–2011 Fredrik Lundh and contributors; Pillow Copyright 2010 Jeffrey 'Alex' Clark and contributors. Teks yang sama memuat banyak lisensi native dependency; jangan memangkas hanya bagian MIT-CMU. |

### Perhatian khusus terhadap aset/native library

Lisensi Pillow yang diperiksa mencakup, antara lain, Brotli, FreeType, HarfBuzz, Little CMS, libavif, libjpeg-turbo, libpng, libwebp, OpenJPEG, libtiff, XZ/liblzma dan zlib-ng. Komponen yang masuk bundel bergantung pada wheel/build; daftar ini bukan klaim semua dimuat saat runtime. Bila komponen terkait didistribusikan, pertahankan seluruh notice dan teks lisensi yang berlaku.

Untuk komponen Pillow yang memuatnya: **This software is based in part on the work of the Independent JPEG Group.** Komponen terkait juga didasarkan sebagian pada karya FreeType Team (https://freetype.org); teks lisensi FreeType dan tahun copyright versi yang benar harus disertakan bersama bundel. Jangan mengarang tahun atau memakai placeholder pada rilis.

Python, Tcl/Tk, native DLL, dependency transitif tambahan dan hook build memerlukan pemeriksaan lisensi dari distribusi target. Utilitas Windows dan installer/runtime eksternal tunduk pada ketentuan vendor masing-masing; tersedianya tautan tidak berarti hak untuk membundel binernya.

## Kewajiban sebelum distribusi executable

1. Inventaris semua paket, DLL, aset, bootloader dan hook yang benar-benar masuk hasil build (termasuk transitif).
2. Salin **teks lisensi/notice lengkap asli**, termasuk copyright dan disclaimer, dalam bahan pendamping distribusi. Tabel ringkas dan tautan dokumen ini **bukan pengganti** teks yang diwajibkan lisensi.
3. Audit konflik metadata/teks, terutama CustomTkinter 6.0.0; konfirmasi distribusi/upstream yang digunakan dan simpan bukti sebelum publikasi biner. Jangan memilih interpretasi paling permisif tanpa verifikasi.
4. Cocokkan ketentuan aset ttkbootstrap/Pillow dan komponen pywin32 yang benar-benar terkoleksi; jangan menganggap semua paket hanya mempunyai satu lisensi.
5. Pertahankan atribusi yang diwajibkan pada kode eksternal; komentar/header atau kemiripan UI bukan bukti hak penggunaan. Review asal-usul dan histori secara terpisah.
6. Jangan menyertakan katalog privat, installer tak berizin, patch aktivasi, atau biner hasil unduhan yang tidak punya hak redistribusi.

Inventaris bundel lengkap dan penyelesaian konflik lisensi masih merupakan **gerbang rilis**, bukan hasil yang sudah disertifikasi oleh dokumen ini. Baca [checklist publikasi](PUBLICATION_CHECKLIST.md).

## Referensi upstream

Teks yang dikirim bersama versi/wheel target tetap harus diverifikasi, bukan menganggap branch upstream terbaru identik dengan paket terpasang.

- ttkbootstrap: https://github.com/israel-dryer/ttkbootstrap
- Bootstrap Icons: https://github.com/twbs/icons
- CustomTkinter: https://github.com/TomSchimansky/CustomTkinter
- darkdetect: https://github.com/albertosottile/darkdetect
- psutil: https://github.com/giampaolo/psutil
- Send2Trash: https://github.com/arsenetar/send2trash
- pywin32: https://github.com/mhammond/pywin32
- PyInstaller: https://pyinstaller.org/en/stable/license.html
- Pillow: https://pillow.readthedocs.io/en/stable/about.html
- Python: https://docs.python.org/3/license.html
- Tcl/Tk: https://www.tcl.tk/software/tcltk/license.html
