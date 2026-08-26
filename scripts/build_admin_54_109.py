from pathlib import Path
import json, re, subprocess, sys, urllib.request

PARQUET_URL = 'https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT = Path('admin-procedure-54-91-102-109')
OUT.mkdir(parents=True, exist_ok=True)
parquet = Path('/tmp/tw_legal_benchmark_v2.parquet')
if not parquet.exists():
    urllib.request.urlretrieve(PARQUET_URL, parquet)

try:
    import pandas as pd
except Exception:
    subprocess.check_call([sys.executable,'-m','pip','install','-q','pandas','pyarrow'])
    import pandas as pd

df = pd.read_parquet(parquet)
df = df[df['subject'].isin(['admin','public','foundational'])].copy()

def norm(x): return '' if x is None else str(x)
def combined(r): return ' '.join(norm(r.get(c)) for c in ['question','A','B','C','D'])

strong = [
    '行政程序法.*聽證','聽證程序','預備聽證','聽證紀錄','聽證之主持人','聽證主持人','再為聽證',
    '經聽證程序','舉行聽證','聽證終結','公開以言詞','聽證期日','聽證之期日','聲明異議',
    '行政程序法.*送達','公示送達','寄存送達','補充送達','留置送達','送達處所','應受送達人',
    '送達之文書','送達證書','送達代收人','囑託送達','郵政機關送達','自行送達','電子交換.*送達',
    '行政程序法.*陳述意見','陳述意見之機會','給予.*陳述意見','不給予.*陳述意見','書面陳述','言詞陳述',
    '行政處分.*陳述意見','陳述意見.*行政處分','聽證.*訴願','訴願.*聽證'
]
weak = ['聽證','送達','陳述意見']
exam_pref = ['警察','一般警察','司法人員','司法官','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路']

def score(r):
    txt, q = combined(r), norm(r.get('question'))
    s = sum(12 for p in strong if re.search(p, txt))
    for w in weak: s += 8 if w in q else (3 if w in txt else 0)
    if '行政程序法' in txt: s += 8
    if any(k in txt for k in ['公示送達','寄存送達','補充送達','留置送達','預備聽證','聽證紀錄']): s += 8
    if any(k in txt for k in ['行政訴訟法之送達','民事訴訟法之送達','刑事訴訟法之送達']): s -= 18
    if any(k in norm(r.get('exam_name')) for k in exam_pref): s += 3
    s += max(0, int(r.get('year_roc') or 0)-100) * 0.08
    return s

df['match_score'] = df.apply(score, axis=1)
cand = df[df['match_score'] >= 10].copy()
cand['dedup'] = cand[['question','A','B','C','D']].astype(str).agg('|'.join, axis=1)
cand = cand.sort_values(['match_score','year_roc'], ascending=[False,False]).drop_duplicates('dedup')

def topic(r):
    t=combined(r)
    if '陳述意見' in t or '書面陳述' in t or '言詞陳述' in t: return '陳述意見'
    if '聽證' in t: return '聽證'
    return '送達'

cand['topic']=cand.apply(topic,axis=1)
quotas={'聽證':34,'陳述意見':26,'送達':40}
selected=[]; used=set()
for tp,n in quotas.items():
    for _,r in cand[cand['topic']==tp].head(n).iterrows(): selected.append(r); used.add(r['dedup'])
if len(selected)<100:
    for _,r in cand.iterrows():
        if r['dedup'] in used: continue
        selected.append(r); used.add(r['dedup'])
        if len(selected)>=100: break
if len(selected)<100: raise RuntimeError(f'Only {len(selected)} directly relevant unique questions found')
selected=selected[:100]

