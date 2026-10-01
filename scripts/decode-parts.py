from pathlib import Path
import base64
for first in Path('assets').rglob('*.b64.part00'):
    stem = str(first)[:-7]
    parts = sorted(first.parent.glob(first.name[:-2]+'*'))
    Path(stem[:-4]).write_bytes(base64.b64decode(''.join(p.read_text() for p in parts)))
