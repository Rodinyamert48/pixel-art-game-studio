# Pixel Art Game Studio

[← README utama](../../README.md) · Bahasa Indonesia · Terjemahan berbantuan mesin; menunggu tinjauan penutur asli.

<!-- section: overview -->
## Ikhtisar

Pixel Art Game Studio adalah sebuah skill untuk Claude Code beserta tim berisi delapan subagen
spesialis untuk membuat game 2D bergaya pixel art yang orisinal. Anda menjelaskan game yang Anda
bayangkan, hal yang tidak Anda sukai dari hasil saat ini, dan apa yang perlu diubah berikutnya. Claude
merencanakan pekerjaan, menulis kode, membuat grafik, menjalankan pengujian, memperbaiki bug yang dapat
direproduksi, dan hanya melaporkan hal yang benar-benar sudah diverifikasi.

Alat ini ditujukan untuk petualangan naratif yang santai, simulasi kehidupan dan pertanian, RPG yang
kaya dialog, game eksplorasi dengan sudut pandang dari atas, dan game teka-teki, tetapi juga bisa
dipakai untuk ide 2D orisinal lainnya. Empat bagian dipisahkan: **skill** (instruksi), **agen**
(spesialis), **skrip** (alat deterministik), dan **game Anda** (direktori proyeknya sendiri).

<!-- section: features -->
## Fitur

- Alur kerja Game Director yang mengubah ide kasar menjadi desain singkat dan satu putaran permainan
  minimum yang bisa dimainkan.
- Delapan spesialis dengan tanggung jawab yang jelas, daftar alat yang dibatasi, dan laporan yang
  terstruktur.
- Pixel art prosedural: spesifikasi JSON diubah menjadi sprite sheet PNG sungguhan, metadata, dan
  pratinjau. Spesifikasi yang sama selalu menghasilkan byte yang sama.
- Kontrak data untuk peta, dekorasi, dialog, misi, item, dan terjemahan, dengan validator yang
  menemukan pintu keluar yang tidak terjangkau, cabang dialog yang mustahil, dan kunci teks yang hilang.
- Penjaminan mutu dengan tingkat keparahan, laporan cacat yang dapat direproduksi, serta perbaikan yang
  diverifikasi dengan uji regresi.
- Pemasang (installer) yang aman dengan mode simulasi, deteksi konflik, cadangan, dan penghapusan yang
  hati-hati.

<!-- section: agents -->
## Tim agen

Ada sembilan peran. **Game Director** adalah skill itu sendiri dan berjalan di sesi utama Claude Code
Anda: ia menjaga desain, menulis rincian tugas, memeriksa setiap hasil, dan memutuskan kapan sesuatu
sudah selesai. Kedelapan subagen adalah:

| Agen | Tanggung jawab |
| --- | --- |
| `pixel-artist` | arahan seni, spesifikasi aset, sprite dan tile yang dihasilkan |
| `npc-story-engineer` | karakter, dialog bercabang, penanda (flag), misi |
| `world-builder-level-design` | tata letak peta, tabrakan, titik muncul, pintu keluar |
| `world-builder-environmental-content` | dekorasi, tempat menarik, suasana setiap wilayah |
| `ui-engineer` | menu, HUD, kotak dialog, layar inventaris dan penyimpanan |
| `gameplay-engineer` | gerakan, status permainan, inventaris, misi, penyimpanan |
| `qa-tester` | pengujian, menjalankan tes, laporan cacat |
| `bug-fixer` | perbaikan akar masalah beserta uji regresi |

Detail lebih lanjut: [AGENTS.md](../AGENTS.md).

<!-- section: architecture -->
## Arsitektur

Director adalah skill dan bukan subagen, karena ia harus melihat permintaan Anda dan memegang satu
sumber kebenaran (`design/GAME_DESIGN.md`, `ART_DIRECTION.md`, dan lima dokumen singkat lainnya).
Spesialis menerima rincian tugas, bekerja pada berkas yang menjadi tanggung jawabnya, lalu memberikan
laporan; mereka tidak dapat menjalankan agen lain. Konten game disimpan di folder `data/` yang tidak
bergantung pada engine, sehingga cerita, level, dan lingkungan bisa dikerjakan secara paralel dan
diperiksa tanpa menjalankan engine. Jika subagen tidak tersedia, Director menjalankan langkah yang sama
sendiri, satu per satu. Lihat [ARCHITECTURE.md](../ARCHITECTURE.md).

<!-- section: prerequisites -->
## Prasyarat

- Claude Code (diperiksa dengan versi 2.1.312).
- Python 3.9 atau yang lebih baru; tidak perlu paket tambahan.
- Untuk game sungguhan, engine pilihan Anda, misalnya Godot 4 atau .NET SDK untuk MonoGame. Skill ini
  memeriksa apa yang sudah terpasang dan bertanya sebelum memasang apa pun.

<!-- section: installation -->
## Pemasangan

Kloning repositori, lalu pilih cara pemasangan. Lihat dulu setiap perubahan dengan `--dry-run`:

```bash
python scripts/install.py --scope project --project-dir ../my-game --dry-run
python scripts/install.py --scope project --project-dir ../my-game
python scripts/install.py --scope user
```