def law_info(r):
    t=combined(r)
    if '陳述意見' in t or '書面陳述' in t or '言詞陳述' in t:
        if any(k in t for k in ['大量作成','急迫','公益','事實客觀上明白','自由或權利之限制內容及程度顯屬輕微','已依第三十九條通知','已舉行聽證','得不給予']): return '第103條','行政程序法第103條列舉得不給予陳述意見機會之例外；判斷時要先確認是否落入法定例外。'
        if any(k in t for k in ['書面通知','通知相對人陳述意見','通知書']): return '第104條','行政機關給予陳述意見機會時，原則應以書面通知相對人並記載法定事項；得以言詞通知時須作成紀錄。'
        if '書面陳述' in t or '書面提出' in t: return '第105條','以書面陳述意見者，應就事實及法律上陳述提出；逾期未提出者，視為放棄陳述機會。'
        if '言詞陳述' in t or '口頭' in t: return '第106條','相對人得於期限內以言詞陳述代替書面陳述，行政機關應作成紀錄並交其確認。'
        if '聽證' in t and any(k in t for k in ['法規明文','認為有必要','必要時']): return '第107條','行政處分之聽證，於法規明文規定或行政機關認為有必要時舉行。'
        return '第102條','行政機關作成限制或剝奪人民自由或權利之行政處分前，原則上應給予相對人陳述意見機會。'
    if '聽證' in t:
        if '預備聽證' in t: return '第58條','必要時得於聽證期日前舉行預備聽證，以議定程序、釐清爭點、提出文書或證據等事項。'
        if any(k in t for k in ['公開以言詞','公開為原則','不公開']): return '第59條','聽證除法律另有規定外，以公開、言詞為原則；有法定情形得全部或一部不公開。'
        if any(k in t for k in ['首長或其指定','主持人']):
            if '異議' in t: return '第63條','當事人認為主持人於聽證程序所為處置違法或不當者，得即時聲明異議，由主持人即時處理。'
            return '第57條、第62條','聽證由機關首長或指定人員主持；主持人應本中立公正立場主持並行使法定程序指揮權。'
        if '聽證紀錄' in t or '紀錄' in t: return '第64條','聽證應作成聽證紀錄，記載法定事項；當事人對紀錄有異議時得即時提出。'
        if any(k in t for k in ['再為聽證','重新聽證']): return '第66條','聽證終結後、行政處分作成前，行政機關認有必要時得再為聽證。'
        if any(k in t for k in ['終結','終止聽證']): return '第65條','當事人意見已充分陳述且案件達可為決定程度時，主持人應終結聽證。'
        if any(k in t for k in ['訴願','先行程序','行政救濟']): return '第109條','不服依聽證程序作成之行政處分者，免除訴願及其先行程序，得直接提起行政訴訟。'
        if any(k in t for k in ['依聽證紀錄','斟酌全部聽證結果','聽證結果']): return '第108條','經聽證作成行政處分時，應斟酌全部聽證結果；法律明定應依聽證紀錄者，應依紀錄作成。'
        if any(k in t for k in ['期日','場所','書面通知']): return '第55條、第56條','行政機關應於聽證前以書面通知法定事項；有正當理由得變更期日或場所並通知、公告。'
        if any(k in t for k in ['陳述意見','提出證據','發問']): return '第61條','當事人於聽證時得陳述意見、提出證據，經主持人許可並得向相關人員發問。'
        return '第54條、第107條','聽證依行政程序法或其他法規舉行；行政處分之聽證於法規明定或機關認有必要時舉行。'
    if '公示送達' in t:
        if any(k in t for k in ['二十日','20日','六十日','60日','發生效力']): return '第81條','公示送達原則自公告之日起經20日發生效力；依第78條第1項第3款對境外送達者為60日；重複公示送達有特別規定。'
        if any(k in t for k in ['公告欄','政府公報','新聞紙','保管送達之文書']): return '第80條','公示送達由行政機關保管文書並於公告欄黏貼公告；必要時並得刊登政府公報或新聞紙。'
        if any(k in t for k in ['處所不明','治外法權','外國或境外','依申請','依職權']): return '第78條、第79條','第78條規定公示送達的法定原因及依申請／職權方式；對同一當事人後續公示送達，第79條另有規定。'
        return '第78條至第82條','公示送達須有法定原因，並依公告方式、效力期間及證書規定辦理。'
    if '寄存送達' in t or '寄存' in t: return '第74條','不能依通常或補充／留置方式送達時，得將文書寄存於送達地地方自治、警察機關或郵政機關，並製作兩份通知書。'
    if '補充送達' in t or any(k in t for k in ['同居人','受雇人','接收郵件人員']): return '第73條第1項','於應送達處所不獲會晤本人時，得交付有辨別事理能力之同居人、受雇人或接收郵件人員，但利益相反者除外。'
    if '留置送達' in t or '拒絕收領' in t: return '第73條第3項','應受送達人或有權收受者無正當理由拒絕收領時，得將文書留置於應送達處所，以為送達。'
    if any(k in t for k in ['行政機關自行','郵政機關','電子交換','電子郵件','傳真']): return '第68條','送達由行政機關自行或交郵政機關為之；依法以電子交換者視為自行送達，對權益有重大影響者原則應採掛號。'
    if any(k in t for k in ['法定代理人','無行政程序行為能力','代表人','管理人']): return '第69條','對無行政程序行為能力人應向其法定代理人送達；機關、法人或非法人團體向代表人或管理人送達。'
    if '外國法人' in t: return '第70條','對外國法人或團體在我國有事務所或營業所者，向其在我國代表人或管理人送達。'
    if '代理人' in t and '送達' in t: return '第71條','代理人受送達權限未受限制時，原則應向代理人送達；必要時亦得送達於當事人本人。'
    if '送達處所' in t or any(k in t for k in ['住所','居所','事務所','營業所','工作地']): return '第72條','送達原則於應受送達人之住居所、事務所或營業所為之；必要時得於就業處所送達。'
    if '送達證書' in t: return '第76條','送達人應作成送達證書，記載法定事項並由收領人簽名、蓋章或按指印。'
    if '送達代收人' in t: return '第83條','在中華民國無住居所、事務所或營業所者，行政機關得命其指定境內送達代收人；未指定時得依規定以掛號寄送。'
    if any(k in t for k in ['星期日','日出前','日沒後']): return '第84條','送達原則不得於星期日、其他休息日或日出前、日沒後為之；但有法定例外或受領人不拒絕者不在此限。'
    if '不能送達' in t: return '第85條','送達不能時，送達人應作成報告書，記載不能送達之事由，並將文書繳回行政機關。'
    if '外國或境外' in t: return '第86條','於外國或境外送達，原則囑託該國管轄機關或我國駐外使領館等為之；不能依此辦理時得按規定以雙掛號郵寄。'
    if '治外法權' in t: return '第87條','對享有治外法權之人送達，得囑託外交部為之。'
    if '軍人' in t or '軍艦' in t: return '第88條','對現役軍人或軍艦乘員送達，囑託其服務機關或艦長為之。'
    if '監獄' in t or '看守所' in t or '在監' in t: return '第89條','對在監所人送達，囑託監所長官為之。'
    if '外國機關' in t and '送達' in t: return '第90條','應向外國機關或團體送達時，得囑託外交部為之。'
    return '第67條至第91條','行政程序法第67條至第91條規範行政文書送達的方式、處所、特殊送達、公示送達及效力。'

