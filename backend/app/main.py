"""Hatekhori backend — FastAPI entrypoint.

Milestone 1 scope only: this file exists so the service boots and has a
health check. Ingest/preprocess/segment/vectorize/metrics/compile routes
are added in later parts, not here.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File

from pipeline.ingest import UnsupportedFileType, UploadTooLarge, save_upload

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
