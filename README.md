# Legal Complaint Analyzer

Sistem ini menganalisis dokumen PDF laporan pengaduan hukum Indonesia secara otomatis dengan kecerdasan buatan (AI) Gemini dan menyimpan hasil analisis ke database Supabase (PostgreSQL Cloud). Cocok digunakan untuk skrining, pelabelan pasal, dan eksekutif ringkasan laporan pengaduan hukum secara cepat dan konsisten.

***

## 🚀 Fitur Utama
- **Ekstraksi teks otomatis dari PDF** (PyMuPDF, fallback OCR jika perlu)
- **Analisis AI hukum**: deteksi fakta, identifikasi pasal KUHP, ringkasan, confidence score
- **Database Cloud (Supabase)**: Simpan hasil analisis secara terstruktur
- **Audit log** untuk setiap proses
- **Struktur modular** (mudah dikembangkan untuk dashboard/query/admin, dsb)

***

## 📦 Struktur Proyek

```
legal-complaint-analyzer/
├── config/
│   └── database_config.py    # Koneksi Supabase
├── database/
│   ├── schema.sql            # Struktur tabel Supabase
│   └── queries.sql           # Query-query referensi
├── src/
│   ├── pdf_extractor.py      # Ekstraksi teks PDF
│   ├── ai_analyzer.py        # Analisis dengan Gemini AI
│   ├── database.py           # Operasi Supabase
│   └── models.py             # Model data
├── utils/
│   └── helpers.py            # Fungsi singkat/bantuan
├── main.py                   # Script utama
├── requirements.txt
├── .env.example
└── README.md
```

***

## ⚡ Cara Instalasi

### **1. Siapkan Supabase & Database**
1. Buat akun/project di https://supabase.com
2. Di dashboard Supabase, buka menu **SQL Editor**
3. Copy seluruh isi `database/schema.sql` dan jalankan, untuk membuat seluruh tabel dan constraint
4. Ambil **project URL**, **anon key** dan **service_role key** di **Settings > API** pada Supabase

### **2. Siapkan API Gemini**
- Daftar dan ambil API key di https://makersuite.google.com/app/apikey

### **3. Clone Repo & Install Dependency**
```bash
# Clone repo atau copy source code
cd legal-complaint-analyzer
python -m venv venv
venv\Scripts\activate         # Windows
# atau
source venv/bin/activate      # Linux/Mac
pip install --upgrade pip
pip install -r requirements.txt
```

### **4. Konfigurasi Environment (.env)**
Buat file `.env` di root folder, isi sesuai kredensial Anda:

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=anon-key
SUPABASE_SERVICE_KEY=service-role-key (recommended, agar bypass RLS)
GEMINI_API_KEY=your-gemini-api-key
```


### **5. Persiapkan File PDF Laporan**
Letakkan file PDF laporan pengaduan di root folder, misal: `contoh_laporan_pengaduan.pdf`

***

## 👩‍💻 Cara Menjalankan

### **A. Jalankan Analisis Satu File**
```bash
python main.py contoh_laporan_pengaduan.pdf
```

### **B. Output yang Diharapkan**
- Teks PDF berhasil diekstraksi (lihat di log)
- Complaint masuk ke database Supabase (tabel `complaints`)
- Hasil analisis AI tersimpan di `analysis_results`, pasal-pasal di `legal_articles`, rekomendasi di `recommendations`
- Log proses di `analysis_logs`

### **C. Cek Hasil**
- Login ke dashboard Supabase → Table Editor
- Cek tabel **complaints**, **analysis_results**, **legal_articles**
- Semua field terisi otomatis

***

## 🛠️ Fitur Lanjutan
- 👀 **Query data** via Supabase query editor atau script (lihat `database/queries.sql`)
- 📊 **Tambah dashboard** dengan Streamlit, Vue.js, atau tools lain (bisa connect langsung ke Supabase)
- 🚦 **Validasi manual**: Reviewer bisa melakukan validasi/approve dari dashboard custom
- 🔒 **RLS (Row Level Security)**: Untuk security production, pastikan policy sudah sesuai kebutuhan

***

## 📝 Troubleshooting

- **File not found:**
  - Pastikan PDF ada di folder yang sama saat jalankan `main.py`, nama file benar.

- **Supabase row-level security (RLS) error:**
  - Gunakan service_role key di `.env`,
  - atau disable RLS/table policy di Supabase saat development.

- **Value violates check constraint (constraint error):**
  - Pastikan AI memberi output yang sesuai format (lihat allowed values di schema.sql), atau longgarkan constraint-nya di Supabase.

- **AI/Model error (model not available, 404):**
  - Ubah nama model di `src/ai_analyzer.py` ke salah satu yang tersedia: `gemini-1.5-pro`, `gemini-pro`, `gemini-1.5-flash`.

***

## ✍️ Contoh Output CLI

```
🚀 Initializing Legal Complaint Analyzer...
✓ All components initialized
...
=====================================================================
  STEP 2: SAVING COMPLAINT TO DATABASE
=====================================================================
✓ Complaint saved with ID: ...
✓ Complaint number: ADU-2025...
=====================================================================
  STEP 3: AI ANALYSIS
=====================================================================
🤖 Starting AI analysis...
✓ Analysis completed in 14 seconds
✓ AI analysis completed successfully
=====================================================================
  STEP 4: SAVING ANALYSIS RESULTS
=====================================================================
✓ Analysis result created with ID: ...
💼 Saving legal articles...
✓ Saved 1 primary legal articles
📋 Saving recommendations...
✓ Saved 3 recommendations
=====================================================================
  ✅ PROCESSING COMPLETE
=====================================================================
```

***

## 💻 Pengembangan & Customisasi
- Semua konfigurasi modular: login, koneksi API, prompt, constraint database.
- Prompt AI diatur agar selalu output `JSON` terstruktur, mudah dipakai backend maupun front-end.
- Bisa dikembangkan ke batch processing, parallel job, dashboard web, dan fitur lain sesuai kebutuhan.

***
