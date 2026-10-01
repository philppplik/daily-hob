from pathlib import Path
import base64
for p in Path('assets').rglob('*.b64'):
    p.with_suffix('').write_bytes(base64.b64decode(p.read_text()))
