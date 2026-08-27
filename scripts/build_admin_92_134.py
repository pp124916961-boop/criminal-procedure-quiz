from pathlib import Path
import json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('admin-procedure-92-134'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)
df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()

def S(x): return '' if x is None else str(x)
def T(r): return ' '.join(S(r.get(c)) for c in ['question','A','B','C','D'])
PREF=['警察','一般警察','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路']
KW=['行政處分','一般處分','附款','期限','條件','負擔','救濟期間','顯然錯誤','陳述意見','聽證','行政處分之效力','行政處分.*無效','重大明顯','程序補正','行政處分.*轉換','違法行政處分','職權撤銷','信賴保護','信賴不值得保護','合法行政處分','行政處分.*廢止','程序再開','新事實','新證據','公法上.*請求權','時效.*中斷']

def score(r):
 t=T(r); q=S(r.get('question')); n=sum(10 for k in KW if re.search(k,t))
 if '行政處分' in q:n+=16
 if '行政程序法' in t:n+=5
 if any(k in S(r.get('exam_name')) for k in PREF):n+=3
 if any(k in q for k in ['行政契約','行政指導','法規命令','行政規則','行政計畫']) and '行政處分' not in q:n-=12
 return n+max(0,int(r.get('year_roc') or 0)-100)*.06

df['score']=df.apply(score,axis=1)
c=df[df.score>=10].copy(); c['sig']=c[['question','A','B','C','D']].astype(str).agg('|'.join,axis=1)
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

def grp(r):
 t=T(r)
 if any(k in t for k in ['程序再開','新事實','新證據','再審事由','公法上請求權','重行起算','時效中斷','中斷之時效']):return '程序再開與時效'
 if any(k in t for k in ['職權撤銷','違法行政處分','信賴保護','信賴不值得','授予利益之合法','非授予利益之合法','廢止']):return '撤銷廢止與信賴保護'
 if any(k in t for k in ['行政處分之無效','重大明顯','補正','轉換','專屬管轄','事務權限','自始不生效力']):return '效力與瑕疵'
 if '陳述意見' in t or '聽證' in t:return '陳述意見與聽證'
 return '成立與附款'
c['grp']=c.apply(grp,axis=1)

sel=[];used=set()
for g,n in [('成立與附款',25),('陳述意見與聽證',15),('效力與瑕疵',25),('撤銷廢止與信賴保護',25),('程序再開與時效',10)]:
 for _,r in c[c.grp==g].head(n).iterrows():sel.append(r);used.add(r.sig)
for _,r in c.iterrows():
 if len(sel)>=100:break
 if r.sig not in used:sel.append(r);used.add(r.sig)
if len(sel)<100:raise RuntimeError(f'Only {len(sel)} unique relevant original questions found')
sel=sel[:100]

def law(r):
 t=T(r); a=S(r.get('answer')).strip().upper(); o=[S(r.get(x)) for x in 'ABCD']; f=o['ABCD'.index(a)] if a in 'ABCD' else ''; z=t+' '+f
 rules=[
 (134,['原有時效期間不滿五年','重行起算之時效期間為五年']),
 (133,['重行起算']), (132,['視為不中斷']), (131,['公法上之請求權','公法上請求權']),
 (130,['證書或物品','註銷之標示']), (129,['申請為有理由','申請為無理由','原處分為正當']),
 (128,['程序再開','重新開始程序','新事實','新證據','再審事由']),
 (127,['返還因該處分所受領','不當得利','一次或連續之金錢']),
 (126,['第一百二十三條第四款','第一百二十三條第五款']), (125,['自廢止時','溯及既往失其效力']),
 (124,['廢止原因發生後二年']), (123,['授予利益之合法行政處分']), (122,['非授予利益之合法行政處分']),
 (121,['知有撤銷原因','撤銷權']), (120,['財產上之損失','補償額度']), (119,['信賴不值得保護','詐欺','脅迫','賄賂','不正確資料','重大過失而不知']),
 (118,['違法行政處分經撤銷後','溯及既往']), (117,['職權撤銷','違法行政處分']),
 (116,['轉換','羈束處分不得轉換']), (115,['土地管轄','相同之處分']), (114,['補正','事後記明','事後給予']),
 (113,['確認行政處分無效','請求確認']), (112,['一部分無效','部分無效']), (111,['重大明顯','不能實現','構成犯罪','公共秩序','善良風俗','專屬管轄','缺乏事務權限']),
 (110,['自送達','自公告日','效力繼續存在','自始不生效力']),
 (109,['免除訴願','先行程序']), (108,['斟酌全部聽證結果','依聽證紀錄']), (107,['舉行聽證']),
 (106,['言詞','陳述意見']), (105,['陳述書','視為放棄']), (104,['書面通知','原因事實及法規依據']), (103,['得不給予陳述意見','大量作成','情況急迫','行政強制執行']), (102,['陳述意見']),
 (101,['誤寫','誤算','顯然錯誤']), (100,['應送達相對人','一般處分之送達']), (99,['無管轄權之機關','十日內移送']), (98,['救濟期間有錯誤','未告知救濟期間']),
 (97,['得不記明理由','無須說明理由']), (96,['主旨、事實、理由','救濟方法']), (95,['書面、言詞或其他方式','要求作成書面']),
 (94,['正當合理之關聯','不得違背行政處分之目的']), (93,['附款','期限','條件','負擔']), (92,['一般處分','公物','行政處分'])]
 for art,keys in rules:
  if any(k in z for k in keys):return f'第{art}條',f'本題核心依行政程序法第{art}條判斷；作答時應依現行條文檢驗題目所述要件、程序或法律效果。'
 return '第92條至第134條','本題屬行政處分章，依行政程序法第92條至第134條之成立、程序、效力、撤銷廢止、程序再開或時效規定判斷。'

qs=[]
for i,r in enumerate(sel,1):
 a=S(r.get('answer')).strip().upper()
 if a not in 'ABCD':raise RuntimeError('bad answer')
 b,e=law(r)
 qs.append({'id':i,'question':S(r.get('question')),'options':[S(r.get(x)) for x in 'ABCD'],'answer':a,'topic':grp(r),'basis':b,'explanation':e,'source':f"{int(r.get('year_roc'))}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",'source_papers':S(r.get('source_papers')),'year_roc':int(r.get('year_roc'))})
assert len(qs)==100 and len({q['question']+'|'.join(q['options']) for q in qs})==100
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'count':100,'groups':dict(Counter(q['topic'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'basis':dict(Counter(q['basis'] for q in qs)),'original_questions_unedited':True,'source_required':True}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
