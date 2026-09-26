"""Hatekhori backend — FastAPI entrypoint.

Milestone 1 scope only: this file exists so the service boots and has a
health check. Ingest/preprocess/segment/vectorize/metrics/compile routes
are added in later parts, not here.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from PIL import Image

from pipeline.ingest import UPLOAD_DIR, UnsupportedFileType, UploadTooLarge, save_upload
from pipeline.preprocess import run_preprocess

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Hatekhori", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    file_bytes = await file.read()
    try:
        return save_upload(file_bytes, file.filename)
    except (UnsupportedFileType, UploadTooLarge) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/preprocess/{upload_id}")
def preprocess(upload_id: str) -> dict:
    matches = list(UPLOAD_DIR.glob(f"{upload_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="No upload found with that id.")

    with Image.open(matches[0]) as img:
        cleaned = run_preprocess(img)
        dest = OUTPUT_DIR / f"{upload_id}_preprocessed.png"
        cleaned.save(dest, format="PNG")

    return {"id": upload_id, "preprocessed_path": str(dest)}
