import asyncio
from contextlib import asynccontextmanager
import io
import sys
import threading
import time
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from pipeline.cleanup import (
    OUTPUT_DIR,
    OUTPUT_MAX_AGE_S,
    OUTPUT_MAX_BYTES,
    OUTPUT_MAX_FILES,
    UPLOAD_MAX_AGE_S,
    UPLOAD_MAX_BYTES,
    UPLOAD_MAX_FILES,
    sweep,
)
from pipeline.ingest import (
    MAX_FILE_SIZE_BYTES,
    UPLOAD_DIR,
    UnsupportedFileType,
    UploadTooLarge,
    save_upload,
    upload_path,
)
from pipeline.run import make_font
from pipeline.sheet import generate_guideline_sheet
from pipeline.validate import BadSheetShape

SWEEP_INTERVAL_SECONDS = 3600  # once an hour
_GENERATE_SEMAPHORE = threading.BoundedSemaphore(2)  # Cap concurrent font compilations to protect CPU/RAM
_CACHED_SHEETS: dict[str, bytes] = {}


class SimpleRateLimiter:
    """Thread-safe sliding-window rate limiter per client IP (PRD §6a)."""

    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            timestamps = self.requests.get(client_ip, [])
            timestamps = [t for t in timestamps if t > cutoff]
            if len(timestamps) >= self.max_requests:
                self.requests[client_ip] = timestamps
                return False
            timestamps.append(now)
            self.requests[client_ip] = timestamps
            return True

    def sweep(self) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            self.requests = {
                ip: [t for t in ts if t > cutoff]
                for ip, ts in self.requests.items()
                if any(t > cutoff for t in ts)
            }


_INGEST_LIMITER = SimpleRateLimiter(max_requests=15, window_seconds=60)
_GENERATE_LIMITER = SimpleRateLimiter(max_requests=6, window_seconds=60)


