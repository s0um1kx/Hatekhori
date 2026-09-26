"""Hatekhori backend — FastAPI entrypoint.

Milestone 1 scope only: this file exists so the service boots and has a
health check. Ingest/preprocess/segment/vectorize/metrics/compile routes
are added in later parts, not here.
"""

from fastapi import FastAPI

app = FastAPI(title="Hatekhori", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
