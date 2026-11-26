import json,time,requests,urllib.parse
from pathlib import Path
W=Path(r'C:\Users\alany\Documents\kenya-law-work'); D=W/'cache'/'parl'; D.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
L=json.load(open(W/'parl_acts.json'))
for u,v in L.items():
    name=urllib.parse.unquote(u.rsplit('/',1)[1]); p=D/name
    if p.exists(): continue
    r=requests.get(u,headers=UA,timeout=180); time.sleep(1)
    print(r.status_code,len(r.content),name)
    if r.status_code==200 and r.content[:4]==b'%PDF': p.write_bytes(r.content)
