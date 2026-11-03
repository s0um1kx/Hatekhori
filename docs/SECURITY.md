# Security & Privacy Policy — Hatekhori (হাতে খড়ি)

This document outlines the security architecture, threat model, privacy safeguards, and vulnerability reporting procedures for Hatekhori.

---

## 1. Vulnerability Reporting & Disclosure

We take the security and privacy of Hatekhori and its users seriously. If you identify a security vulnerability, we ask that you practice responsible disclosure.

- **Security & Privacy Contact:** `privacy@hatekhori.org` (or `security@hatekhori.org`)
- **Initial Response Time:** Within 48 hours of receipt.
- **Remediation SLA:** Critical vulnerabilities are patched within 7 business days.
- **Policy:** Please do not publicly disclose vulnerabilities before a fix has been committed and verified. We do not pursue legal action against security researchers acting in good faith.

---

## 2. Threat Model & Implemented Guardrails

Hatekhori operates without user accounts or persistent identity. Because of this architecture, security protections are enforced at the transport, ingest, pipeline, and storage levels.

### A. Denial of Service (DoS) & Memory Exhaustion
- **Attack Vector:** An attacker sends a continuous multi-gigabyte upload stream to exhaust server RAM and trigger an Out-Of-Memory (OOM) crash.
- **Implemented Mitigation:**
  - In `backend/app/main.py`, uploads are consumed as chunked streams (64KB chunks).
  - An absolute ceiling of 15MB (`MAX_FILE_SIZE_BYTES`) is enforced. If an incoming stream exceeds 15MB, the server terminates reading immediately and returns `HTTP 413 Payload Too Large`.
  - Unbounded `await file.read()` calls are strictly forbidden.

### B. Decompression Bombs (Zip / Pixel Bombs)
- **Attack Vector:** A small file (e.g. 500KB PNG) whose header specifies a dimension like 100,000 × 100,000 pixels, which expands into dozens of gigabytes of RAM upon decompression.
- **Implemented Mitigation:**
  - `Image.MAX_IMAGE_PIXELS = 36_000_000` is set in `backend/pipeline/ingest.py`. Pillow aborts during header inspection and raises `Image.DecompressionBombError` before raster memory allocation.
  - Hard cap of `MAX_PIXEL_DIMENSION = 6000` per side is verified on opened image headers.

### C. Resource Starvation & CPU Flooding
- **Attack Vector:** Scripted botnets flooding the CPU-intensive Potrace vectorization and TrueType/OpenType compilation engine.
- **Implemented Mitigation:**
  - **Sliding-Window Rate Limiting:** In-memory rate limiting per IP address:
    - `/ingest`: max 15 requests per 60-second window.
    - `/generate`: max 6 requests per 60-second window.
    - Exceeding requests receive `HTTP 429 Too Many Requests`.
  - **Reverse Proxy IP Resolution:** `get_client_ip()` correctly parses `CF-Connecting-IP`, `X-Forwarded-For`, and `X-Real-IP` behind Cloudflare, Nginx, or Caddy.
  - **Concurrency Throttling:** `_GENERATE_SEMAPHORE = threading.BoundedSemaphore(2)` restricts concurrent font generation to 2 parallel worker threads, queuing or rejecting (`HTTP 503`) excess compilations to preserve host responsiveness.

### D. Path Traversal & Injection
- **Attack Vector:** An attacker supplies `../../` or wildcard paths in request parameters to access or delete arbitrary filesystem files.
- **Implemented Mitigation:**
  - Route parameters such as `{upload_id}` in `/generate/{upload_id}` and `/download-font/{upload_id}` are strictly typed as standard library `uuid.UUID`. Non-UUID inputs fail with `HTTP 422 Unprocessable Entity` at the routing layer.
  - Font file downloads restrict the `format` parameter strictly to `"otf"` or `"ttf"`. No arbitrary extensions or path elements can be requested.

### E. Malicious Uploads & CSAM / Offensive Content
- **Attack Vector:** Uploading arbitrary files, malware, or offensive imagery disguised as handwriting.
- **Implemented Mitigation:**
  - **Content Sniffing:** Pillow inspects magic bytes; files must decode as real JPEG, PNG, or MPO.
  - **Structural Guideline Validation (`validate.py`):** The pipeline requires 4 black square fiducial markers at the page corners and minimum ink density across cell regions. Arbitrary images and junk photos fail registration and are rejected before vectorization.
  - **Abuse Hash Logging:** Rejected uploads are hashed (SHA-256) and recorded into `rejected_hashes.log` to track repeated abuse patterns without storing malicious or illegal images.

### F. Privacy Leakage & EXIF GPS Scrubbing
- **Attack Vector:** Phone camera captures containing embedded GPS coordinates, timestamps, and device serial numbers.
- **Implemented Mitigation:**
  - Orientation is normalized via `ImageOps.exif_transpose()`.
  - Only clean raw pixel data is re-saved to disk. EXIF, IPTC, and XMP metadata dictionaries are completely stripped on ingest.

### G. Browser Security Headers
- All HTTP responses include defense-in-depth headers:
  - `X-Content-Type-Options: nosniff` — Prevents MIME-type confusion attacks.
  - `X-Frame-Options: DENY` — Prevents clickjacking and unauthorized iframe framing.
  - `Referrer-Policy: strict-origin-when-cross-origin` — Protects referer leakage.
  - `Content-Security-Policy` — Restricts script, font, and style execution sources.
  - `Permissions-Policy: camera=(), microphone=(), geolocation=()` — Disables browser sensor access.

---

## 3. Data Lifecycle & Retention Contract

| Data Category | Retention Limit | Storage Location | Purge Method |
| :--- | :--- | :--- | :--- |
| **Raw Uploaded Photo** | Single processing run | `uploads/{uuid}.img` | Unlinked immediately upon font compilation (max 24h on error). |
| **Compiled Font (.otf/.ttf)** | 30 days | `output/{uuid}.otf` | Auto-purged by hourly background sweep task. |
| **Abuse Tracking Hashes** | 90 days | `output/rejected_hashes.log` | SHA-256 hashes only. No image data retained. |
| **Session Analytics** | Indefinite | Memory / Aggregated | Strictly anonymized count metrics. |

---

## 4. Legal Provenance & Signature Forgery Policy

1. **User Certification:** Users must check the legal consent checkbox prior to font compilation, certifying that the handwriting is their own or that they hold express legal authority to digitize it.
2. **Prohibited Use:** Using Hatekhori to digitize forged signatures, execute financial fraud, or copy proprietary font software is strictly prohibited.
3. **Expedited Takedown:** Anyone who believes their handwriting or signature has been converted without consent may contact `privacy@hatekhori.org` for immediate removal.

---

## 5. Production Deployment Hardening Checklist

When deploying Hatekhori in a production environment:

- [ ] **HTTPS / TLS Termination:** Serve only over HTTPS with HTTP/2 or HTTP/3 enabled via a reverse proxy (e.g., Caddy, Nginx, or Cloudflare).
- [ ] **Real IP Forwarding:** Ensure the reverse proxy passes `X-Forwarded-For` or `CF-Connecting-IP` so the built-in rate limiter identifies individual clients.
- [ ] **Data Directory Isolation:** Set `HATEKHORI_DATA_DIR` to a dedicated volume or directory outside the application source tree with restrictive permissions (`chmod 700`).
- [ ] **Least Privilege:** Run the backend service under an unprivileged user (e.g., `hatekhori:hatekhori`), never as `root` or `Administrator`.
- [ ] **Storage Sweeps:** Keep the automated lifespan sweep enabled or run a daily cron executing `pipeline.cleanup.sweep()`.
