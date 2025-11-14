from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/analyze")
async def analyze_laporan(file: UploadFile = File(...)):
    # ... baca file, proses, dst seperti di jawaban sebelumnya
    content = await file.read()
    # Simulasi response cepat
    return JSONResponse(content={"success": True, "filename": file.filename, "result": "ok"})

@app.get("/")
async def root():
    return {"message": "API Online"}
