from pathlib import Path
import json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('admin-disposition-situational'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)
df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()

def S(x): return '' if x is None else str(x)
def T(r): return ' '.join(S(r.get(c)) for c in ['question','A','B','C','D'])
PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路']
CORE=['行政處分','一般處分','事實行為','附款','期限','條件','負擔','保留行政處分之廢止權','行政處分之效力','行政處分.*無效','重大明顯','程序補正','行政處分.*轉換','違法行政處分','職權撤銷','信賴保護','信賴不值得保護','合法行政處分','行政處分.*廢止','程序再開','行政處分.*送達','顯然錯誤']
SITU=['下列何者.*行政處分','下列何種.*行政處分','何者為行政處分','何者非行政處分','何者不是行政處分','事實行為','下列何者.*事實行為','何種附款','何者為.*附款','屬於何種附款','下列.*附款','甲','乙','某市','某縣','某機關','主管機關','警察機關']
CONCRETE=['核發','吊銷','撤銷','廢止','命令','命其','通知','許可','駁回','登記','拒絕','補助','拆除','公告','警告','扣押','取締','勸導','給付']

def situational(r):
 q=S(r.get('question')); t=T(r); n=0
 for p in SITU:
  if re.search(p,q): n+=1
 if sum(1 for k in CONCRETE if k in t)>=2:n+=1
 if ('附款' in t and any(k in t for k in ['期限','條件','負擔','廢止權'])):n+=1
 return n>0

def score(r):
 t=T(r);q=S(r.get('question'));n=sum(10 for k in CORE if re.search(k,t))
 if '行政處分' in q:n+=16
 if '附款' in q:n+=14
 if '事實行為' in q:n+=16
 if situational(r):n+=18
 if any(k in S(r.get('exam_name')) for k in PREF):n+=4
 if '警察' in S(r.get('exam_name')) or '升官' in S(r.get('exam_name')):n+=5
 if any(k in q for k in ['行政契約','行政指導','法規命令','行政規則','行政計畫']) and '行政處分' not in q:n-=14
 if any(k in q for k in ['行政訴訟種類','行政訴訟法','訴願管轄','國家賠償']) and not any(k in q for k in ['救濟期間','救濟方法']):n-=35
 return n+max(0,int(r.get('year_roc') or 0)-100)*.05

df['score']=df.apply(score,axis=1);df['situational']=df.apply(situational,axis=1)
c=df[df.score>=12].copy();c['sig']=c[['question','A','B','C','D']].astype(str).agg('|'.join,axis=1)
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

def grp(r):
 t=T(r);q=S(r.get('question'))
 if '附款' in t or any(k in t for k in ['保留行政處分之廢止權','停止條件','解除條件','負擔']):return '附款辨識與合法性'
 if any(k in t for k in ['行政處分之無效','行政處分無效','重大明顯','程序補正','轉換','自始不生效力','效力繼續存在','行政處分之效力','行政處分效力','顯然錯誤','救濟期間','書面之行政處分','書面行政處分','不記明理由','送達','公告日']):return '效力與瑕疵'
 if any(k in t for k in ['職權撤銷','信賴保護','信賴不值得','合法行政處分','廢止','補償']):return '撤銷廢止與信賴保護'
 if any(k in t for k in ['一般處分','事實行為']) or re.search('何者.*行政處分|何種.*行政處分|行政處分.*何者',q):return '行政處分／事實行為辨識'
 return '其他行政處分制度'
c['grp']=c.apply(grp,axis=1)

quotas=[('行政處分／事實行為辨識',30),('附款辨識與合法性',25),('效力與瑕疵',20),('撤銷廢止與信賴保護',15),('其他行政處分制度',10)]
sel=[];used=set()
for g,n in quotas:
 gdf=c[c.grp==g].sort_values(['situational','score','year_roc'],ascending=[False,False,False])
 for _,r in gdf.head(n).iterrows():sel.append(r);used.add(r.sig)
for _,r in c.sort_values(['situational','score','year_roc'],ascending=[False,False,False]).iterrows():
 if len(sel)>=100:break
 if r.sig not in used:sel.append(r);used.add(r.sig)
