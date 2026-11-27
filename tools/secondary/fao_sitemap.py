import requests,re,json,time
UA={'User-Agent':'Mozilla/5.0'}
out=[]
for i in range(1,6):
    r=requests.get(f'https://faolex.fao.org/sitemaps/documents-{i}.xml',headers=UA,timeout=180)
    locs=re.findall(r'<loc>([^<]+)</loc>',r.text)
    k=[l for l in locs if re.search(r'-ken-(\d{4}|nd)?$',l) or l.endswith('-ken')]
    print(i,len(locs),len(k)); out+=k; time.sleep(1)
json.dump(out,open(r'kenya-law-work\faolex_ken.json','w'),indent=0)
