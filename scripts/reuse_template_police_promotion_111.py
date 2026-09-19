from pathlib import Path
import base64,gzip,json,copy,re

SRC=Path('criminal-illegality-50')
DST=Path('police-promotion-111-sergeant-to-inspector')
DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
html=gzip.decompress(base64.b64decode(''.join((SRC/n).read_text(encoding='utf-8') for n in parts))).decode('utf-8')
newq=json.loads((DST/'questions.json').read_text(encoding='utf-8'))
assert len(newq)==158

dec=json.JSONDecoder(); old=None; arr_start=arr_end=None
for i,ch in enumerate(html):
    if ch!='[': continue
    try:a,end=dec.raw_decode(html[i:])
    except Exception: continue
    if isinstance(a,list) and a and isinstance(a[0],dict):
        keys=set(a[0])
        if ('opts' in keys or 'options' in keys) and ('q' in keys or 'question' in keys):
            old=a; arr_start=i; arr_end=i+end; break
if old is None: raise RuntimeError('fixed quiz question array not found')

proto=old[0]
converted=[]
for i,nq in enumerate(newq):
    b=copy.deepcopy(old[i] if i < len(old) else proto)
    if 'q' in b:b['q']=nq['question']
    else:b['question']=nq['question']
    if 'opts' in b:b['opts']=nq['options']
    else:b['options']=nq['options']
    ans='ABCD'.index(nq['answer'])
    if 'ans' in b:b['ans']=ans
    elif 'answer' in b:b['answer']=ans
    else:b['ans']=ans
    b['topic']=nq['topic']; b['basis']=nq['basis']; b['explanation']=nq['explanation']; b['source']=nq['source']
    if 'url' in b:b['url']=''
    converted.append(b)

lit=json.dumps(converted,ensure_ascii=False,separators=(',',':'))
prefix=html[:arr_start]; suffix=html[arr_end:]

for oldlabel in ['刑法總則｜違法性','刑法總則 違法性','違法性｜50題歷屆原題']:
    prefix=prefix.replace(oldlabel,'111警察升官等｜警佐升警正')
    suffix=suffix.replace(oldlabel,'111警察升官等｜警佐升警正')
for oldcount,newcount in [('50 題','158 題'),('50題','158題'),('第 1 / 50 題','第 1 / 158 題')]:
    prefix=prefix.replace(oldcount,newcount); suffix=suffix.replace(oldcount,newcount)

# Independent progress key; no behavior change.
ns='police-promotion-111-sergeant-to-inspector'
def namespace_storage(text):
    for m in list(re.finditer(r"localStorage\.(?:getItem|setItem|removeItem)\(\s*(['\"])([^'\"]+)\1",text)):
        key=m.group(2)
        if ns not in key:
            text=text.replace("'"+key+"'","'"+key+'::'+ns+"'").replace('"'+key+'"','"'+key+'::'+ns+'"')
    vars_used=set(re.findall(r'localStorage\.(?:getItem|setItem|removeItem)\(\s*([A-Za-z_$][\w$]*)',text))
    for v in vars_used:
        pat=re.compile(r'((?:const|let|var)\s+'+re.escape(v)+r'\s*=\s*)([\'\"])(.*?)(\2)')
        m=pat.search(text)
        if m and ns not in m.group(3):
            text=text[:m.start(3)]+m.group(3)+'::'+ns+text[m.end(3):]
    return text
prefix=namespace_storage(prefix); suffix=namespace_storage(suffix)
html=prefix+lit+suffix

sp=html.find('id="qSource"'); qp=html.find('id="qTitle"')
if sp<0 or qp<0 or sp>qp: raise RuntimeError('source is not above question')
if 'feedbackSource' in html: raise RuntimeError('source duplicated in feedback')

packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text(encoding='utf-8')) for n in parts]; total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:p=packed[pos:]
    else:
        take=round(len(packed)*sz/total); p=packed[pos:pos+take]; pos+=take
    out.append(p)
for n,p in zip(parts,out):(DST/n).write_text(p,encoding='utf-8')

browser_html=gzip.decompress(base64.b64decode(''.join(out))).decode('utf-8')
assert newq[0]['question'] in browser_html and newq[-1]['question'] in browser_html
assert browser_html.find('id="qSource"') < browser_html.find('id="qTitle"')

REV='20260919-police-promotion-111-v1'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>111警察升官等｜警佐升警正｜158題原題</title><script>(async()=>{{const v='{REV}';const names={json.dumps(parts)};const a=(await Promise.all(names.map(n=>fetch(n+'?v='+v,{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={'template':'criminal-illegality-50','question_count':158,'program_reused':True,'new_path':'police-promotion-111-sergeant-to-inspector','source_position':'above_question','source_in_explanation':False,'storage_namespaced':True,'cache_busted':True,'revision':REV}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
