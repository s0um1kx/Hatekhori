"""python -m app.cli photo.jpg  ->  output/<id>.otf"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.cleanup import OUTPUT_DIR
from pipeline.ingest import save_upload, upload_path
from pipeline.run import make_font

upload_id = save_upload(Path(sys.argv[1]).read_bytes())
try:
    make_font(upload_path(upload_id), OUTPUT_DIR / f"{upload_id}.otf")
finally:
    upload_path(upload_id).unlink(missing_ok=True)
print(OUTPUT_DIR / f"{upload_id}.otf")
