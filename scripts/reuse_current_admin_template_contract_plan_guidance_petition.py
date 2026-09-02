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

# Replace only static mother-template text. Historical question text is inserted afterwards untouched.
prefix=html[:m.start(2)]
suffix=html[m.end(2):]
NEW_LABEL='行政契約・行政計畫・行政指導・陳情'
for block_name in ('prefix','suffix'):
    block=locals()[block_name]
    block=block.replace('行政處分實境辨識強化',NEW_LABEL).replace('行政處分情境辨識強化',NEW_LABEL)
    block=block.replace('行政程序法｜行政處分',f'行政程序法｜{NEW_LABEL}')
    block=block.replace('行政處分',NEW_LABEL)
    locals()[block_name]=block

html=prefix+lit+suffix

# IMPORTANT: the mother program used the same storage keys. Namespace every localStorage access so
# this quiz can never restore the administrative-disposition quiz's question order/answers/progress.
NS="admin-contract-plan-guidance-petition::"
html=html.replace('localStorage.getItem(',f"localStorage.getItem('{NS}'+")
html=html.replace('localStorage.setItem(',f"localStorage.setItem('{NS}'+")
html=html.replace('localStorage.removeItem(',f"localStorage.removeItem('{NS}'+")

# Audit rebuilt in-memory program before packing.
m2=re.search(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S)
if not m2:
    for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and 'opts' in a[0]:m2=mm;break
if not m2: raise RuntimeError('rebuilt quiz array not found')
rebuilt=json.loads(m2.group(2))
assert rebuilt[0]['q']==newq[0]['question']
assert rebuilt[0]['topic']=='行政契約'
assert sum(1 for x in rebuilt if x.get('topic')=='行政處分／事實行為辨識')==0
static_text=html[:m2.start(2)]+html[m2.end(2):]
static_admin_mentions=static_text.count('行政處分')
if static_admin_mentions: raise RuntimeError(f'static UI still contains 行政處分 x{static_admin_mentions}')

packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text()) for n in parts]; total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:p=packed[pos:]
    else:
        take=round(len(packed)*sz/total);p=packed[pos:pos+take];pos+=take
    out.append(p)
for n,p in zip(parts,out):(DST/n).write_text(p,encoding='utf-8')

# Verify the ACTUAL final p1-p6 bundle, not only questions.json / pre-pack HTML.
final_html=gzip.decompress(base64.b64decode(''.join(out))).decode('utf-8')
fm=re.search(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',final_html,re.S)
if not fm:
    for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',final_html,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and 'opts' in a[0]:fm=mm;break
if not fm: raise RuntimeError('final packed quiz array not found')
final_q=json.loads(fm.group(2))
assert final_q[0]['q']==newq[0]['question']
assert final_q[0]['topic']=='行政契約'
assert NS in final_html

# Cache-bust fixed p1-p6 filenames. Program inside the bundle is unchanged; only loader fetch policy changes.
REV='20260903-contract-plan-guidance-petition-v3'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政程序法｜行政契約・行政計畫・行政指導・陳情｜100題歷屆原題</title><script>(async()=>{{const names=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt'];const a=(await Promise.all(names.map(n=>fetch(n+'?rev={REV}',{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={
    'template':'admin-disposition-situational','question_count':100,'program_reused':True,
    'source_position':'above_question','source_in_explanation':False,'stale_source_urls_removed':True,
    'static_admin_disposition_mentions':static_admin_mentions,'storage_namespaced':True,
    'cache_busted':True,'revision':REV,'visible_label':NEW_LABEL,
    'final_bundle_first_question':final_q[0]['q'],'final_bundle_first_topic':final_q[0]['topic'],
    'parts':{n:len(p) for n,p in zip(parts,out)}
}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
