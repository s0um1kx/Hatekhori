"""Hatekhori backend — FastAPI entrypoint.

Pipeline endpoints (ingest -> preprocess -> segment -> vectorize ->
metrics -> compile) plus serving the frontend as static files at "/".
"""

import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from PIL import Image

from pipeline.compile import build_font
from pipeline.ingest import UPLOAD_DIR, UnsupportedFileType, UploadTooLarge, save_upload
from pipeline.preprocess import run_preprocess
from pipeline.metrics import compute_global_metrics, glyph_ink_bbox, side_bearings
from pipeline.segment import char_grid, crop_glyphs
from pipeline.sheet import generate_guideline_sheet
from pipeline.vectorize import path_to_svg, trace_glyph

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Hatekhori", version="0.1.0")


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


@app.post("/segment/{upload_id}")
def segment(upload_id: str) -> dict:
    preprocessed_path = OUTPUT_DIR / f"{upload_id}_preprocessed.png"
    if not preprocessed_path.exists():
        raise HTTPException(status_code=404, detail="Run /preprocess for this upload id first.")

    glyphs_dir = OUTPUT_DIR / upload_id / "glyphs"
    glyphs_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(preprocessed_path) as img:
        glyphs = crop_glyphs(img)

    manifest = []
    for index, char in enumerate(char_grid()):
        # Index prefix avoids Windows filesystem case-insensitivity
        # colliding "A.png" with "a.png".
        dest = glyphs_dir / f"{index:02d}_{char}.png"
        glyphs[char].save(dest, format="PNG")
        manifest.append({"char": char, "path": str(dest)})

    return {"id": upload_id, "glyph_count": len(manifest), "glyphs": manifest}


@app.post("/vectorize/{upload_id}")
def vectorize(upload_id: str) -> dict:
    glyphs_dir = OUTPUT_DIR / upload_id / "glyphs"
    if not glyphs_dir.exists():
        raise HTTPException(status_code=404, detail="Run /segment for this upload id first.")

    vectors_dir = OUTPUT_DIR / upload_id / "vectors"
    vectors_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for index, char in enumerate(char_grid()):
        glyph_path = glyphs_dir / f"{index:02d}_{char}.png"
        if not glyph_path.exists():
            continue

        with Image.open(glyph_path) as img:
            path = trace_glyph(img)
            svg = path_to_svg(path, img.width, img.height)

        dest = vectors_dir / f"{index:02d}_{char}.svg"
        dest.write_text(svg, encoding="utf-8")
        manifest.append({"char": char, "path": str(dest)})

    return {"id": upload_id, "vector_count": len(manifest), "vectors": manifest}


@app.post("/metrics/{upload_id}")
def metrics(upload_id: str) -> dict:
    glyphs_dir = OUTPUT_DIR / upload_id / "glyphs"
    if not glyphs_dir.exists():
        raise HTTPException(status_code=404, detail="Run /segment for this upload id first.")

    per_glyph = {}
    for index, char in enumerate(char_grid()):
        glyph_path = glyphs_dir / f"{index:02d}_{char}.png"
        if not glyph_path.exists():
            continue

        with Image.open(glyph_path) as img:
            bbox = glyph_ink_bbox(img)
            bearings = side_bearings(img, bbox)
            per_glyph[char] = {
                "bbox": bbox,
                "crop_height": img.height,
                **bearings,
            }

    global_metrics = compute_global_metrics(per_glyph)
    result = {"id": upload_id, "global": global_metrics, "glyphs": per_glyph}

    dest = OUTPUT_DIR / upload_id / "metrics.json"
    dest.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return result


@app.post("/compile/{upload_id}")
def compile_font_endpoint(upload_id: str) -> dict:
    glyphs_dir = OUTPUT_DIR / upload_id / "glyphs"
    if not glyphs_dir.exists():
        raise HTTPException(status_code=404, detail="Run /segment for this upload id first.")

    glyph_entries = {}
    for index, char in enumerate(char_grid()):
        glyph_path = glyphs_dir / f"{index:02d}_{char}.png"
        if not glyph_path.exists():
            continue

        with Image.open(glyph_path) as img:
            trace_path = trace_glyph(img)
            bbox = glyph_ink_bbox(img)
            bearings = side_bearings(img, bbox)
            glyph_entries[char] = {
                "path": trace_path,
                "crop_height": img.height,
                "advance_width": bearings["advance_width"],
            }

    font_builder = build_font(glyph_entries, units_per_em=1000, family_name="Hatekhori Kill-Test")
    dest = OUTPUT_DIR / upload_id / "font.otf"
    font_builder.save(str(dest))

    return {"id": upload_id, "font_path": str(dest), "glyph_count": len(glyph_entries)}


@app.get("/download-font/{upload_id}")
def download_font(upload_id: str) -> Response:
    font_path = OUTPUT_DIR / upload_id / "font.otf"
    if not font_path.exists():
        raise HTTPException(status_code=404, detail="Run /compile for this upload id first.")

    return Response(
        content=font_path.read_bytes(),
        media_type="font/otf",
        headers={"Content-Disposition": f'attachment; filename="hatekhori-{upload_id}.otf"'},
    )


# Mounted LAST and deliberately at "/" — Starlette matches the explicit
# API routes above first; this only catches whatever they don't. Serves
# frontend/index.html at "/" and everything else in frontend/ alongside
# it, so the browser and the API share one origin and never need CORS.
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
