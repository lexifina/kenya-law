"""Parse every cached web PDF into cache/webparse/<sha>.pkl, each in its own process (a MuPDF crash or a
3-minute hang marks that PDF unreadable instead of killing the build). 4 at a time. Loops until STOP."""
import hashlib, pickle, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
W = Path(r'kenya-law-work')
T = W / 'tools'
NOWIN = 0x08000000 | 0x00004000
OUT = W / 'cache' / 'webparse'
OUT.mkdir(exist_ok=True)


def one(p):
    b = p.read_bytes()
    q = OUT / (hashlib.sha256(b).hexdigest() + '.pkl')
    if q.exists():
        return
    try:
        r = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(T / 'parse_one.py'), str(p), str(q)],
                           creationflags=NOWIN, timeout=180, capture_output=True)
        ok = r.returncode == 0 and q.exists()
    except subprocess.TimeoutExpired:
        ok = False
    if not ok:
        q.write_bytes(pickle.dumps(({'ok': False, 'why': 'unreadable PDF (reader crashed or hung)'}, '')))


while not (W / 'STOP').exists():
    ps = sorted((W / 'cache' / 'web').glob('*.pdf'), key=lambda p: p.stat().st_size)
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(one, ps))
    time.sleep(60)
