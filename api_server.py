import os
import sys
import tempfile
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum
from contextlib import asynccontextmanager

# --- Konfigurasi Path dan Logging ---
# Tambahkan root directory ke sys.path agar bisa impor 'src'
try:
    APP_ROOT = Path(__file__).parent
    sys.path.insert(0, str(APP_ROOT))
    
    if 'src' not in [p.name for p in APP_ROOT.iterdir()]:
        APP_ROOT = Path(__file__).parent.parent
        sys.path.insert(0, str(APP_ROOT))

    load_dotenv(APP_ROOT / '.env')
    
    # Impor modul Anda SETELAH sys.path diatur
    from main import LegalComplaintProcessor
    from src.database import DatabaseManager
    from src.ai_analyzer import LegalAIAnalyzer
    
except ImportError as e:
    logging.fatal(f"FATAL: Gagal impor modul. Pastikan struktur file benar. Error: {e}")
    sys.exit(1) # Keluar jika impor dasar gagal

# Inisialisasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Manajemen Lifespan (Inisialisasi Saat Startup) ---

# Variabel global untuk menyimpan instance prosesor
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Kode ini berjalan SAAT STARTUP ---
    logger.info("Server startup... memulai inisialisasi.")
    
    try:
        # 1. Coba inisialisasi Prosesor utama
        #    Ini akan memicu __init__ dari LegalComplaintProcessor
        #    yang juga akan memicu __init__ dari DatabaseManager dan LegalAIAnalyzer
        logger.info("Menginisialisasi LegalComplaintProcessor...")
        processor = LegalComplaintProcessor()
        
        # Simpan prosesor di state aplikasi
        app_state["processor"] = processor
        logger.info("LegalComplaintProcessor berhasil diinisialisasi.")
        
    except ValueError as e:
        # Ini kemungkinan besar adalah error ENV (misal: "Missing credentials")
        logger.error(f"FATAL (ValueError): Gagal inisialisasi. Cek Environment Variables! Error: {e}")
        app_state["processor"] = None
    except Exception as e:
        # Tangkap semua error lain saat startup
        logger.error(f"FATAL (Exception): Gagal inisialisasi LegalComplaintProcessor. Error: {e}")
        app_state["processor"] = None
        
    # 'yield' menandakan aplikasi siap menerima request
    yield
    
    # --- Kode ini berjalan SAAT SHUTDOWN (tidak terlalu relevan di Vercel) ---
    logger.info("Server shutdown...")
    app_state.clear()


# --- Inisialisasi Aplikasi ---
app = FastAPI(
    title="Legal Complaint Analyzer API",
    description="API untuk menganalisis dokumen laporan pengaduan hukum",
    version="1.0.0",
    lifespan=lifespan  # Gunakan lifespan manager yang baru
)
handler = Mangum(app)


# --- Endpoints ---

@app.get("/")
async def root():
    """Endpoint root untuk memeriksa status API."""
    if app_state.get("processor") is None:
        # Jika inisialisasi gagal, kembalikan error
        raise HTTPException(
            status_code=500,
            detail="Server Gagal Dikonfigurasi. Cek log untuk error inisialisasi."
        )
    return {"message": "Legal Complaint Analyzer API Online dan Terkonfigurasi."}

@app.post("/analyze")
async def analyze_laporan(file: UploadFile = File(...)):
    """
    Endpoint utama untuk meng-upload dan menganalisis laporan pengaduan PDF.
    """
    processor = app_state.get("processor")
    
    if not processor:
        logger.error("Prosesor tidak terinisialisasi. Endpoint /analyze tidak bisa bekerja.")
        raise HTTPException(
            status_code=500,
            detail="Server tidak terkonfigurasi dengan benar (Prosesor gagal). Hubungi administrator."
        )

    # Vercel hanya mengizinkan penulisan ke direktori /tmp
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename)

    logger.info(f"Menerima file: {file.filename}. Menyimpan ke: {temp_path}")

    try:
        # Simpan file yang di-upload ke /tmp
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File berhasil disimpan. Memulai pemrosesan untuk: {temp_path}")

        # Gunakan LegalComplaintProcessor untuk menjalankan alur lengkap
        result = processor.process_complaint(temp_path, uploaded_by='system-api')
        
        if not result.get('success'):
            logger.error(f"Pemrosesan gagal: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Gagal memproses file: {result.get('error')}"
            )

        # Jika sukses, kembalikan hasil
        logger.info(f"Analisis berhasil untuk {file.filename}. Complaint ID: {result.get('complaint_id')}")
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Analisis berhasil dan data telah disimpan.",
                "filename": file.filename,
                "result": result
            }
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Terjadi kesalahan internal saat memproses {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Terjadi kesalahan internal pada server: {e}"
        )
    finally:
        # Selalu hapus file sementara setelah selesai
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.info(f"File sementara dihapus: {temp_path}")
            except Exception as e:
                logger.error(f"Gagal menghapus file sementara {temp_path}: {e}")