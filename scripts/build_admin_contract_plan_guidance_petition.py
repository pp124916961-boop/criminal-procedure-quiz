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
def ans_text(r):
 a=S(r.get('answer')).strip().upper()
 return S(r.get(a)) if a in 'ABCD' else ''
def focus(r): return S(r.get('question'))+' '+ans_text(r)
PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路']
TOPIC_PATTERNS={
 '行政契約':['行政契約','公法上契約','和解契約','雙務契約','代替行政處分之行政契約','締結行政契約','契約之調整','終止契約','自願接受執行','契約無效'],
 '行政計畫':['行政計畫','計畫裁決','重大公共設施','集中事權'],
 '行政指導':['行政指導','不具法律上強制力','拒絕指導','輔導業者','勸告','建議'],
 '陳情':['陳情','陳情人','行政興革','行政法令之查詢','行政違失之舉發','一再陳情']
}

def topic(r):
 z=focus(r); q=S(r.get('question'))
 scores={k:0 for k in TOPIC_PATTERNS}
 for k,ps in TOPIC_PATTERNS.items():
  for p in ps:
   if p in q:scores[k]+=8
   elif p in ans_text(r):scores[k]+=5
 # Do not classify merely because a wrong option names one of the target chapters.
 return max(scores,key=scores.get) if max(scores.values())>0 else ''

def score(r):
 q=S(r.get('question')); z=focus(r); tp=topic(r); n=0
 if tp:n+=20
 for ps in TOPIC_PATTERNS.values():
  for p in ps:
   if p in q:n+=8
   elif p in ans_text(r):n+=4
 if '行政程序法' in q:n+=4
 ex=S(r.get('exam_name'))
 if any(k in ex for k in PREF):n+=4
 if '警察' in ex or '升官' in ex:n+=5
 if any(k in q for k in ['行政處分之附款','法規命令','行政規則','送達','訴願管轄']) and not any(p in z for ps in TOPIC_PATTERNS.values() for p in ps):n-=20
 return n+max(0,int(r.get('year_roc') or 0)-100)*.05

df['topic']=df.apply(topic,axis=1);df['score']=df.apply(score,axis=1)
c=df[(df.topic!='') & (df.score>=10)].copy();c['sig']=c[['question','A','B','C','D']].astype(str).agg('|'.join,axis=1)
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

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
 q=S(r.get('question')); f=ans_text(r); z=q+' '+f; tp=r['topic']
 if tp=='行政契約':
  if '自願接受執行' in z or ('強制執行' in z and '認可' in z):return '第148條','行政契約得約定自願接受執行；該約定須符合第148條之認可要求，始得作為強制執行名義。'
  if '情事重大變更' in z or ('顯失公平' in z and '調整' in z):return '第147條','契約締結後發生非當時所得預料之重大情事變更，依原約定顯失公平者，得請求調整；不能調整時得終止。'
  if '重大危害' in z or ('公益' in z and ('調整契約' in z or '終止契約' in z)):return '第146條','行政機關為防止或除去公益重大危害，得於必要範圍調整或終止契約，但須依第146條處理補償及書面理由。'
  if '顯增費用' in z or '不可預期之損失' in z:return '第145條','因締約機關所屬公法人其他機關於契約外行使公權力，使人民履約顯增費用或受不可預期損失者，得依第145條請求補償。'
  if '指導' in z or '協助' in z:return '第144條','行政契約一方為人民者，行政機關得就相對人履約，依書面約定方式為必要之指導或協助。'
  if '一部無效' in z:return '第143條','行政契約一部無效原則上全部無效；如可認欠缺該部分雙方仍會締約，其他部分仍有效。'
  if '無效' in z:return '第141條、第142條','行政契約無效除準用民法外，代替行政處分之行政契約另有第142條所定特別無效事由。'
  if '第三人' in z or '其他行政機關' in z:return '第140條','行政契約履行侵害第三人權利，或代替處分依法須經其他機關核准、同意或會同辦理者，須依法取得書面同意或核准始生效。'
  if '書面' in z:return '第139條','行政契約原則應以書面締結；法規另有其他方式規定者，依其規定。'
  if '甄選' in z or '競爭方式' in z:return '第138條','依法應以甄選或其他競爭方式決定人民締約相對人時，應事先公告資格及程序，並於決定前給予表示意見機會。'
  if '雙務' in z or ('給付' in z and '正當合理' in z):return '第137條','雙務行政契約須符合特定用途、助益行政職務、給付相當及正當合理關聯等法定要件。'
  if '和解' in z:return '第136條','行政機關對處分所依據之事實或法律關係經職權調查仍不能確定時，為達行政目的並解決爭執，得締結和解契約。'
  if '民法' in z:return '第149條','行政契約於行政程序法未規定者，準用民法相關規定。'
  return '第135條至第149條','本題依行政程序法行政契約章判斷。'
 if tp=='行政計畫':
  if '公開' in z or '聽證' in z or '集中事權' in z:return '第164條','一定地區土地特定利用或重大公共設施設置，涉及多數利益及多機關權限者，其計畫裁決應經公開與聽證，並得有集中事權效果。'
  return '第163條','行政計畫係行政機關為將來一定期限內達成特定目的或構想，事前就方法、步驟或措施所作的設計與規劃。'
 if tp=='行政指導':
  if '明確拒絕' in z or ('拒絕' in z and '不利' in z):return '第166條','相對人明確拒絕行政指導時，行政機關應即停止，且不得據此為不利處置。'
  if '負責指導者' in z or '請求交付文書' in z or '明示行政指導' in z:return '第167條','行政指導時應明示目的、內容及負責指導者；相對人請求交付文書時，除行政上有特別困難外，應以書面為之。'
  return '第165條、第166條','行政指導以輔導、協助、勸告、建議等不具法律上強制力的方法促請特定人作為或不作為，且不得濫用。'
 if tp=='陳情':
  if '言詞' in z or '朗讀' in z or '簽名或蓋章' in z:return '第169條','陳情得以書面或言詞為之；言詞陳情應作成紀錄並供陳情人確認。'
  if '保密' in z:return '第170條','行政機關應迅速、確實處理陳情；有保密必要者，處理時應不予公開。'
  if '補陳' in z or ('有理由' in z and '無理由' in z):return '第171條','陳情有理由者應採適當措施；無理由者應通知並說明；內容不明確或有疑義者得通知補陳。'
  if '移送' in z or '訴願' in z or '國家賠償' in z:return '第172條','陳情應向其他機關為之者，得告知或移送並通知；事項依法得提起訴願、訴訟或國賠者，應告知陳情人。'
  if '不予處理' in z or '一再陳情' in z or '真實姓名' in z:return '第173條','無具體內容或真實姓名住址、同一事由已適當處理仍一再陳情等法定情形，得不予處理。'
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
summary={'count':100,'topics':dict(Counter(q['topic'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'original_questions_unedited':True,'source_required':True,'topic_classification_uses_question_and_correct_option':True}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
