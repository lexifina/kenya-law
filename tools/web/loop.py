"""Build + push loop (detached, idle priority): every ~12 min run web_build.py, push main fast-forward, verify with
ls-remote. Keeps web_fetch.py and prewarm.py running. Deadline 2026-11-27 13:33 local: final build, docs commit
(docs_web.py), push, stop everything. Also stops on the STOP file."""
import datetime as dt, os, subprocess, sys, time
from pathlib import Path
W = Path(r'kenya-law-work')
T = W / 'tools'
NOWIN = 0x08000000 | 0x00000040          # CREATE_NO_WINDOW | IDLE_PRIORITY_CLASS
DEADLINE = dt.datetime(2026, 11, 27, 13, 33)


def log(m):
    with open(W / 'progress.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%H:%M:%S ') + 'loop: ' + m + '\n')


def run(a, t=3600):
    r = subprocess.run(a, capture_output=True, text=True, encoding='utf-8', errors='replace',
                       creationflags=NOWIN, timeout=t)
    return r.returncode, (r.stdout + r.stderr).strip()


def git(*a, t=900):
    return run(['git', '-C', str(W / 'repo'), *a], t=t)


def build_push():
    rc, out = run([sys.executable, '-X', 'utf8', '-I', str(T / 'web_build.py')])
    log(f'build rc={rc} {out[-300:]}')
    for a in range(4):
        rc, out = git('push', 'origin', 'main')
        if rc == 0:
            break
        log(f'push retry {a}: {out[-200:]}')
        time.sleep(30)
    loc = git('rev-parse', 'main')[1]
    rem = git('ls-remote', 'origin', 'refs/heads/main', t=300)[1].split()[:1]
    log(f'pushed={rem == [loc]} main={loc[:8]} commits={git("rev-list", "--count", "main")[1]}')


def spawn(name):
    return subprocess.Popen([sys.executable, '-I', str(T / name)], creationflags=NOWIN,
                            stdout=open(W / (name + '.out'), 'a'), stderr=subprocess.STDOUT)


fetch = prewarm = None
while not (W / 'STOP').exists() and dt.datetime.now() < DEADLINE:
    if fetch is None or fetch.poll() is not None:
        fetch = spawn('web_fetch.py')
    if prewarm is None or prewarm.poll() is not None:
        prewarm = spawn('prewarm.py')
    build_push()
    for _ in range(72):
        if (W / 'STOP').exists() or dt.datetime.now() >= DEADLINE:
            break
        time.sleep(10)
for p in (fetch, prewarm):
    if p and p.poll() is None:
        p.terminate()
build_push()
rc, out = run([sys.executable, '-X', 'utf8', '-I', str(T / 'docs_web.py')])
log(f'docs rc={rc} {out[-200:]}')
git('add', 'README.md', 'LICENSE', 'REPRODUCE.md', 'tools')
env = dict(os.environ, GIT_AUTHOR_NAME='Lexifina', GIT_AUTHOR_EMAIL='kenya-law@lexifina.com',
           GIT_COMMITTER_NAME='Lexifina', GIT_COMMITTER_EMAIL='kenya-law@lexifina.com')
r = subprocess.run(['git', '-C', str(W / 'repo'), 'commit', '-q', '-m',
                    'Documentation: README, REPRODUCE.md and LICENSE for the official website copies '
                    '(county, ministry, regulator, Parliament and EALA sites); tools/web'],
                   env=env, capture_output=True, text=True, creationflags=NOWIN)
log(f'docs commit rc={r.returncode}')
for a in range(4):
    if git('push', 'origin', 'main')[0] == 0:
        break
    time.sleep(30)
loc = git('rev-parse', 'main')[1]
rem = git('ls-remote', 'origin', 'refs/heads/main', t=300)[1].split()[:1]
log(f'FINAL pushed={rem == [loc]} main={loc[:8]} commits={git("rev-list", "--count", "main")[1]}')
(W / 'STOP').write_text('deadline reached')
log('stopped')
