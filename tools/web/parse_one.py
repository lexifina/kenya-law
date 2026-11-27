import pickle, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pdfread  # noqa: E402
import pymupdf  # noqa: E402

b = Path(sys.argv[1]).read_bytes()
r = pdfread.read(b)
raw = ''
if r.get('ok'):
    doc = pymupdf.open(stream=b, filetype='pdf')
    raw = re.sub(r'\s+', ' ', ' '.join(pg.get_text() for pg in list(doc)[:5]))
q = Path(sys.argv[2])
tmp = q.with_suffix('.tmp')
tmp.write_bytes(pickle.dumps((r, raw)))
tmp.replace(q)
