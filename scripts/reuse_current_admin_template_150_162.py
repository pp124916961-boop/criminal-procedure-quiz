from pathlib import Path
import base64,gzip,json,re,copy

SRC=Path('admin-procedure-54-91-102-109')
DST=Path('admin-procedure-150-162'); DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
b64=''.join((SRC/n).read_text(encoding='utf-8') for n in parts)
html=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
newq=json.loads((DST/'questions.json').read_text(encoding='utf-8'))
assert len(newq)==100

pat=re.compile(r'((?:const|let|var)\s+QUESTIONS\s*=\s*)(\[.*?\])(?=\s*;)',re.S)
m=pat.search(html)
if not m:
 # fallback to any 100-object quiz array
 for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S):
  try: a=json.loads(mm.group(2))
  except Exception: continue
  if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and 'opts' in a[0]: m=mm;break
if not m: raise RuntimeError('quiz array not found')
old=json.loads(m.group(2)); sample=old[0]
converted=[]
for i,nq in enumerate(newq):
 b=copy.deepcopy(old[i])
 b['q']=nq['question']; b['opts']=nq['options']; b['ans']='ABCD'.index(nq['answer'])
 b['topic']=nq['topic']; b['basis']=nq['basis']; b['explanation']=nq['explanation']; b['source']=nq['source']
 # Do not retain a URL from a different template question.
 if 'url' in b: b['url']=''
 converted.append(b)
lit=json.dumps(converted,ensure_ascii=False,separators=(',',':'))
html=html[:m.start(2)]+lit+html[m.end(2):]
# Visible content only; interface/controls/layout remain exactly the current program.
html=html.replace('行政程序法第54～91條、第102～109條','行政程序法第150～162條')
html=html.replace('聽證、陳述意見、送達','法規命令、行政規則')
# Replace old topic-specific note/collection copy if present, without changing DOM structure.
html=html.replace('行政程序法第54～91條、第102～109條｜100題歷屆原題','行政程序法第150～162條｜100題歷屆原題')

packed=base64.b64encode(gzip.compress(html.encode('utf-8'),compresslevel=9)).decode('ascii')
orig=[len((SRC/n).read_text(encoding='utf-8')) for n in parts]; total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
 if j==len(orig)-1: part=packed[pos:]
 else:
  take=round(len(packed)*sz/total); part=packed[pos:pos+take];pos+=take
 out.append(part)
for n,p in zip(parts,out): (DST/n).write_text(p,encoding='utf-8')
loader='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政程序法第150～162條｜100題歷屆原題</title><script>(async()=>{const names=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt'];const a=(await Promise.all(names.map(n=>fetch(n).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={'template':'admin-procedure-54-91-102-109','question_count':100,'program_reused':True,'source_position':'above_question','source_in_explanation':False,'stale_source_urls_removed':True,'answer_values_sample':[x['ans'] for x in converted[:10]],'parts':{n:len(p) for n,p in zip(parts,out)}}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
