import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse

# ✅ Dinamiski pievieno /src mapi Python path
import sys
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from healthdq.pipeline import run_pipeline

# ------------------------------------------------------
# API konfigurācija
# ------------------------------------------------------
app = FastAPI(
    title="healthdq-ai API",
    description="REST API veselības datu kvalitātes novērtēšanai un uzlabošanai (Precision • Completeness • Reusability)",
    version="1.0.0"
)

CONFIG_PATH = os.path.abspath("healthdq_ai/configs/rules.yml")
OUT_DIR = os.path.abspath("out")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------
# 1️⃣ Augšupielādē datu failu un palaiž AI cauruļvadu
# ------------------------------------------------------
@app.post("/run")
async def run_quality_pipeline(
    file: UploadFile = File(...),
    kind: str = Form("csv")
):
    """
    Augšupielādē datu failu un palaid AI cauruļvadu (run_pipeline)
    """
    try:
        input_path = os.path.join(OUT_DIR, file.filename)
        with open(input_path, "wb") as f:
            f.write(await file.read())

        df, issues, metrics = run_pipeline(input_path, kind, CONFIG_PATH, OUT_DIR)

        return {
            "status": "success",
            "records": len(df),
            "issues": len(issues),
            "metrics": metrics
        }

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# ------------------------------------------------------
# 2️⃣ Lejupielādē rezultātus (cleaned.csv, issues.csv utt.)
# ------------------------------------------------------
@app.get("/download/{filename}")
async def download_result(filename: str):
    path = os.path.join(OUT_DIR, filename)
    if not os.path.exists(path):
        return JSONResponse(content={"error": f"File '{filename}' not found"}, status_code=404)
    return FileResponse(path, filename=filename)

# ------------------------------------------------------
# 3️⃣ Veselības pārbaude (ping)
# ------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "✅ healthdq-ai API darbojas",
        "endpoints": {
            "POST /run": "Augšupielādē failu un palaiž cauruļvadu",
            "GET /download/{filename}": "Lejupielādē apstrādātos datus",
        }
    }
