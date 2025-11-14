from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from src.pdf_extractor import PDFExtractor
from src.ai_analyzer import LegalAIAnalyzer
from supabase import create_client
import os, tempfile
from mangum import Mangum
handler = Mangum(app)

app = FastAPI()

@app.post("/analyze")
async def analyze_laporan(file: UploadFile = File(...)):
    # 1. Simpan file PDF ke temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2. Upload ke Supabase Storage (optional)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    bucket_name = "complaint-pdfs"
    storage_path = f"user_uploads/{file.filename}"
    with open(tmp_path, "rb") as f:
        sb.storage().from_(bucket_name).upload(storage_path, f, {"content-type": "application/pdf"})
    storage_url = f"{bucket_name}/{storage_path}"

    # 3. Ekstraksi teks PDF
    extractor = PDFExtractor()
    doc_text = extractor.extract_text(tmp_path)

    # 4. Kirim ke AI Analyzer untuk analisis hukum
    analyzer = LegalAIAnalyzer()
    hasil_ai = analyzer.analyze(doc_text)

    # 5. Response ke frontend: hasil AI (JSON), status sukses
    os.remove(tmp_path)
    return JSONResponse({
        "success": True,
        "filename": file.filename,
        "storage_path": storage_url,
        "analysis_result": hasil_ai
    })

@app.get("/")
async def root():
    return {"message": "API Online"}
