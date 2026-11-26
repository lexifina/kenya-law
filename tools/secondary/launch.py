import subprocess, sys
p = subprocess.Popen([sys.executable, '-I', sys.argv[1]], creationflags=0x08000000 | 0x00004000 | 0x00000200,
                     stdout=open(sys.argv[2], 'a'), stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, close_fds=True)
open(sys.argv[2] + '.pid', 'w').write(str(p.pid)); print(p.pid)
