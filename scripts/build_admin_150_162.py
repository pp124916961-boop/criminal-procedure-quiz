from pathlib import Path
import json,re,subprocess,sys,urllib.request

PARQUET_URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('admin-procedure-150-162'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(PARQUET_URL,P)
try:
 import pandas as pd
except Exception:
 subprocess.check_call([sys.executable,'-m','pip','install','-q','pandas','pyarrow']); import pandas as pd

df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()

def s(x): return '' if x is None else str(x)
def txt(r): return ' '.join(s(r.get(c)) for c in ['question','A','B','C','D'])

strong=[
 '法規命令','行政規則','裁量基準','解釋性規定','解釋性行政規則','裁量性行政規則',
 '行政程序法第150','行政程序法第151','行政程序法第152','行政程序法第153','行政程序法第154','行政程序法第155','行政程序法第156','行政程序法第157','行政程序法第158','行政程序法第159','行政程序法第160','行政程序法第161','行政程序法第162',
 '法律授權.*命令','命令.*法律授權','授權命令','職權命令','法規命令.*授權','法規命令.*無效','法規命令.*發布','法規命令.*公告','法規命令.*聽證','法規命令.*草案',
 '行政規則.*政府公報','行政規則.*拘束','行政規則.*下達','行政規則.*廢止','行政規則.*對外','行政規則.*內部'
]
exam_pref=['警察','一般警察','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路']

def score(r):
 t=txt(r); q=s(r.get('question')); sc=0
 for p in strong:
  if re.search(p,t): sc+=12
 if '法規命令' in q: sc+=15
 if '行政規則' in q: sc+=15
 if '裁量基準' in q or '解釋性規定' in q: sc+=10
 if '行政程序法' in t: sc+=5
 if any(k in s(r.get('exam_name')) for k in exam_pref): sc+=3
 # Penalize questions whose real center is clearly another chapter despite incidental wording.
 if any(k in q for k in ['行政處分之附款','行政契約','行政指導','行政計畫','送達','公示送達','聽證程序之主持','訴願管轄']): sc-=10
 sc+=max(0,int(r.get('year_roc') or 0)-100)*0.06
 return sc

df['score']=df.apply(score,axis=1)
cand=df[df['score']>=12].copy()
cand['sig']=cand[['question','A','B','C','D']].astype(str).agg('|'.join,axis=1)
cand=cand.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

def topic(r):
 t=txt(r)
 if any(k in t for k in ['行政規則','裁量基準','解釋性規定','解釋性行政規則','裁量性行政規則']): return '行政規則'
 return '法規命令'
cand['topic']=cand.apply(topic,axis=1)

# Prefer a balanced bank, then fill by relevance without editing any question text/options.
selected=[];used=set()
for tp,n in [('法規命令',60),('行政規則',40)]:
 for _,r in cand[cand['topic']==tp].head(n).iterrows():
  selected.append(r);used.add(r['sig'])
if len(selected)<100:
 for _,r in cand.iterrows():
  if r['sig'] in used: continue
  selected.append(r);used.add(r['sig'])
  if len(selected)>=100: break
if len(selected)<100:
 raise RuntimeError(f'Only {len(selected)} directly relevant unique original questions found for APA 150-162')
selected=selected[:100]

def law_info(r):
 t=txt(r); ans=s(r.get('answer')).strip().upper(); opts=[s(r.get(c)) for c in 'ABCD']; focus=opts['ABCD'.index(ans)] if ans in 'ABCD' else ''
 z=t+' '+focus
 if '行政規則' in z or '裁量基準' in z or '解釋性規定' in z:
  if any(k in focus for k in ['拘束訂定機關','下級機關','屬官','拘束力']): return '第161條','有效下達之行政規則，拘束訂定機關、其下級機關及屬官，但原則上不直接對人民發生法規範效力。'
  if any(k in focus for k in ['廢止','原發布機關']): return '第162條','行政規則得由原發布機關廢止；其廢止適用第160條的下達、發布規則。'
  if any(k in focus for k in ['政府公報','首長簽署','下達']): return '第160條','行政規則應下達下級機關或屬官；第159條第2項第2款之解釋性規定及裁量基準，應由首長簽署並登載政府公報發布。'
  return '第159條','行政規則是上級對下級或長官對屬官，依權限或職權所作、規範機關內部秩序運作而非直接對外發生法規範效力的一般抽象規定；並包括內部一般規定、解釋性規定及裁量基準。'
 # 法規命令
 if any(k in focus for k in ['牴觸憲法','牴觸法律','上級機關之命令','無法律之授權','未經核准','無效']): return '第158條','法規命令牴觸憲法、法律或上級命令，無法律授權而限制人民自由權利，或依法應經核准而未核准者，無效。'
 if any(k in focus for k in ['核定後','會銜發布','政府公報','新聞紙']) and '法規命令' in z: return '第157條','依法應經上級機關核定者，須核定後始得發布；數機關會同訂定者依規定核定後會銜發布；法規命令應刊登政府公報或新聞紙。'
 if '聽證' in focus and '法規命令' in z:
  if any(k in focus for k in ['日期及場所','主要程序','草案之全文','訂定機關']): return '第156條','依法舉行法規命令聽證時，應於政府公報或新聞紙公告訂定機關、依據、草案內容、聽證日期場所及主要程序。'
  return '第155條','行政機關訂定法規命令，得依職權舉行聽證。'
 if any(k in focus for k in ['任何人得於所定期間','草案全文','主要內容','情況急迫','公告周知']): return '第154條','擬訂法規命令原則應事先公告訂定機關、依據、草案全文或主要內容及陳述意見期間；情況急迫顯然無法事先公告者例外。'
 if any(k in focus for k in ['非主管','移送','無須訂定','著手研擬','通知原提議者']): return '第153條','人民或團體提議訂定法規命令後，受理機關應依是否主管、是否合法可規定、是否有必要等情形分別處理。'
 if any(k in focus for k in ['人民或團體提議','書面敘明','目的、依據及理由','附具相關資料']): return '第152條','法規命令除機關自行草擬外，也得由人民或團體提議；提議應以書面敘明目的、依據、理由並附相關資料。'
 if any(k in focus for k in ['修正','廢止','停止','恢復適用','軍事','外交','國家機密','安全']): return '第151條','訂定法規命令原則應依行政程序法程序；軍事、外交或重大事項涉及國家機密或安全者例外。修正、廢止、停止或恢復適用準用訂定程序。'
 return '第150條','法規命令須基於法律授權，對多數不特定人民就一般事項作成抽象、對外發生法律效果的規定；內容應明列授權依據，不得逾越授權範圍與立法精神。'

qs=[]
for i,r in enumerate(selected,1):
 ans=s(r.get('answer')).strip().upper()
 if ans not in 'ABCD': raise RuntimeError(f'bad answer at {i}: {ans}')
 basis,exp=law_info(r)
 qs.append({
  'id':i,'question':s(r.get('question')),'options':[s(r.get(c)) for c in 'ABCD'],'answer':ans,
  'topic':topic(r),'basis':basis,'explanation':exp,
  'source':f"{int(r.get('year_roc'))}年｜{s(r.get('exam_name'))}｜{s(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",
  'source_papers':s(r.get('source_papers')),'year_roc':int(r.get('year_roc'))
 })

assert len(qs)==100
assert len({q['question']+'|'.join(q['options']) for q in qs})==100
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
from collections import Counter
summary={'count':100,'topics':dict(Counter(q['topic'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'basis':dict(Counter(q['basis'] for q in qs)),'original_questions_unedited':True,'source_required':True}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
