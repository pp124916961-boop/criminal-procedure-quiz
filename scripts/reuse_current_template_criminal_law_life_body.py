from pathlib import Path
import base64,gzip,json,copy

SRC=Path('admin-procedure-92-134')
DST=Path('criminal-law-life-body-100')
DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']

b64=''.join((SRC/n).read_text(encoding='utf-8') for n in parts)
html=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
newq=json.loads((DST/'questions.json').read_text(encoding='utf-8'))
assert len(newq)==100

# Locate the fixed template's 100-question JSON array without depending on JS variable names.
dec=json.JSONDecoder()
old=None
arr_start=arr_end=None
for i,ch in enumerate(html):
    if ch!='[':
        continue
    try:
        a,end=dec.raw_decode(html[i:])
    except Exception:
        continue
    if not (isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict)):
        continue
    keys=set(a[0])
    if ('opts' in keys or 'options' in keys) and ('q' in keys or 'question' in keys):
        old=a
        arr_start=i
        arr_end=i+end
        break
if old is None:
    raise RuntimeError('fixed template 100-question array not found')

converted=[]
for i,nq in enumerate(newq):
    b=copy.deepcopy(old[i])
    if 'q' in b: b['q']=nq['question']
    else: b['question']=nq['question']
    if 'opts' in b: b['opts']=nq['options']
    else: b['options']=nq['options']

    # Fixed quiz uses zero-based numeric answers; preserve the existing field name.
    ansnum='ABCD'.index(nq['answer'])
    if 'ans' in b: b['ans']=ansnum
    elif 'answer' in b: b['answer']=ansnum
    else: b['ans']=ansnum

    b['topic']=nq['topic']
    b['basis']=nq['basis']
    b['explanation']=nq['explanation']
    b['source']=nq['source']
    if 'url' in b:
        b['url']=''
    converted.append(b)

lit=json.dumps(converted,ensure_ascii=False,separators=(',',':'))
prefix=html[:arr_start]
suffix=html[arr_end:]

# Change only static UI labels, never the injected historical question text.
for oldlabel in [
    '行政程序法第92～134條',
    '行政程序法｜第92～134條',
    '行政程序法｜行政處分實境辨識強化',
    '行政處分實境辨識強化'
]:
    prefix=prefix.replace(oldlabel,'刑法分則｜殺人・傷害・墮胎・遺棄・185-4')
    suffix=suffix.replace(oldlabel,'刑法分則｜殺人・傷害・墮胎・遺棄・185-4')
prefix=prefix.replace('行政程序法','刑法')
suffix=suffix.replace('行政程序法','刑法')

# Namespace literal localStorage keys so progress is independent from every older quiz.
def namespace_storage(text):
    markers=['localStorage.getItem(','localStorage.setItem(','localStorage.removeItem(']
    found=[]
    for marker in markers:
        pos=0
        while True:
            p=text.find(marker,pos)
            if p<0: break
            j=p+len(marker)
            while j<len(text) and text[j].isspace(): j+=1
            if j<len(text) and text[j] in "'\"":
                quote=text[j]
                k=text.find(quote,j+1)
                if k>j:
                    key=text[j+1:k]
                    if key and key not in found: found.append(key)
            pos=p+len(marker)
    for key in found:
        newkey=key+'::criminal-law-life-body-100'
        text=text.replace("'"+key+"'","'"+newkey+"'")
        text=text.replace('"'+key+'"','"'+newkey+'"')
    return text,found

static=prefix+'\n'+suffix
_,keys=namespace_storage(static)
for key in keys:
    newkey=key+'::criminal-law-life-body-100'
    prefix=prefix.replace("'"+key+"'","'"+newkey+"'").replace('"'+key+'"','"'+newkey+'"')
    suffix=suffix.replace("'"+key+"'","'"+newkey+"'").replace('"'+key+'"','"'+newkey+'"')

html=prefix+lit+suffix

# Fixed presentation contract.
sp=html.find('id="qSource"')
qp=html.find('id="qTitle"')
if sp<0 or qp<0 or sp>qp:
    raise RuntimeError('source is not above question')
if 'feedbackSource' in html:
    raise RuntimeError('source is duplicated in feedback')

# Validate the injected array from the exact final HTML.
check_old=None
for i,ch in enumerate(html):
    if ch!='[': continue
    try:
        a,end=dec.raw_decode(html[i:])
    except Exception:
        continue
    if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and ('opts' in a[0] or 'options' in a[0]):
        check_old=a
        break
if check_old is None:
    raise RuntimeError('cannot re-open injected question bank')
first_text=check_old[0].get('q',check_old[0].get('question',''))
last_text=check_old[-1].get('q',check_old[-1].get('question',''))
assert first_text==newq[0]['question']
assert last_text==newq[-1]['question']

packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text(encoding='utf-8')) for n in parts]
total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:
        p=packed[pos:]
    else:
        take=round(len(packed)*sz/total)
        p=packed[pos:pos+take]
        pos+=take
    out.append(p)
for n,p in zip(parts,out):
    (DST/n).write_text(p,encoding='utf-8')

# Re-open exact browser payload.
browser_html=gzip.decompress(base64.b64decode(''.join(out))).decode('utf-8')
assert newq[0]['question'] in browser_html
assert newq[-1]['question'] in browser_html
assert browser_html.find('id="qSource"') < browser_html.find('id="qTitle"')
assert 'feedbackSource' not in browser_html

REV='20260911-criminal-law-life-body-100-v2'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>刑法分則｜殺人・傷害・墮胎・遺棄・185-4｜100題歷屆原題</title><script>(async()=>{{const v='{REV}';const names={json.dumps(parts)};const a=(await Promise.all(names.map(n=>fetch(n+'?v='+v,{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')

summary={
    'template':'admin-procedure-92-134',
    'question_count':100,
    'program_reused':True,
    'new_path':'criminal-law-life-body-100',
    'source_position':'above_question',
    'source_in_explanation':False,
    'storage_namespaced':True,
    'storage_literal_keys_found':keys,
    'cache_busted':True,
    'revision':REV,
    'final_bundle_first_question':newq[0]['question'],
    'final_bundle_last_question':newq[-1]['question'],
    'parts':{n:len(p) for n,p in zip(parts,out)}
}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
