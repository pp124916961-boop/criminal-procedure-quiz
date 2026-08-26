from pathlib import Path
import base64, gzip, json, re, copy

SRC = Path('criminal-general-attempt')
DST = Path('admin-procedure-54-91-102-109')
DST.mkdir(parents=True, exist_ok=True)

part_names = ['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
b64 = ''.join((SRC / name).read_text(encoding='utf-8') for name in part_names)
html = gzip.decompress(base64.b64decode(b64)).decode('utf-8')
newq = json.loads((DST / 'questions.json').read_text(encoding='utf-8'))
assert len(newq) == 100

patterns = [
    re.compile(r'((?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*)(\[.*?\])(?=\s*;)', re.S),
    re.compile(r'(([A-Za-z_$][\w$]*)\s*=\s*)(\[.*?\])(?=\s*;)', re.S),
]
match = None
old_items = None
for pat in patterns:
    for m in pat.finditer(html):
        raw = m.group(3)
        try:
            arr = json.loads(raw)
        except Exception:
            continue
        if isinstance(arr, list) and len(arr) == 100 and arr and isinstance(arr[0], dict):
            if any(isinstance(v, list) and len(v) == 4 for v in arr[0].values()):
                match, old_items = m, arr
                break
    if match:
        break
if not match:
    raise RuntimeError('Could not locate Criminal Law 100-question array')

sample = old_items[0]
all_keys = set().union(*(x.keys() for x in old_items if isinstance(x, dict)))

def find_key(preferred, pred=None):
    for k in preferred:
        if k in all_keys:
            vals = [x.get(k) for x in old_items[:20]]
            if pred is None or any(pred(v) for v in vals):
                return k
    if pred:
        for k in all_keys:
            vals = [x.get(k) for x in old_items[:20]]
            if any(pred(v) for v in vals):
                return k
    return None

qkey = find_key(['question','q','text','stem','title'], lambda v:isinstance(v,str) and len(v)>=8)
okey = find_key(['options','choices','opts','answers'], lambda v:isinstance(v,list) and len(v)==4)
akey = find_key(['answer','ans','correct','key'], lambda v:(isinstance(v,str) and v.strip().upper() in 'ABCD') or isinstance(v,int))
lkey = find_key(['basis','law','article','legalBasis','legal_basis'], lambda v:isinstance(v,str) and ('第' in v or '刑法' in v))
ekey = find_key(['explanation','exp','analysis','note','reason'], lambda v:isinstance(v,str) and len(v)>=6)
skey = find_key(['source','origin','exam','citation','from','sourceLabel','source_label'], lambda v:isinstance(v,str) and ('年' in v or '考試' in v or '特考' in v or '出處' in v))
tkey = find_key(['topic','type','category','tag','chapter'], lambda v:isinstance(v,str) and len(v)<=40)
idkey = find_key(['id','no','number','index'], lambda v:isinstance(v,int))
# A generic integer fallback must never be allowed to steal the answer field (e.g. Criminal template uses numeric `ans`).
if idkey in {qkey, okey, akey, lkey, ekey, skey, tkey}:
    idkey = None

if not (qkey and okey and akey and ekey):
    raise RuntimeError(f'Could not map Criminal Law template schema; keys={sorted(all_keys)}')
if not skey:
    raise RuntimeError(f'Criminal Law template has no dedicated source field; keys={sorted(all_keys)}')

converted = []
for i, nq in enumerate(newq, 1):
    base = copy.deepcopy(old_items[min(i-1, len(old_items)-1)])
    base[qkey] = nq['question']
    base[okey] = nq['options']

    old_ans = sample.get(akey)
    if isinstance(old_ans, int):
        vals = [x.get(akey) for x in old_items if isinstance(x.get(akey), int)]
        zero_based = 0 in vals
        base[akey] = 'ABCD'.index(nq['answer']) + (0 if zero_based else 1)
    else:
        base[akey] = nq['answer']

    if idkey:
        base[idkey] = i
    if lkey:
        base[lkey] = nq.get('basis','')
    if tkey:
        base[tkey] = nq.get('topic','')

    # Source appears only in the Criminal Law template's dedicated source area.
    base[skey] = nq.get('source','').strip()

    # Explanation stays clean: no repeated source underneath it.
    exp = nq.get('explanation','').strip()
    exp = re.sub(r'\n\s*原題出處：.*$', '', exp, flags=re.S).strip()
    base[ekey] = exp
    converted.append(base)

new_literal = json.dumps(converted, ensure_ascii=False, separators=(',', ':'))
html = html[:match.start(3)] + new_literal + html[match.end(3):]

for a,b in {
    '刑法總則到未遂犯': '行政程序法第54～91條、第102～109條',
    '刑法總則': '行政程序法',
    '未遂犯': '聽證、陳述意見、送達',
}.items():
    html = html.replace(a,b)

packed = base64.b64encode(gzip.compress(html.encode('utf-8'), compresslevel=9)).decode('ascii')
orig_sizes = [len((SRC/name).read_text(encoding='utf-8')) for name in part_names]
orig_total = sum(orig_sizes)
pos = 0
parts = []
for idx, size in enumerate(orig_sizes):
    if idx == len(orig_sizes)-1:
        part = packed[pos:]
    else:
        target = round(len(packed) * size / orig_total)
        part = packed[pos:pos+target]
        pos += target
    parts.append(part)
for name, part in zip(part_names, parts):
    (DST / name).write_text(part, encoding='utf-8')

loader = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政程序法第54～91條、第102～109條｜100題歷屆原題</title><script>(async()=>{const names=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt'];const a=(await Promise.all(names.map(n=>fetch(n).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()})();</script>'''
(DST / 'index.html').write_text(loader, encoding='utf-8')

report = {
    'template': 'criminal-general-attempt',
    'question_count': len(converted),
    'program_reused': True,
    'source_field': skey,
    'source_in_explanation': False,
    'schema': {'question':qkey,'options':okey,'answer':akey,'law':lkey,'explanation':ekey,'source':skey,'topic':tkey,'id':idkey},
    'answer_values_sample': [x.get(akey) for x in converted[:10]],
    'parts': {name: len(part) for name,part in zip(part_names,parts)},
}
(DST / 'template-reuse-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