Cakupan proyek menulis ke `<project>/.claude/`, sedangkan cakupan pengguna menulis ke `~/.claude/`.
Berkas yang sudah ada dan tidak dibuat oleh pemasang tidak akan pernah diganti. Gunakan `--update` untuk
memperbarui pemasangan (berkas lama dicadangkan) dan `--uninstall` untuk menghapus hanya berkas yang
dipasangnya dan belum diubah. Anda juga bisa menjalankan Claude Code langsung di dalam repositori ini
atau menyalin foldernya secara manual. Semua pilihan ada di [INSTALLATION.md](../INSTALLATION.md).

<!-- section: quick-start -->
## Mulai cepat

Buka Claude Code di folder proyek Anda lalu ketik:

```text
/pixel-art-game-studio Buat game pixel art orisinal yang santai dengan sudut pandang dari atas, berisi kota kecil, hutan, tiga NPC, dialog bercabang, siklus siang dan malam, serta fitur simpan.
```

Director memilih nilai bawaan yang masuk akal, menulis desain singkat, dan membangun versi kecil yang
bisa dimainkan terlebih dahulu. Untuk memanggil satu spesialis secara langsung, sebutkan namanya,
misalnya `@agent-qa-tester`.

<!-- section: examples -->
## Contoh permintaan

```text
/pixel-art-game-studio Tambahkan wilayah rawa berkabut dengan dua NPC dan misi yang punya dua akhir.
/pixel-art-game-studio Kotanya terasa kosong. Tambahkan detail dan penemuan kecil, tetapi biarkan jalan tetap lapang.
/pixel-art-game-studio Periksa game ini, jalankan semua tes yang ada, dan perbaiki bug yang bisa direproduksi.
```

Anda boleh menulis permintaan dalam bahasa apa pun. Contoh lengkap tersedia di
[examples](../../examples/example-game-idea.md).

<!-- section: workflows -->
## Alur kerja

- **Membuat game**: dari ide hingga pengiriman dalam 14 tahap, dimulai dengan putaran permainan minimum.
- **Mengembangkan game**: memeriksa proyek yang ada, membuat perubahan koheren yang paling kecil, dan
  memeriksa regresi.
- **Menguji dan memperbaiki**: menjalankan tes sungguhan, melaporkan cacat, lalu memperbaiki cacat yang
  sudah dikonfirmasi dengan jumlah percobaan yang terbatas.
- **Membuat aset**: arahan seni lebih dulu, kemudian spesifikasi, berkas PNG, dan pratinjau.
- **Pemeriksaan rilis**: keputusan yang didukung bukti: siap, siap dengan masalah yang diketahui, atau
  belum siap.

Ringkasan: [WORKFLOWS.md](../WORKFLOWS.md).

<!-- section: testing -->
## Pengujian dan perbaikan bug

Penguji QA mencari tahu alat apa saja yang benar-benar dimiliki game, mengubah kriteria penerimaan
menjadi tes, menjalankannya, lalu menulis laporan cacat lengkap dengan tingkat keparahan, langkah, dan
bukti. Perbaikan bug mereproduksi setiap cacat, memperbaiki akar masalah, menambahkan uji regresi, dan
menjalankan ulang pemeriksaan. Melemahkan atau menghapus tes tidak pernah diizinkan. Untuk menguji
repositori ini:

```bash
python -m unittest discover -s tests -v
python scripts/validate_repository.py
```

Detail: [TESTING.md](../TESTING.md).

<!-- section: limitations -->
## Keterbatasan

- Alat ini tidak membuat game komersial yang sudah jadi dengan sendirinya; harapkan fondasi yang
  berfungsi dan terus berkembang berkat masukan Anda.
- Tanpa engine yang terpasang, hanya data, aset, dan logika yang tidak bergantung pada engine yang bisa
  diverifikasi.
- Pemeriksaan struktural tidak bisa menilai apakah seni terlihat bagus atau game terasa seru; untuk itu
  diperlukan manusia.
- Terjemahan dibuat dengan bantuan mesin dan masih menunggu tinjauan penutur asli.

<!-- section: troubleshooting -->
## Pemecahan masalah

Jika skill tidak muncul, pastikan `SKILL.md` berada di `.claude/skills/pixel-art-game-studio/`. Jika agen
tidak ditemukan, mulai ulang Claude Code setelah membuat `.claude/agents/`. Jika pemasang berhenti
dengan kode 2, ia menemukan berkas yang tidak dibuatnya; baca rencana yang ditampilkan. Jawaban lainnya
ada di [TROUBLESHOOTING.md](../TROUBLESHOOTING.md).

<!-- section: contributing -->
## Berkontribusi

Kontribusi sangat diterima, terutama tinjauan terjemahan ini oleh penutur asli. Baca
[CONTRIBUTING.md](../CONTRIBUTING.md) dan [Kode Etik](../CODE_OF_CONDUCT.md) sebelum membuka pull
request.

<!-- section: license -->
## Lisensi

Pixel Art Game Studio dirilis dengan [Lisensi MIT](../../LICENSE). Game yang Anda buat dengannya adalah
milik Anda.
