from pathlib import Path
import base64,gzip,json,copy,re

SRC=Path('criminal-illegality-50')
DST=Path('constitution-rights-100')
DST.mkdir(parents=True,exist_ok=True)
parts=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']

newq=json.loads((DST/'questions.json').read_text(encoding='utf-8'))
assert len(newq)==100
assert all(len(q.get('options',[]))==4 for q in newq)
assert all(q.get('answer') in 'ABCD' for q in newq)
assert all(q.get('source_url','').startswith('https://wwwq.moex.gov.tw/') for q in newq)

# Use the exact same quiz program family as the Constitution 50-question versions.
html=gzip.decompress(base64.b64decode(''.join((SRC/n).read_text(encoding='utf-8') for n in parts))).decode('utf-8')

# Locate the template question array.
dec=json.JSONDecoder(); old=None; arr_start=arr_end=None
for i,ch in enumerate(html):
    if ch!='[': continue
    try:a,end=dec.raw_decode(html[i:])
    except Exception: continue
    if isinstance(a,list) and len(a)>=50 and a and isinstance(a[0],dict):
        keys=set(a[0])
        if ('opts' in keys or 'options' in keys) and ('q' in keys or 'question' in keys):
            old=a; arr_start=i; arr_end=i+end; break
if old is None:
    raise RuntimeError('fixed quiz question array not found')

# The UI is dynamic by QUESTIONS.length, so the same 50-question template can safely hold 100.
converted=[]
for i,nq in enumerate(newq):
    b=copy.deepcopy(old[i % len(old)])
    if 'q' in b:b['q']=nq['question']
    else:b['question']=nq['question']
    if 'opts' in b:b['opts']=nq['options']
    else:b['options']=nq['options']
    ans='ABCD'.index(nq['answer'])
    if 'ans' in b:b['ans']=ans
    elif 'answer' in b:b['answer']=ans
    else:b['ans']=ans
    b['topic']=nq.get('topic','憲法')
    b['basis']=nq.get('basis','')
    b['explanation']=nq.get('explanation','')
    b['source']=nq.get('source',f'第{i+1}題')
    # Critical bug fix: never leave href empty, or the quiz page opens itself.
    b['url']=nq['source_url']
    converted.append(b)

lit=json.dumps(converted,ensure_ascii=False,separators=(',',':'))
prefix=html[:arr_start]; suffix=html[arr_end:]

# Static labels only; historical question wording is injected later and stays untouched.
repls={
    '刑法 → 行政處分 50 題歷屆原題':'憲法 → 基本原則＋自由權利 100 題歷屆原題',
    '刑法 → 行政處分':'憲法 → 基本原則＋自由權利',
    '行政處分 50 題歷屆原題':'憲法 → 基本原則＋自由權利 100 題歷屆原題',
    '刑法總則｜違法性':'憲法｜基本原則＋自由權利',
    '刑法總則 違法性':'憲法｜基本原則＋自由權利',
    '違法性｜50題歷屆原題':'憲法 → 基本原則＋自由權利 100 題歷屆原題',
    '範圍限刑法至行政處分。題幹與選項保留歷屆試題原文，不自行改編；每題標示年度、考試、科目與原題題號。作答後立即顯示正解、法條／理論依據與簡要解析。':
      '範圍限憲法基本原則與自由權利。題幹與選項保留歷屆試題原文，不自行改編；每題標示年度、考試、科目與原題題號。作答後立即顯示正解、法條／理論依據與簡要解析。',
    '三等考試如原科目為申論題，本版不擅自改造成選擇題。高階選擇題以司法官／律師第一試原題補充。正犯共犯、罪數、刑罰等超出本次範圍者不收。':
      '本版限憲法基本原則與自由權利相關歷屆選擇題；中央政府體制等後續章節不納入本次範圍。',
    '司法官／律師第一試':'司法人員特考',
    '司法特考':'普通考試',
    '答案與解析依原題答案及現行刑法整理。':'答案依原考試官方答案整理；每題原題來源直接連結考選部試題。',
    '刑法總則｜違法性｜50題歷屆原題互動測驗｜本機自動保存進度':'憲法｜基本原則＋自由權利｜100題歷屆原題互動測驗｜本機自動保存進度'
}
for oldlabel,newlabel in repls.items():
    prefix=prefix.replace(oldlabel,newlabel)
    suffix=suffix.replace(oldlabel,newlabel)

# Convert every remaining static 50-question UI count to 100. This touches only prefix/suffix.
prefix=prefix.replace('50 題','100 題').replace('50題','100題')
suffix=suffix.replace('50 題','100 題').replace('50題','100題')

# Independent resumable progress.
ns='constitution-rights-100'
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

# Correct/wrong colors in the bottom question-number browser.
jump_css='''<style id="answer-jump-colors">
.jbtn.correct{background:#eaf8ef;border-color:#7bc8ad;color:#166534;font-weight:800}
.jbtn.wrong{background:#fff0f0;border-color:#f0a6a6;color:#b42318;font-weight:800}
</style>'''
html=html.replace('</head>',jump_css+'\n</head>',1)
old_jump="b.className='jbtn'+(state.answers[qi]?' done':'')+(idx===state.pos?' current':'');"
new_jump="const qa=state.answers[qi];\n    b.className='jbtn'+(qa?(qa.correct?' correct':' wrong'):'')+(idx===state.pos?' current':'');"
if old_jump not in html:
    raise RuntimeError('question-number browser hook not found')
html=html.replace(old_jump,new_jump,1)

# Persistent wrong-answer history, using this quiz's own ID/title.
if 'wrong-history.css' not in html:
    html=html.replace('</head>','<link rel="stylesheet" href="https://law-quiz-hub.pp124916961.chatgpt.site/wrong-history.css?v=1">\n</head>',1)
