from pathlib import Path
import base64,gzip,json,re,copy

SRC=Path('admin-disposition-situational')
DST=Path('admin-contract-plan-guidance-petition'); DST.mkdir(parents=True,exist_ok=True)
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

# IMPORTANT: replace only static program/UI text, never the newly injected original questions.
# Split around the old question array first, so any legitimate「行政處分」inside historical questions is untouched.
prefix=html[:m.start(2)]
suffix=html[m.end(2):]
NEW_LABEL='行政契約・行政計畫・行政指導・陳情'

# The source template is the administrative-disposition quiz. Remove every residual static title/subtitle label.
prefix=prefix.replace('行政處分實境辨識強化',NEW_LABEL).replace('行政處分情境辨識強化',NEW_LABEL)
suffix=suffix.replace('行政處分實境辨識強化',NEW_LABEL).replace('行政處分情境辨識強化',NEW_LABEL)
prefix=prefix.replace('行政程序法｜行政處分',f'行政程序法｜{NEW_LABEL}')
suffix=suffix.replace('行政程序法｜行政處分',f'行政程序法｜{NEW_LABEL}')
# Catch any remaining standalone static occurrence from the mother template.
prefix=prefix.replace('行政處分',NEW_LABEL)
suffix=suffix.replace('行政處分',NEW_LABEL)

# Keep each quiz's persisted progress separate even though the program is reused exactly.
for oldkey in ['admin-disposition-situational','admin_disposition_situational','administrative-disposition','行政處分測驗']:
    prefix=prefix.replace(oldkey,'admin-contract-plan-guidance-petition')
    suffix=suffix.replace(oldkey,'admin-contract-plan-guidance-petition')

html=prefix+lit+suffix

# Audit the static UI outside the newly injected question array.
m2=re.search(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S)
if not m2: raise RuntimeError('rebuilt quiz array not found')
static_text=html[:m2.start(2)]+html[m2.end(2):]
static_admin_mentions=static_text.count('行政處分')
if static_admin_mentions:
    raise RuntimeError(f'static UI still contains 行政處分 x{static_admin_mentions}')

packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text()) for n in parts]; total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:p=packed[pos:]
    else:
        take=round(len(packed)*sz/total);p=packed[pos:pos+take];pos+=take
    out.append(p)
for n,p in zip(parts,out):(DST/n).write_text(p,encoding='utf-8')

loader='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政程序法｜行政契約・行政計畫・行政指導・陳情｜100題歷屆原題</title><script>(async()=>{const names=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt'];const a=(await Promise.all(names.map(n=>fetch(n).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={
    'template':'admin-disposition-situational','question_count':100,'program_reused':True,
    'source_position':'above_question','source_in_explanation':False,'stale_source_urls_removed':True,
    'static_admin_disposition_mentions':static_admin_mentions,'storage_isolated':True,
    'visible_label':NEW_LABEL,
    'parts':{n:len(p) for n,p in zip(parts,out)}
}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