if len(sel)<100:raise RuntimeError(f'Only {len(sel)} relevant originals')
sel=sel[:100]

def law(r):
 q=S(r.get('question')); a=S(r.get('answer')).strip().upper();o=[S(r.get(x)) for x in 'ABCD'];f=o['ABCD'.index(a)] if a in 'ABCD' else '';z=q+' '+f
 if '附款' in z or any(k in z for k in ['保留行政處分之廢止權','停止條件','解除條件','負擔']):return '第93條、第94條','附款須先辨識期限、條件、負擔、保留廢止權或保留事後附加／變更負擔，再檢驗是否具法定容許性及與行政處分目的之正當合理關聯。'
 if '無效' in z or '重大明顯' in z or '自始不生效力' in z:return '第111條、第110條','行政處分原則自送達或通知發生效力；具有第111條所列或其他重大明顯瑕疵者無效，並自始不生效力。'
 if '行政處分之效力' in z or '行政處分效力' in z or '發生效力' in z or '效力繼續存在' in z:return '第110條','行政處分自送達、通知或使相對人知悉時起發生效力；在未經撤銷、廢止或因其他事由失效前，其效力原則上繼續存在。'
 if any(k in z for k in ['誤寫','誤算','顯然錯誤']):return '第101條','行政處分如有誤寫、誤算或其他類此之顯然錯誤，處分機關得隨時更正，並應通知相對人及已知利害關係人。'
 if '救濟期間' in z or '救濟方法' in z:return '第98條','行政處分之救濟教示錯誤或未教示，依第98條處理其救濟期間效果。'
 if any(k in z for k in ['不記明理由','記明理由','主旨、事實、理由']):return '第96條、第97條','書面行政處分原則應記載主旨、事實、理由及救濟教示；第97條另列得不記明理由之例外。'
 if '補正' in z or '轉換' in z:return '第114條至第116條','程序或方式瑕疵是否得補正、以及違法行政處分能否轉換，須依第114條至第116條分別判斷。'
 if '事實行為' in z:return '第92條','行政處分須是行政機關就公法上具體事件所為、對外直接發生法律效果之單方行政行為；欠缺法律效果者通常屬事實行為。'
 if '一般處分' in z:return '第92條第2項','相對人雖依一般性特徵可得確定，或涉及公物設定、變更、廢止或一般使用者，仍可能構成一般處分。'
 if any(k in z for k in ['信賴保護','信賴不值得','職權撤銷']):return '第117條至第121條','違法行政處分之職權撤銷受信賴保護、補償及撤銷權期間等規範限制。'
 if '廢止' in z:return '第122條至第126條','合法行政處分之廢止，須區分是否授益處分，並依第122條至第126條判斷事由、期間與補償。'
 if '程序再開' in z or '新事實' in z or '新證據' in z:return '第128條、第129條','法定救濟期間經過後，具法定事由者得申請程序再開，並受三個月及五年期間限制。'
 if '行政處分' in z:return '第92條','判斷行政處分時，重點是行政機關、公權力、公法事件、具體事件、對外直接法律效果與單方性等要素。'
 return '第92條至第134條','本題依行政程序法行政處分章之成立、附款、效力、瑕疵、撤銷廢止及程序再開等規定判斷。'

qs=[]
for i,r in enumerate(sel,1):
 a=S(r.get('answer')).strip().upper()
 if a not in 'ABCD':raise RuntimeError('bad answer')
 b,e=law(r)
 qs.append({'id':i,'question':S(r.get('question')),'options':[S(r.get(x)) for x in 'ABCD'],'answer':a,'topic':grp(r),'basis':b,'explanation':e,'source':f"{int(r.get('year_roc'))}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",'source_papers':S(r.get('source_papers')),'year_roc':int(r.get('year_roc')),'situational':bool(r.get('situational'))})
assert len(qs)==100 and len({q['question']+'|'.join(q['options']) for q in qs})==100
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'count':100,'groups':dict(Counter(q['topic'] for q in qs)),'situational_count':sum(q['situational'] for q in qs),'years':dict(Counter(q['year_roc'] for q in qs)),'original_questions_unedited':True,'source_required':True,'legal_basis_uses_question_and_correct_option':True}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