if 'wrong-history.js' not in html:
    qpos=html.find('const QUESTIONS')
    script_pos=html.rfind('<script>',0,qpos)
    if qpos < 0 or script_pos < 0:
        raise RuntimeError('could not locate main quiz script')
    html=html[:script_pos]+'<script src="https://law-quiz-hub.pp124916961.chatgpt.site/wrong-history.js?v=1"></script>\n'+html[script_pos:]

mount_repl='QuizWrongHistory?.mount({quizId:"constitution-rights-100", title:"憲法－基本原則＋自由權利100題", questions:QUESTIONS, getState:()=>state, idsAreQuestionIds:false})'
if 'QuizWrongHistory?.mount' in html:
    mount_pattern=r'QuizWrongHistory\?\.mount\(\{.*?\}\)'
    html,n=re.subn(mount_pattern,mount_repl,html,count=1,flags=re.S)
    if n!=1:
        raise RuntimeError('wrong-history mount replacement failed')
else:
    save_marker='function save(){'
    if save_marker not in html:
        raise RuntimeError('save() hook not found')
    mount_js='''const wrongHistory = window.QuizWrongHistory?.mount({quizId:"constitution-rights-100", title:"憲法－基本原則＋自由權利100題", questions:QUESTIONS, getState:()=>state, idsAreQuestionIds:false}) || {capture(){},newRound(){}};\nif(!window.QuizWrongHistory){ const warning=document.createElement("p"); warning.textContent="錯題紀錄功能未載入，請確認網路後重新整理。"; (document.getElementById("controlPanel")||document.getElementById("home")).appendChild(warning); }\n'''
    html=html.replace(save_marker,mount_js+'function save(){ wrongHistory.capture(state); ',1)

if 'wrongHistory.newRound(state)' not in html:
    m=re.search(r'(function start\([^)]*\)\{.*?state\s*=\s*\{.*?\};)(\s*currentRoundWrong\s*=\s*\[\];)',html,re.S)
    if not m:
        raise RuntimeError('start() hook not found')
    html=html[:m.end(1)]+'\n  wrongHistory.newRound(state);'+html[m.end(1):]
    retry_old="state.order=wrong; state.pos=0; state.mode='錯題重練'; currentRoundWrong=[];"
    retry_new="state.order=wrong; state.pos=0; state.mode='錯題重練'; wrongHistory.newRound(state); currentRoundWrong=[];"
    if retry_old in html:
        html=html.replace(retry_old,retry_new,1)

# Presentation/source checks.
if html.find('id="qSource"') > html.find('id="qTitle"'):
    raise RuntimeError('source must remain above question')
if 'feedbackSource' in html:
    raise RuntimeError('source duplicated in feedback')
if 'href=""' in html:
    # Empty anchors elsewhere would be a regression risk for source behavior.
    raise RuntimeError('empty href remains in final quiz')

# Re-open the final question array and verify all 100 official links made it through.
check=None
for i,ch in enumerate(html):
    if ch!='[': continue
    try:a,end=dec.raw_decode(html[i:])
    except Exception: continue
    if isinstance(a,list) and len(a)==100 and a and isinstance(a[0],dict) and ('opts' in a[0] or 'options' in a[0]):
        check=a; break
if check is None: raise RuntimeError('cannot re-open 100-question bank')
assert check[0].get('q',check[0].get('question'))==newq[0]['question']
assert check[-1].get('q',check[-1].get('question'))==newq[-1]['question']
assert all(x.get('url','').startswith('https://wwwq.moex.gov.tw/') for x in check)

# Pack exactly like the existing Constitution quizzes.
packed=base64.b64encode(gzip.compress(html.encode(),9)).decode()
orig=[len((SRC/n).read_text(encoding='utf-8')) for n in parts]
total=sum(orig); pos=0; out=[]
for j,sz in enumerate(orig):
    if j==len(orig)-1:p=packed[pos:]
    else:
        take=round(len(packed)*sz/total); p=packed[pos:pos+take]; pos+=take
    out.append(p)
for n,p in zip(parts,out):
    (DST/n).write_text(p,encoding='utf-8')

browser_html=gzip.decompress(base64.b64decode(''.join(out))).decode('utf-8')
assert newq[0]['question'] in browser_html and newq[-1]['question'] in browser_html
assert 'jbtn.correct' in browser_html and 'jbtn.wrong' in browser_html
assert "qa.correct?' correct':' wrong'" in browser_html
assert 'quizId:"constitution-rights-100"' in browser_html
assert 'https://wwwq.moex.gov.tw/' in browser_html
assert '刑法 → 行政處分' not in browser_html

REV='20260924-constitution-rights-100-source-jump-v1'
loader=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>憲法｜基本原則＋自由權利｜100題歷屆原題</title><script>(async()=>{{const v='{REV}';const names={json.dumps(parts)};const a=(await Promise.all(names.map(n=>fetch(n+'?v='+v,{{cache:'no-store'}}).then(r=>r.text())))).join('');const b=atob(a);const u=Uint8Array.from(b,c=>c.charCodeAt(0));const t=await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();document.open();document.write(t);document.close()}})();</script>'''
(DST/'index.html').write_text(loader,encoding='utf-8')

summary={
 'template':'criminal-illegality-50',
 'program_reused':True,
 'question_count':100,
 'new_path':'constitution-rights-100',
 'source_position':'above_question',
 'official_source_links':True,
 'question_number_colors':'correct green / wrong red',
 'storage_namespaced':True,
 'persistent_wrong_history':True,
 'revision':REV
}
(DST/'template-reuse-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
