from pathlib import Path
import base64,gzip,json,copy,re

SRC=Path('criminal-illegality-50')
DST=Path('police-promotion-111-admin-law'); DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
html=gzip.decompress(base64.b64decode(''.join((SRC/n).read_text(encoding='utf-8') for n in parts))).decode('utf-8')
newq=json.loads((DST/'questions.json').read_text(encoding='utf-8')); assert len(newq)==50

dec=json.JSONDecoder(); old=None; arr_start=arr_end=None
for i,ch in enumerate(html):
    if ch!='[': continue
    try:a,end=dec.raw_decode(html[i:])
    except Exception: continue
    if isinstance(a,list) and len(a)>=50 and a and isinstance(a[0],dict):
        keys=set(a[0])
        if ('opts' in keys or 'options' in keys) and ('q' in keys or 'question' in keys):
            old=a; arr_start=i; arr_end=i+end; break
if old is None: raise RuntimeError('fixed quiz question array not found')

converted=[]
for i,nq in enumerate(newq):
    b=copy.deepcopy(old[i])
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
    prefix=prefix.replace(oldlabel,'111警察升官等｜行政法')
    suffix=suffix.replace(oldlabel,'111警察升官等｜行政法')

ns='police-promotion-111-admin-law'
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

# Add the same persistent wrong-answer history module used by the neighboring quizzes.
# It stores attempt history separately from the ordinary resumable progress key.
if 'wrong-history.css' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="https://law-quiz-hub.pp124916961.chatgpt.site/wrong-history.css?v=1">\n</head>',1)

if 'wrong-history.js' not in html:
    qpos=html.find('const QUESTIONS')
    script_pos=html.rfind('<script>',0,qpos)
    if qpos < 0 or script_pos < 0:
        raise RuntimeError('could not locate main quiz script for wrong-history module')
    html=html[:script_pos]+'<script src="https://law-quiz-hub.pp124916961.chatgpt.site/wrong-history.js?v=1"></script>\n'+html[script_pos:]

if 'QuizWrongHistory?.mount' not in html:
    save_marker='function save(){'
    if save_marker not in html:
        raise RuntimeError('save() hook not found for wrong-history module')
    mount_js='''const wrongHistory = window.QuizWrongHistory?.mount({quizId:"police-promotion-111-admin-law", title:"111警察升官等－行政法", questions:QUESTIONS, getState:()=>state, idsAreQuestionIds:false}) || {capture(){},newRound(){}};
if(!window.QuizWrongHistory){ const warning=document.createElement("p"); warning.textContent="錯題紀錄功能未載入，請確認網路後重新整理。"; (document.getElementById("controlPanel")||document.getElementById("home")).appendChild(warning); }
'''
    html=html.replace(save_marker,mount_js+'function save(){ wrongHistory.capture(state); ',1)

    # A brand-new ordinary attempt gets its own history round.
    m=re.search(r'(function start\([^)]*\)\{.*?state\s*=\s*\{.*?\};)(\s*currentRoundWrong\s*=\s*\[\];)',html,re.S)
    if not m:
        raise RuntimeError('start() hook not found for wrong-history new round')
    html=html[:m.end(1)]+'\n  wrongHistory.newRound(state);'+html[m.end(1):]

    # Wrong-question retry is also a distinct attempt in history.
    retry_old="state.order=wrong; state.pos=0; state.mode='錯題重練'; currentRoundWrong=[];"
    retry_new="state.order=wrong; state.pos=0; state.mode='錯題重練'; wrongHistory.newRound(state); currentRoundWrong=[];"
    if retry_old in html:
        html=html.replace(retry_old,retry_new,1)

if html.find('id="qSource"') > html.find('id="qTitle"'):
    raise RuntimeError('source not above question')
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

REV='20260919-police-promotion-111-admin-law-official-history-v3'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>111警察升官等｜行政法｜50題原題</title><script>(async()=>{{const v='{REV}';const names={json.dumps(parts)};const a=(await Promise.all(names.map(n=>fetch(n+'?v='+v,{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')
summary={'template':'criminal-illegality-50','question_count':50,'program_reused':True,'new_path':'police-promotion-111-admin-law','source_position':'above_question','source_in_explanation':False,'storage_namespaced':True,'persistent_wrong_history':True,'wrong_history_ui':'date + wrong-count summary; click for question details','cache_busted':True,'revision':REV}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
