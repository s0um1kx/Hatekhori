"""In-memory session store for the QR + phone camera capture path.

A session links a desktop browser tab to a phone: the desktop creates
a session and shows its QR code; the phone scans it, uploads a photo
tagged with that session id; the desktop polls until the photo shows
up, then continues the normal pipeline with it.

In-memory only — sessions don't survive a server restart, which is
fine for a short-lived "scan now" flow. Not designed for multiple
concurrent users on a shared deployment yet (see AGENTS.md's
no-accounts stance — sessions are anonymous and short-lived by design,
not a place to add real user state later).
"""

import socket
import uuid

_sessions: dict[str, dict] = {}


def create_session() -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"status": "waiting", "upload_id": None}
    return session_id


def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def mark_received(session_id: str, upload_id: str) -> None:
    if session_id in _sessions:
        _sessions[session_id]["status"] = "received"
        _sessions[session_id]["upload_id"] = upload_id


def get_lan_ip() -> str:
    """Best-effort guess at this machine's LAN IP (not 127.0.0.1), so a
    QR code points somewhere a phone on the same WiFi can actually
    reach. Opens a UDP "connection" to an external address purely to
    see which local interface the OS would route through — no packets
    are actually sent to that address.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()
