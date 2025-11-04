"""
api — veselības datu kvalitātes REST API modulis

Šis modulis nodrošina programmatisku piekļuvi *healthdq-ai* funkcionalitātei.
Tas ļauj integrēt MI datu kvalitātes novērtēšanas cauruļvadu (pipeline)
citās sistēmās vai automatizētos eksperimentos, ievērojot FAIR un reproducējamības principus.

Autore: Agate Jarmakoviča
Versija: 1.2
Datums: 2025-10-30
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
import os
import tempfile
from ..pipeline import run_pipeline

app = FastAPI(
    title="healthdq-ai API",
    description="REST API veselības datu kvalitātes uzlabošanai ar MI aģentiem (Precision, Completeness, Reusability).",
    version="1.2"
)


@app.post("/process")
async def process_dataset(
    file: UploadFile = File(...),
    format: str = Form("csv"),
    config: str = Form("configs/rules.yml"),
    out_dir: str = Form("out")
):
    """
    Apstrādā augšupielādēto datu kopu un atgriež rezultātus JSON formātā.
    """
    try:
        os.makedirs(out_dir, exist_ok=True)
        tmp_path = os.path.join(tempfile.gettempdir(), file.filename)
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        df, issues, metrics = run_pipeline(tmp_path, format, config, out_dir)

        return JSONResponse({
            "status": "success",
            "records_processed": len(df),
            "issues_detected": len(issues),
            "metrics": metrics
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


@app.get("/health")
def health_check():
    """Vienkārša sistēmas veselības pārbaude."""
    return {"status": "ok", "service": "healthdq-ai API"}
