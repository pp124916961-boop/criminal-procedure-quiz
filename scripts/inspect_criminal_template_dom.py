from pathlib import Path
import base64,gzip,re,json
SRC=Path('criminal-general-attempt')
names=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
b64=''.join((SRC/n).read_text(encoding='utf-8') for n in names)
html=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
needles=['source','來源','出處','question','qText','qtext','stem','renderQuestion','render']
out=[]
for needle in needles:
    for m in re.finditer(re.escape(needle),html,re.I):
        s=max(0,m.start()-350); e=min(len(html),m.end()+550)
        sn=html[s:e].replace('\n',' ')
        out.append({'needle':needle,'snippet':sn})
        if sum(1 for x in out if x['needle']==needle)>=8: break
Path('admin-procedure-54-91-102-109/template-dom-diagnostics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('diagnostics',len(out))
