from pathlib import Path
import base64,gzip,json,re,copy
SRC=Path('admin-procedure-92-134')
DST=Path('criminal-law-life-body-100'); DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
b64=''.join((SRC/n).read_text(encoding='utf-8') for n in parts)
html=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
newq=json.loads((DST/'questions.json').read_text(encoding='utf-8')); assert len(newq)==100
m=re.search(r'((?:const|let|var)\\s+QUESTIONS\\s*=\\s*)(\\[.*?\\])(?=\\s*;)',html,re.S)
arr_start=arr_end=None; old=None
if m:
    try:
        cand=json.loads(m.group(2))
        if isinstance(cand,list) and len(cand)==100:
            old=cand; arr_start=m.start(2); arr_end=m.end(2)
    except Exception:
        pass
if old is None:
    for mm in re.finditer(r'((?:const|let|var)\\s+[A-Za-z_$][\\w$]*\\s*=\\s*)(\\[.*?\\])(?=\\s*;)',html,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and ('opts' in a[0] or 'options' in a[0]):
            old=a; arr_start=mm.start(2); arr_end=mm.end(2); break
if old is None:
    dec=json.JSONDecoder()
    for mm in re.finditer(r'\\[\\s*\\{',html):
        try:
            a,end=dec.raw_decode(html[mm.start():])
        except Exception:
            continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and ('opts' in a[0] or 'options' in a[0]):
            old=a; arr_start=mm.start(); arr_end=mm.start()+end; break
if old is None:
    vars_=re.findall(r'(?:const|let|var)\\s+([A-Za-z_$][\\w$]*)\\s*=',html)
    oi=html.find('"opts"'); qi=html.find('"q"')
    print('template diagnostics',{'length':len(html),'vars':vars_[:40],'opts_at':oi,'q_at':qi,'opts_context':html[max(0,oi-120):oi+180] if oi>=0 else ''})
    raise RuntimeError('quiz array not found')
converted=[]
for i,nq in enumerate(newq):
    b=copy.deepcopy(old[i])
    b['q']=nq['question']; b['opts']=nq['options']; b['ans']='ABCD'.index(nq['answer'])
    b['topic']=nq['topic']; b['basis']=nq['basis']; b['explanation']=nq['explanation']; b['source']=nq['source']
    if 'url' in b:b['url']=''
    converted.append(b)
lit=json.dumps(converted,ensure_ascii=False,separators=(',',':'))
prefix=html[:arr_start]; suffix=html[arr_end:]

# Static labels only; original-question text is injected after label replacement.
for old in ['行政程序法｜行政處分實境辨識強化','行政處分實境辨識強化','行政處分實境辨識']:
    prefix=prefix.replace(old,'刑法分則｜生命・身體法益')
    suffix=suffix.replace(old,'刑法分則｜生命・身體法益')
prefix=prefix.replace('行政程序法','刑法')
suffix=suffix.replace('行政程序法','刑法')

# Independent progress key, while leaving program behavior unchanged.
static=prefix+'\\n'+suffix
keys=[]
for mm in re.finditer(r'localStorage\\.(?:getItem|setItem|removeItem)\\(\\s*([\\\'\\"])(.*?)\\1',static):
    k=mm.group(2)
    if k and k not in keys:keys.append(k)
for k in keys:
    nk=k+'::criminal-law-life-body-100'
    prefix=prefix.replace("'"+k+"'","'"+nk+"'").replace('"'+k+'"','"'+nk+'"')
    suffix=suffix.replace("'"+k+"'","'"+nk+"'").replace('"'+k+'"','"'+nk+'"')
html=prefix+lit+suffix

# Keep source above question and do not repeat source inside feedback.
# The selected fixed template already has this behavior; verify it rather than redesigning.
sp=html.find('id="qSource"'); qp=html.find('id="qTitle"')
if sp<0 or qp<0 or sp>qp: raise RuntimeError('source is not above question in template')
if 'feedbackSource' in html: raise RuntimeError('template unexpectedly repeats source in feedback')

packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text(encoding='utf-8')) for n in parts]; total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:p=packed[pos:]
    else:
        take=round(len(packed)*sz/total);p=packed[pos:pos+take];pos+=take
    out.append(p)
for n,p in zip(parts,out):(DST/n).write_text(p,encoding='utf-8')

check=gzip.decompress(base64.b64decode(''.join(out))).decode('utf-8')
assert newq[0]['question'] in check and newq[-1]['question'] in check
REV='20260911-criminal-law-life-body-100-v1'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>刑法分則｜殺人・傷害・墮胎・遺棄・185-4｜100題歷屆原題</title><script>(async()=>{{const v='{REV}';const names={json.dumps(parts)};const a=(await Promise.all(names.map(n=>fetch(n+'?v='+v,{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={'template':'admin-procedure-92-134','question_count':100,'program_reused':True,'new_path':'criminal-law-life-body-100','source_position':'above_question','source_in_explanation':False,'storage_namespaced':True,'cache_busted':True,'revision':REV,'parts':{n:len(p) for n,p in zip(parts,out)}}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
