# E-ProcureCheck

Website verifikasi kode barang pengadaan.

Aplikasi lokal untuk mencari data pengadaan berdasarkan `Unique Code` dengan pencocokan persis. Sumber pengembangan adalah `Dummy_Data_Pengadaan.xlsx` pada sheet `Data Pengadaan`. Workbook dibuka dalam mode read-only; aplikasi tidak membuat data baru dan tidak menyimpan perubahan ke spreadsheet.

## Menjalankan aplikasi

1. Pasang dependensi: `python -m pip install -r requirements.txt`
2. Jalankan server: `python -m Backend.Main`
3. Buka <http://127.0.0.1:8000>

## Konfigurasi sumber data

Pengaturan spreadsheet dummy dan produksi berada terpisah di `Backend/config.py`. Pencarian dan tampilan aplikasi menggunakan antarmuka sumber data di `Backend/data_sources.py`. Sumber aktif saat ini adalah `dummy`; adapter sumber produksi perlu dikonfigurasi sebelum sumber tersebut dipilih.

Nomor kolom memakai indeks mulai dari 1: Unique Code di kolom A, header di baris 1, data mulai baris 2, dan kolom tampilan B–F. Kode dicocokkan sebagai string utuh tanpa menghapus spasi atau mengubah kapitalisasi. Nilai kode bertipe teks dipertahankan persis; nilai angka dengan format nol di Excel juga dikonversi dengan mempertahankan nol di depan.
