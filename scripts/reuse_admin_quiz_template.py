from pathlib import Path
import base64, gzip, json, re, copy

SRC = Path('admin-procedure-20-53')
DST = Path('admin-procedure-54-91-102-109')
DST.mkdir(parents=True, exist_ok=True)

# 1) Read yesterday's exact program bundle.
b64 = ''.join((SRC / f'p{i}.txt').read_text(encoding='utf-8') for i in range(1, 6))
html = gzip.decompress(base64.b64decode(b64)).decode('utf-8')
newq = json.loads((DST / 'questions.json').read_text(encoding='utf-8'))
assert len(newq) == 100

# 2) Locate the 100-question data array in yesterday's JS without changing the program code.
#    We only replace the question-bank literal and visible range/title text.
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
            # Require something that looks like a 4-choice quiz question object.
            sample = arr[0]
            if any(isinstance(v, list) and len(v) == 4 for v in sample.values()):
                match, old_items = m, arr
                break
    if match:
        break
if not match:
    raise RuntimeError('Could not locate yesterday\'s 100-question array')

sample = old_items[0]
keys = list(sample.keys())

def choose_key(candidates, pred=None):
    for k in candidates:
        if k in sample and (pred is None or pred(sample[k])):
            return k
    if pred:
        for k, v in sample.items():
            if pred(v):
                return k
    return None

qkey = choose_key(['question','q','text','stem','title'], lambda v:isinstance(v,str) and len(v) >= 8)
okey = choose_key(['options','choices','opts','answers'], lambda v:isinstance(v,list) and len(v)==4)
akey = choose_key(['answer','ans','correct','key'], lambda v:(isinstance(v,str) and v.strip().upper() in 'ABCD') or isinstance(v,int))
lkey = choose_key(['basis','law','article','legalBasis','legal_basis'], lambda v:isinstance(v,str) and '第' in v and '條' in v)
ekey = choose_key(['explanation','exp','analysis','note','reason'], lambda v:isinstance(v,str) and len(v) >= 8)
tkey = choose_key(['topic','type','category','tag','chapter'], lambda v:isinstance(v,str) and len(v) <= 30)
idkey = choose_key(['id','no','number','index'], lambda v:isinstance(v,int))

if not (qkey and okey and akey):
    raise RuntimeError(f'Could not map question schema; keys={keys}')

# Preserve every object field and every program behavior from yesterday.
# Only overwrite fields that are question-bank content.
converted = []
for i, nq in enumerate(newq, 1):
    base = copy.deepcopy(old_items[min(i-1, len(old_items)-1)])
    base[qkey] = nq['question']
    base[okey] = nq['options']

    old_ans = sample[akey]
    if isinstance(old_ans, int):
        # Detect 0-based vs 1-based from yesterday's data.
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
    if ekey:
        exp = nq.get('explanation','').strip()
        src = nq.get('source','').strip()
        # Source is content only; no UI/program structure is changed.
        base[ekey] = (exp + ('\n\n原題出處：' + src if src else '')).strip()
    else:
        # If yesterday's schema has no explanation field, use the least invasive existing string field
        # only when it is clearly a note/analysis field; otherwise stop instead of changing UI code.
        raise RuntimeError('Yesterday template has no explanation field to place source information')
    converted.append(base)

new_literal = json.dumps(converted, ensure_ascii=False, separators=(',', ':'))
html = html[:match.start(3)] + new_literal + html[match.end(3):]

# 3) Change content labels/range only; program structure, CSS, controls and event logic remain yesterday's.
replacements = {
    '行政程序法第20～53條': '行政程序法第54～91條、第102～109條',
    '第20～53條': '第54～91條、第102～109條',
    '20～53': '54～91、102～109',
    '20-53': '54-91-102-109',
}
for a, b in replacements.items():
    html = html.replace(a, b)

# 4) Repack exactly like yesterday: tiny loader + 5 gzip/base64 chunks.
packed = base64.b64encode(gzip.compress(html.encode('utf-8'), compresslevel=9)).decode('ascii')
chunk = (len(packed) + 4) // 5
parts = [packed[i*chunk:(i+1)*chunk] for i in range(5)]
for i, part in enumerate(parts, 1):
    (DST / f'p{i}.txt').write_text(part, encoding='utf-8')

loader = '''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政程序法第54～91條、第102～109條｜100題國考選擇題</title><script>(async()=>{const names=[1,2,3,4,5].map(n=>`p${n}.txt`);const a=(await Promise.all(names.map(n=>fetch(n).then(r=>r.text())))).join("");const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream("gzip"))).text();document.open();document.write(t);document.close()})();</script>'''
(DST / 'index.html').write_text(loader, encoding='utf-8')

report = {
    'template': 'admin-procedure-20-53',
    'question_count': len(converted),
    'schema': {'question':qkey,'options':okey,'answer':akey,'law':lkey,'explanation':ekey,'topic':tkey,'id':idkey},
    'program_reused': True,
    'source_added_inside_existing_explanation': True,
    'bundle_parts': [len(x) for x in parts],
}
(DST / 'template-reuse-summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
