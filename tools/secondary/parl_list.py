import requests, re, json, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36'}
base='https://www.parliament.go.ke/the-national-assembly/house-business/acts'
seen={}
def grab(params):
    r=requests.get(base,params=params,headers=UA,timeout=60)
    t=r.text
    i=t.find('views-exposed-form-the-national-assembly-business'); j=t.find('<!-- Sidebar Right',i)
    body=t[i:j]
    links=re.findall(r'href="([^"]+\.pdf)"[^>]*>(.*?)</a>',body,re.S|re.I)
    pages=re.findall(r'href="\?[^"]*page=(\d+)',body)
    return links,pages
for sess in ['All','2013','2017','2018','2019','2020','2021','2022']:
    p=0
    while True:
        links,pages=grab({'title':'','field_parliament_value':sess,'page':p})
        new=0
        for u,tt in links:
            if u not in seen: seen[u]={'title':re.sub(r'\s+',' ',re.sub('<[^>]+>','',tt)).strip(),'session':sess}; new+=1
        print(sess,p,len(links),new,len(seen),max(map(int,pages)) if pages else None,flush=True)
        time.sleep(1)
        if not pages or p>=max(map(int,pages)) or not links: break
        p+=1
json.dump(seen,open(r'C:\Users\alany\Documents\kenya-law-work\parl_acts.json','w'),indent=1)
