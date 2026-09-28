from pathlib import Path
import re
from app.config import settings
def ensure_directories():
    for p in (Path(settings.static_dir)/'panels',Path(settings.static_dir)/'exports'): p.mkdir(parents=True,exist_ok=True)
def safe_filename(v): return re.sub(r'[^A-Za-z0-9._-]+','_',Path(v).name)[:150] or 'comic.pdf'
