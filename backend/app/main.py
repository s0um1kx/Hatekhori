import asyncio
import io
import sys
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from pipeline.cleanup import OUTPUT_DIR, OUTPUT_MAX_AGE_S, UPLOAD_MAX_AGE_S, sweep
from pipeline.ingest import UPLOAD_DIR, UnsupportedFileType, UploadTooLarge, save_upload, upload_path
from pipeline.run import make_font
from pipeline.sheet import generate_guideline_sheet
from pipeline.validate import BadSheetShape

app = FastAPI(title="Hatekhori", version="0.1.0")

SWEEP_INTERVAL_SECONDS = 3600  # once an hour


async def _periodic_sweep() -> None:
    while True:
        try:
            sweep(UPLOAD_DIR, UPLOAD_MAX_AGE_S)
            sweep(OUTPUT_DIR, OUTPUT_MAX_AGE_S)
        except Exception:
            pass  # best-effort: a failed sweep must never take the app down
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)


@app.on_event("startup")
async def start_background_sweep() -> None:
    asyncio.create_task(_periodic_sweep())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/guideline-sheet.png")
def guideline_sheet() -> Response:
    img = generate_guideline_sheet()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)) -> dict:
    try:
        return {"id": save_upload(await file.read())}
    except (UnsupportedFileType, UploadTooLarge) as e:
        raise HTTPException(status_code=400, detail=str(e))


def _font_path(upload_id: UUID) -> Path:
    return OUTPUT_DIR / f"{upload_id}.otf"


@app.post("/generate/{upload_id}")
def generate(upload_id: UUID) -> dict:
    photo = upload_path(upload_id)
    if not photo.exists():
        raise HTTPException(status_code=404, detail="No upload found with that id.")
    try:
        return make_font(photo, _font_path(upload_id))
    except BadSheetShape as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        photo.unlink(missing_ok=True)  # the raw photo is never kept past its one use (AGENTS.md §7)


@app.get("/download-font/{upload_id}")
def download_font(upload_id: UUID, inline: bool = False) -> Response:
    font_path = _font_path(upload_id)
    if not font_path.exists():
        raise HTTPException(status_code=404, detail="No font for this id yet.")

    # inline=true is what the in-page live preview loads as a web font;
    # without it the browser is told to save the file instead.
    headers = {}
    if not inline:
        headers["Content-Disposition"] = f'attachment; filename="hatekhori-{upload_id}.otf"'

    return Response(content=font_path.read_bytes(), media_type="font/otf", headers=headers)


# Mounted LAST and deliberately at "/" — Starlette matches the explicit
# API routes above first; this only catches whatever they don't. Serves
# frontend/index.html at "/" and everything else in frontend/ alongside
# it, so the browser and the API share one origin and never need CORS.
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