questions=[]
for i,r in enumerate(selected,1):
    basis,expl=law_info(r)
    questions.append({'id':i,'question':norm(r['question']),'options':[norm(r['A']),norm(r['B']),norm(r['C']),norm(r['D'])],'answer':norm(r['answer']).strip().upper(),'topic':topic(r),'basis':basis,'explanation':expl,'source':f"{int(r['year_roc'])}年｜{norm(r['exam_name'])}｜{norm(r['subject_zh'])}｜第{int(r['q_no'])}題",'source_papers':norm(r['source_papers']),'year_roc':int(r['year_roc'])})
assert len(questions)==100
for q in questions: assert q['answer'] in 'ABCD' and len(q['options'])==4 and all(q['options'])
(OUT/'questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
DATA=json.dumps(questions,ensure_ascii=False).replace('</','<\\/')
page=r'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>行政程序法｜聽證・陳述意見・送達 100題</title><style>:root{--bg:#f3f6fb;--card:#fff;--ink:#172033;--muted:#657087;--line:#dce3ee;--ok:#14804a;--bad:#bd2939;--accent:#1d4ed8;--soft:#eef4ff}*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,"Noto Sans TC","Microsoft JhengHei",sans-serif;background:var(--bg);color:var(--ink)}.wrap{max-width:880px;margin:auto;padding:18px}.hero{background:linear-gradient(135deg,#102a56,#1d4ed8);color:white;border-radius:22px;padding:24px;box-shadow:0 12px 34px #17376b24}.hero h1{margin:0 0 8px;font-size:clamp(24px,4vw,36px)}.hero p{margin:6px 0;opacity:.9}.bar{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:14px 0}.stat,.card{background:var(--card);border:1px solid var(--line);border-radius:18px;box-shadow:0 6px 22px #21385b0b}.stat{padding:13px;text-align:center}.stat b{display:block;font-size:21px}.stat span{font-size:12px;color:var(--muted)}.controls{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.btn{border:1px solid var(--line);background:white;padding:10px 13px;border-radius:12px;font-weight:700;cursor:pointer}.btn.primary{background:var(--accent);color:white;border-color:var(--accent)}.btn:disabled{opacity:.45;cursor:not-allowed}.card{padding:20px}.meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}.pill{font-size:12px;background:var(--soft);color:#254c96;padding:5px 9px;border-radius:999px}.source{font-size:13px;color:var(--muted);line-height:1.5;margin:8px 0 14px}.q{font-weight:800;font-size:19px;line-height:1.65;margin:8px 0 16px}.opt{width:100%;text-align:left;border:1px solid var(--line);background:white;border-radius:14px;padding:13px 14px;margin:8px 0;cursor:pointer;font-size:16px;line-height:1.5}.opt:hover{border-color:#9db5e8;background:#fbfdff}.opt.correct{border-color:#71c99b;background:#effaf4}.opt.wrong{border-color:#e799a2;background:#fff3f4}.opt.lock{cursor:default}.feedback{display:none;margin-top:16px;border-top:1px solid var(--line);padding-top:16px}.feedback.show{display:block}.feedback .ans{font-weight:800}.ok{color:var(--ok)}.bad{color:var(--bad)}.basis{background:#f7f9fc;border-left:4px solid var(--accent);padding:12px;border-radius:8px;margin-top:10px;line-height:1.65}.nav{display:flex;justify-content:space-between;gap:8px;margin-top:14px}.jump{display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-top:12px}.jump input{width:76px;padding:9px;border:1px solid var(--line);border-radius:10px}.footer{font-size:12px;color:var(--muted);text-align:center;margin:18px 0 30px;line-height:1.6}@media(max-width:600px){.bar{grid-template-columns:repeat(2,1fr)}.card{padding:15px}.wrap{padding:11px}.q{font-size:17px}}</style></head><body><div class="wrap"><section class="hero"><h1>行政程序法 100題</h1><p>範圍：第54～91條、第102～109條｜聽證・陳述意見・送達</p><p>歷屆國考原題（題幹與選項不改編）｜每題附出處、現行法條與簡析</p></section><div class="bar"><div class="stat"><b id="pos">1/100</b><span>目前題號</span></div><div class="stat"><b id="done">0</b><span>已作答</span></div><div class="stat"><b id="rate">—</b><span>正確率</span></div><div class="stat"><b id="wrong">0</b><span>錯題數</span></div></div><div class="controls"><button class="btn primary" id="ordered">依序100題</button><button class="btn" id="shuffle">隨機100題</button><button class="btn" id="retry">錯題重練</button><button class="btn" id="reset">重設進度</button></div><section class="card"><div class="meta"><span class="pill" id="topic"></span><span class="pill" id="basisTop"></span></div><div class="source" id="source"></div><div class="q" id="question"></div><div id="options"></div><div class="feedback" id="feedback"></div><div class="nav"><button class="btn" id="prev">← 上一題</button><button class="btn" id="next">下一題 →</button></div><div class="jump"><span>跳至題號</span><input id="jump" type="number" min="1" max="100"><button class="btn" id="go">前往</button></div></section><div class="footer">題目／標準答案：考選部歷屆國家考試資料；題庫整理 metadata：Taiwan Legal Benchmark v2。解析以現行《行政程序法》為準。舊題如涉及修法，以現行法提示為準。</div></div><script>const BASE=__DATA__;const KEY='ap54_91_102_109_v1';let order=[...Array(BASE.length).keys()],idx=0;let state=JSON.parse(localStorage.getItem(KEY)||'{"answers":{}}');function save(){localStorage.setItem(KEY,JSON.stringify(state))}function current(){return BASE[order[idx]]}function stats(){const v=Object.values(state.answers),d=v.length,o=v.filter(x=>x.correct).length;done.textContent=d;wrong.textContent=d-o;rate.textContent=d?Math.round(o/d*100)+'%':'—';pos.textContent=(idx+1)+'/'+order.length}function render(){const q=current(),s=state.answers[q.id];topic.textContent=q.topic;basisTop.textContent='行政程序法'+q.basis;source.textContent='出處：'+q.source+'｜原卷代碼：'+q.source_papers;question.textContent='第'+(idx+1)+'題　'+q.question;options.innerHTML='';q.options.forEach((x,i)=>{const l='ABCD'[i],b=document.createElement('button');b.className='opt';b.textContent='('+l+') '+x;if(s){b.classList.add('lock');if(l===q.answer)b.classList.add('correct');if(l===s.choice&&l!==q.answer)b.classList.add('wrong')}b.onclick=()=>answer(l);options.appendChild(b)});if(s){feedback.className='feedback show';feedback.innerHTML='<div class="ans '+(s.correct?'ok':'bad')+'">'+(s.correct?'✓ 答對':'✗ 答錯')+'　正確答案：'+q.answer+'</div><div class="basis"><b>法條依據：行政程序法'+q.basis+'</b><br>'+q.explanation+'</div>'}else{feedback.className='feedback';feedback.innerHTML=''}prev.disabled=idx===0;next.disabled=idx===order.length-1;jump.max=order.length;stats();window.scrollTo({top:0,behavior:'smooth'})}function answer(l){const q=current();if(state.answers[q.id])return;state.answers[q.id]={choice:l,correct:l===q.answer};save();render()}prev.onclick=()=>{if(idx>0){idx--;render()}};next.onclick=()=>{if(idx<order.length-1){idx++;render()}};go.onclick=()=>{let n=parseInt(jump.value);if(n>=1&&n<=order.length){idx=n-1;render()}};ordered.onclick=()=>{order=[...Array(BASE.length).keys()];idx=0;render()};shuffle.onclick=()=>{order=[...Array(BASE.length).keys()].sort(()=>Math.random()-.5);idx=0;render()};retry.onclick=()=>{const ids=new Set(Object.entries(state.answers).filter(([k,v])=>!v.correct).map(([k])=>+k));if(!ids.size){alert('目前沒有錯題。');return}order=BASE.map((q,i)=>ids.has(q.id)?i:-1).filter(i=>i>=0);idx=0;render()};reset.onclick=()=>{if(confirm('確定清除全部作答紀錄？')){state={answers:{}};save();order=[...Array(BASE.length).keys()];idx=0;render()}};render();</script></body></html>'''.replace('__DATA__',DATA)
(OUT/'index.html').write_text(page,encoding='utf-8')
from collections import Counter
summary={'count':len(questions),'candidates':len(cand),'topics':dict(Counter(q['topic'] for q in questions)),'years':dict(Counter(str(q['year_roc']) for q in questions)),'first5':[{k:q[k] for k in ('question','answer','source','basis')} for q in questions[:5]]}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
