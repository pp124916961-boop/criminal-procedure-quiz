from pathlib import Path
import json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('admin-contract-plan-guidance-petition'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)
df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()

def S(x): return '' if x is None else str(x)
def T(r): return ' '.join(S(r.get(c)) for c in ['question','A','B','C','D'])
PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路']
TOPIC_PATTERNS={
 '行政契約':['行政契約','公法上契約','和解契約','雙務契約','代替行政處分之行政契約','締結行政契約','契約之調整','終止契約','自願接受執行','強制執行約定','契約無效'],
 '行政計畫':['行政計畫','計畫裁決','重大公共設施','集中事權'],
 '行政指導':['行政指導','輔導、協助、勸告','輔導','勸告','建議','不具法律上強制力','拒絕指導'],
 '陳情':['陳情','陳情人','行政興革','行政法令之查詢','行政違失之舉發','一再陳情']
}

def topic(r):
 t=T(r); q=S(r.get('question'))
 scores={k:0 for k in TOPIC_PATTERNS}
 for k,ps in TOPIC_PATTERNS.items():
  for p in ps:
   if p in q:scores[k]+=6
   elif p in t:scores[k]+=2
 return max(scores,key=scores.get) if max(scores.values())>0 else ''

def score(r):
 t=T(r); q=S(r.get('question')); tp=topic(r); n=0
 if tp:n+=18
 for ps in TOPIC_PATTERNS.values():
  for p in ps:
   if p in q:n+=8
   elif p in t:n+=2
 if '行政程序法' in t:n+=4
 ex=S(r.get('exam_name'))
 if any(k in ex for k in PREF):n+=4
 if '警察' in ex or '升官' in ex:n+=5
 # keep questions centered on these four chapters
 if any(k in q for k in ['行政處分之附款','法規命令','行政規則','送達','訴願管轄']) and not any(p in q for ps in TOPIC_PATTERNS.values() for p in ps):n-=15
 return n+max(0,int(r.get('year_roc') or 0)-100)*.05

df['topic']=df.apply(topic,axis=1);df['score']=df.apply(score,axis=1)
c=df[(df.topic!='') & (df.score>=12)].copy();c['sig']=c[['question','A','B','C','D']].astype(str).agg('|'.join,axis=1)
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

# Original-question availability controls the final distribution. Contract gets the largest share; plan is intentionally smaller.
targets=[('行政契約',50),('行政計畫',10),('行政指導',20),('陳情',20)]
sel=[];used=set()
for tp,n in targets:
 for _,r in c[c.topic==tp].head(n).iterrows():sel.append(r);used.add(r.sig)
for _,r in c.iterrows():
 if len(sel)>=100:break
 if r.sig not in used:sel.append(r);used.add(r.sig)
if len(sel)<100:raise RuntimeError(f'Only {len(sel)} unique relevant original questions found')
sel=sel[:100]

def law(r):
 q=S(r.get('question')); a=S(r.get('answer')).strip().upper(); opts=[S(r.get(x)) for x in 'ABCD']; f=opts['ABCD'.index(a)] if a in 'ABCD' else ''; z=q+' '+f; tp=r['topic']
 if tp=='行政契約':
  if '書面' in z:return '第139條','行政契約原則應以書面締結；法規另有其他方式規定者，依其規定。'
  if '第三人' in z or '其他行政機關' in z:return '第140條','行政契約履行將侵害第三人權利，或代替之行政處分依法須經其他機關核准、同意或會同辦理者，應依法取得同意或核准始生效力。'
  if '無效' in z:return '第141條至第143條','行政契約無效須依第141條至第143條判斷，包括準用民法、違反法定締約界限及代替行政處分契約的特別無效事由。'
  if '和解' in z:return '第136條','行政機關對行政處分所依據之事實或法律關係經職權調查仍不能確定時，得為有效達成行政目的並解決爭執，締結和解契約。'
  if '雙務' in z or '給付' in z:return '第137條','雙務行政契約須符合特定用途、助益行政職務、給付相當及正當合理關聯等要件。'
  if '調整' in z or '終止' in z:return '第147條、第148條','情事重大變更得請求調整契約，不能調整時得終止；為防止或除去重大公益危害，行政機關得於法定條件下調整或終止。'
  if '自願接受執行' in z or '強制執行' in z:return '第148條','行政契約得依第148條約定自願接受執行；須以書面為之並經有權機關認可。'
  return '第135條至第149條','本題依行政程序法行政契約章判斷，重點包括締約容許性、和解或雙務契約、書面、生效、無效、履行、調整終止與強制執行。'
 if tp=='行政計畫':
  if '公開' in z or '聽證' in z or '集中事權' in z:return '第164條','一定地區土地特定利用或重大公共設施設置，涉及多數不同利益之人及多數不同行政機關權限者，其計畫裁決應經公開及聽證程序，並得有集中事權效果。'
  return '第163條','行政計畫係行政機關為將來一定期限內達成特定目的或構想，事前就方法、步驟或措施所作的設計與規劃。'
 if tp=='行政指導':
  if '拒絕' in z or '不利' in z:return '第166條','相對人明確拒絕行政指導時，行政機關應即停止，且不得因拒絕而對其為不利處置。'
  if '書面' in z or '目的' in z or '內容' in z or '負責指導者' in z:return '第167條','行政指導時應明示目的、內容及負責指導者；相對人請求交付文書時，除行政上有特別困難外，應以書面為之。'
  return '第165條、第166條','行政指導以輔導、協助、勸告、建議等不具法律上強制力的方法為之，並不得濫用。'
 if tp=='陳情':
  if '書面' in z or '言詞' in z:return '第169條','陳情得以書面或言詞為之；言詞陳情應作成紀錄並供陳情人確認。'
  if '保密' in z:return '第170條','行政機關應迅速確實處理陳情；有保密必要者，處理時應不予公開。'
  if '有理由' in z or '無理由' in z or '補陳' in z:return '第171條','陳情有理由者應採適當措施；無理由者應通知並說明意旨；內容不明確或有疑義者得通知補陳。'
  if '移送' in z or '訴願' in z or '國家賠償' in z:return '第172條','陳情應向其他機關為之者，得告知或移送並通知；事項依法得提起訴願、訴訟或請求國家賠償者，應告知陳情人。'
  if '不予處理' in z or '一再陳情' in z:return '第173條','無具體內容或真實姓名住址、同一事由已適當處理仍一再陳情等法定情形，得不予處理。'
  return '第168條','人民對行政興革建議、行政法令查詢、行政違失舉發或行政上權益維護，得向主管機關陳情。'
 return '行政程序法','依現行行政程序法判斷。'

qs=[]
for i,r in enumerate(sel,1):
 a=S(r.get('answer')).strip().upper()
 if a not in 'ABCD':raise RuntimeError(f'bad answer {i}')
 b,e=law(r)
 qs.append({'id':i,'question':S(r.get('question')),'options':[S(r.get(x)) for x in 'ABCD'],'answer':a,'topic':r['topic'],'basis':b,'explanation':e,'source':f"{int(r.get('year_roc'))}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",'source_papers':S(r.get('source_papers')),'year_roc':int(r.get('year_roc'))})
assert len(qs)==100
assert len({q['question']+'|'.join(q['options']) for q in qs})==100
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'count':100,'topics':dict(Counter(q['topic'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'original_questions_unedited':True,'source_required':True}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