def get_client_ip(request: Request) -> str:
    """Extract real client IP behind reverse proxies (Cloudflare, Caddy, Nginx)."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()
    return request.client.host if request.client else "127.0.0.1"


def _get_guideline_sheet_bytes(script: str = "bn") -> bytes:
    s = "en" if script.lower() == "en" else "bn"
    if s not in _CACHED_SHEETS:
        img = generate_guideline_sheet(script=s)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        _CACHED_SHEETS[s] = buf.getvalue()
    return _CACHED_SHEETS[s]


def _run_sweep() -> None:
    sweep(UPLOAD_DIR, UPLOAD_MAX_AGE_S, UPLOAD_MAX_FILES, UPLOAD_MAX_BYTES)
    sweep(OUTPUT_DIR, OUTPUT_MAX_AGE_S, OUTPUT_MAX_FILES, OUTPUT_MAX_BYTES)
    _INGEST_LIMITER.sweep()
    _GENERATE_LIMITER.sweep()


async def _periodic_sweep() -> None:
    while True:
        await asyncio.sleep(SWEEP_INTERVAL_SECONDS)
        try:
            _run_sweep()
        except Exception:
            pass  # best-effort: a failed sweep must never take the app down


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Immediate sweep on startup so stale temp files from prior server runs don't linger
    try:
        _run_sweep()
    except Exception:
        pass
    sweep_task = asyncio.create_task(_periodic_sweep())
    try:
        yield
    finally:
        sweep_task.cancel()
        try:
            await sweep_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Hatekhori", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Enforce defense-in-depth HTTP headers against XSS, sniffing, and clickjacking."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: blob:; "
        "font-src 'self' data: blob: https://fonts.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "script-src 'self'; "
        "frame-ancestors 'none';"
    )
    path = request.url.path
    if path.endswith((".css", ".js", ".html")) or path == "/":
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/privacy")
def privacy_policy() -> dict:
    """Structured legal and privacy terms for Hatekhori (PRD §6b, docs/privacy-policy.md)."""
    return {
        "product": "Hatekhori (হাতে খড়ি)",
        "model_training": "Zero. We never use your handwriting to train AI models — ours or anyone else's.",
        "identity": "No accounts, no cookies, no tracking. Capture and preview sessions are anonymous.",
        "retention": {
            "raw_uploaded_photo": "Deleted immediately on successful font generation; purged within 24h on error.",
            "generated_font": "Kept for 30 days for re-download via direct link, then permanently purged.",
            "rejected_upload_hashes": "SHA-256 hash only (never raw photos) kept up to 90 days for abuse detection.",
        },
        "legal_warranty": "Submitting users certify they own or have permission to convert their handwriting. Signature forgery is strictly prohibited.",
        "abuse_and_takedown_contact": "privacy@hatekhori.org",
    }


@app.get("/guideline-sheet.png")
def guideline_sheet(script: str = "bn") -> Response:
    content = _get_guideline_sheet_bytes(script)
    filename = f"hatekhori-{'english' if script == 'en' else 'bengali'}-sheet.png"
    return Response(
        content=content,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


@app.get("/guideline-sheet-bengali.png")
def guideline_sheet_bengali() -> Response:
    return Response(
        content=_get_guideline_sheet_bytes("bn"),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": 'attachment; filename="hatekhori-bengali-sheet.png"',
        },
    )


@app.get("/guideline-sheet-english.png")
def guideline_sheet_english() -> Response:
    return Response(
        content=_get_guideline_sheet_bytes("en"),
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": 'attachment; filename="hatekhori-english-sheet.png"',
        },
    )


@app.post("/ingest")
async def ingest(request: Request, file: UploadFile = File(...)) -> dict:
    client_ip = get_client_ip(request)
    if not _INGEST_LIMITER.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many upload attempts from this address. Please wait a minute before retrying.",
        )

    # Chunked read to prevent unbounded in-memory buffer exhaustion (PRD §6a DoS defense)
    chunk_size = 64 * 1024
    total_bytes = 0
    chunks = []
    while chunk := await file.read(chunk_size):
        total_bytes += len(chunk)
        if total_bytes > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"That file is larger than the {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB limit.",
            )
        chunks.append(chunk)

    try:
        return {"id": save_upload(b"".join(chunks))}
    except (UnsupportedFileType, UploadTooLarge) as e:
        raise HTTPException(status_code=400, detail=str(e))


def _font_path(upload_id: UUID, ext: str = "otf") -> Path:
    return OUTPUT_DIR / f"{upload_id}.{ext}"


@app.post("/generate/{upload_id}")
def generate(
    upload_id: UUID,
    request: Request,
    script: str = "bn",
    consent: bool = True,
) -> dict:
    if not consent:
        raise HTTPException(
            status_code=400,
            detail="Legal consent required: you must confirm you have the right to submit this handwriting.",
        )

    client_ip = get_client_ip(request)
    if not _GENERATE_LIMITER.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Font compilation rate limit reached. Please wait a moment before trying again.",
        )

    photo = upload_path(upload_id)
    if not photo.exists():
        raise HTTPException(status_code=404, detail="No upload found with that id.")
    if not _GENERATE_SEMAPHORE.acquire(blocking=True, timeout=30.0):
        raise HTTPException(
            status_code=503,
            detail="Server is currently busy generating fonts. Please retry shortly.",
        )
    try:
        return make_font(photo, _font_path(upload_id), script=script)
    except BadSheetShape as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        _GENERATE_SEMAPHORE.release()
        try:
            photo.unlink(missing_ok=True)  # the raw photo is never kept past its one use (AGENTS.md §7)
        except OSError:
            pass


@app.get("/download-font/{upload_id}")
def download_font(upload_id: UUID, inline: bool = False, format: str = "otf") -> Response:
    ext = "ttf" if format.lower() == "ttf" else "otf"
    font_path = _font_path(upload_id, ext)
    if not font_path.exists():
        # Fallback to alternate font format if primary requested is missing
        alt_ext = "otf" if ext == "ttf" else "ttf"
        alt_path = _font_path(upload_id, alt_ext)
        if alt_path.exists():
            font_path = alt_path
            ext = alt_ext
        else:
            raise HTTPException(status_code=404, detail="No font for this id yet.")

    # inline=true is what the in-page live preview loads as a web font;
    # without it the browser is told to save the file instead.
    headers = {}
    if not inline:
        headers["Content-Disposition"] = f'attachment; filename="hatekhori-{upload_id}.{ext}"'

    media_type = f"font/{ext}"
    return FileResponse(font_path, media_type=media_type, headers=headers)


# Mounted LAST and deliberately at "/" — Starlette matches the explicit
# API routes above first; this only catches whatever they don't. Serves
# frontend/index.html at "/" and everything else in frontend/ alongside
# it, so the browser and the API share one origin and never need CORS.
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = Path.cwd() / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
