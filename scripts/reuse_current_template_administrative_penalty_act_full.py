from pathlib import Path
import base64,gzip,json,re,copy

SRC=Path('admin-procedure-1-19-round2')
DST=Path('administrative-penalty-act-full'); DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
b64=''.join((SRC/n).read_text(encoding='utf-8') for n in parts)
html=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
newq=json.loads((DST/'questions.json').read_text(encoding='utf-8')); assert len(newq)==100

m=re.search(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S)
if not m:
    for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and 'opts' in a[0]:
            m=mm; break
if not m: raise RuntimeError('quiz array not found')
old=json.loads(m.group(2)); converted=[]
for i,nq in enumerate(newq):
    b=copy.deepcopy(old[i])
    b['q']=nq['question']; b['opts']=nq['options']; b['ans']='ABCD'.index(nq['answer'])
    b['topic']=nq['topic']; b['basis']=nq['basis']; b['explanation']=nq['explanation']; b['source']=nq['source']
    if 'url' in b:b['url']=''
    converted.append(b)
lit=json.dumps(converted,ensure_ascii=False,separators=(',',':'))
prefix=html[:m.start(2)]; suffix=html[m.end(2):]

# Change only static UI text, never the newly injected original questions.
for oldlabel in ['行政程序法｜第1～19條・第二回','行政程序法｜第1～19條','行政程序法第1～19條','第1～19條・第二回']:
    prefix=prefix.replace(oldlabel,'行政罰法｜全法')
    suffix=suffix.replace(oldlabel,'行政罰法｜全法')
prefix=prefix.replace('行政程序法','行政罰法')
suffix=suffix.replace('行政程序法','行政罰法')

# Namespace all literal localStorage keys so this quiz has independent progress.
static=prefix+'\n'+suffix
keys=[]
for mm in re.finditer(r'localStorage\.(?:getItem|setItem|removeItem)\(\s*([\'\"])(.*?)\1',static):
    k=mm.group(2)
    if k and k not in keys: keys.append(k)
for k in keys:
    nk=k+'::administrative-penalty-act-full'
    prefix=prefix.replace("'"+k+"'","'"+nk+"'").replace('"'+k+'"','"'+nk+'"')
    suffix=suffix.replace("'"+k+"'","'"+nk+"'").replace('"'+k+'"','"'+nk+'"')
html=prefix+lit+suffix

# Verify final question array exactly matches new bank.
m2=re.search(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S)
if not m2:
    for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and 'opts' in a[0]:m2=mm;break
if not m2: raise RuntimeError('final quiz array not found')
qa=json.loads(m2.group(2))
assert qa[0]['q']==newq[0]['question'] and qa[-1]['q']==newq[-1]['question']

packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text(encoding='utf-8')) for n in parts]; total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:p=packed[pos:]
    else:
        take=round(len(packed)*sz/total); p=packed[pos:pos+take]; pos+=take
    out.append(p)
for n,p in zip(parts,out):(DST/n).write_text(p,encoding='utf-8')

# Re-open exact browser payload to prevent mother-template/cached-bank mistakes.
check=gzip.decompress(base64.b64decode(''.join(out))).decode('utf-8')
mc=re.search(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',check,re.S)
if not mc:
    for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',check,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and 'opts' in a[0]:mc=mm;break
if not mc:raise RuntimeError('cannot verify final bundle')
finalq=json.loads(mc.group(2)); assert finalq[0]['q']==newq[0]['question']

REV='20260907-administrative-penalty-act-full-v1'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政罰法｜全法｜100題歷屆原題</title><script>(async()=>{{const v='{REV}';const names={json.dumps(parts)};const a=(await Promise.all(names.map(n=>fetch(n+'?v='+v,{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={
 'template':'admin-procedure-1-19-round2','question_count':100,'program_reused':True,
 'new_path':'administrative-penalty-act-full','source_position':'above_question','source_in_explanation':False,
 'storage_namespaced':True,'storage_literal_keys_found':keys,'cache_busted':True,'revision':REV,
 'final_bundle_first_question':finalq[0]['q'],'final_bundle_first_topic':finalq[0].get('topic'),
 'parts':{n:len(p) for n,p in zip(parts,out)}
}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
