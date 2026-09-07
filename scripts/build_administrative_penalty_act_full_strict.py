from pathlib import Path
import json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('administrative-penalty-act-full'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)

def S(x): return '' if x is None else str(x)
def norm(s): return re.sub(r'\s+','',S(s))
def sig(q,opts): return norm(q)+'|'+'|'.join(norm(x) for x in opts)
def ans_text(r):
    a=S(r.get('answer')).strip().upper()
    return S(r.get(a)) if a in 'ABCD' else ''
def focus(r): return S(r.get('question'))+' '+ans_text(r)

PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路','警大','警佐']
OTHER_LAW_ONLY=['行政執行法','行政執行時','刑事訴訟法','社會秩序維護法','警察職權行使法']

def article(r):
    q=S(r.get('question')); a=ans_text(r); z=q+' '+a
    m=re.search(r'行政罰法第\s*(\d+)\s*條',q)
    if m:
        n=int(m.group(1))
        if 1<=n<=46:return n
    # Procedure: remedies before generic powers.
    if '扣留' in z and any(k in z for k in ['單獨對扣留','逕行提起行政訴訟','不得對裁處案件之實體決定聲明不服','直接上級機關','聲明異議']):return 41
    if ('指定處所' in z or '查證身分' in z or '強制排除抗拒保全證據' in z) and '不服' in z and any(k in z for k in ['異議','法院','陳述理由','不得表示不服']):return 35
    if any(k in z for k in ['當場陳述理由','表示異議']) and any(k in z for k in ['保全證據','查證身分','強制']):return 35
    if '聽證' in z and any(k in z for k in ['申請','裁處','裁罰性','不包括','第2條','第二條']):return 43
    if '陳述意見' in z:return 42
    if '裁處書' in z:return 44
    if '扣留' in z and any(k in z for k in ['發還','六個月','歸屬公庫']):return 40
    if '扣留' in z and any(k in z for k in ['封緘','看守','拍賣','變賣','毀棄','易生危險']):return 39
    if '扣留' in z and any(k in z for k in ['收據','作成紀錄','簽名','蓋章','按指印']):return 38
    if '扣留' in z and any(k in z for k in ['提出','交付','強制力','拒絕提出']):return 37
    if '扣留' in z:return 36
    if any(k in z for k in ['現行違反行政法上義務','即時制止','查證身分','隨同到指定處所','保全證據']):return 34
    if any(k in z for k in ['執行職務之證明文件','足資辨別之標誌','告知其所違反之法規']):return 33
    # Concurrence / limitation / jurisdiction.
    if '移送' in z and '司法機關' in z:return 32
    if '管轄' in z and any(k in z for k in ['處理在先','法定罰鍰額最高','共同上級機關','不能協議']):return 31
    if '管轄' in z and '故意共同' in z:return 30
    if '管轄' in z and any(k in z for k in ['行為地','結果地','住所','居所','營業所','船艦本籍地','最初停泊地','最初降落地','行為人所在地']):return 29
    if '裁處權時效' in z and any(k in z for k in ['停止','天災','事變','不能開始','不能進行']):return 28
    if '裁處權時效' in z or ('三年' in z and '裁處' in z):return 27
    if any(k in z for k in ['緩起訴','緩刑','不起訴處分','免刑','無罪','免訴','不受理','義務勞務','刑事法律']) and ('行政' in z or '罰鍰' in z):return 26
    if '數行為' in z:return 25
    if '一行為' in z and any(k in z for k in ['數個行政法上義務','從一重','法定罰鍰額','沒入','拘留']):return 24
    # §§14-23.
    if any(k in z for k in ['追徵','不能執行沒入','減損之差額','沒入其物之價額']):return 23
    if ('不屬於受處罰者所有' in z and '所有人' in z) or any(k in z for k in ['故意或重大過失，致使該物','規避沒入']):return 22
    if '沒入' in z and any(k in z for k in ['受處罰者所有','屬於受處罰者','以屬於']):return 21
    if '追繳' in z or ('財產上利益' in z and '未受處罰' in z):return 20
    if any(k in z for k in ['三千元','3000元','免予處罰','糾正或勸導']):return 19
    if any(k in z for k in ['應受責難程度','所生影響','所得利益','所得之利益','受處罰者之資力','二分之一','三分之一']):return 18
    if ('中央或地方機關' in z or '公法組織' in z) and '處罰' in z:return 17
    if '非法人團體' in z and ('準用' in z or '第十五條' in z):return 16
    if any(k in z for k in ['私法人','董事','其他有代表權之人','未盡其防止義務','一百萬元','100萬元']):return 15
    if '故意共同' in z or '共同實施' in z:return 14
    # §§7-13.
    if any(k in z for k in ['緊急避難','緊急危難','避難過當']):return 13
    if any(k in z for k in ['正當防衛','現在不法之侵害','防衛過當']):return 12
    if '職務命令' in z or '依法令之行為' in z:return 11
    if any(k in z for k in ['能防止而不防止','依法有防止之義務','發生違反行政法上義務事實之危險']):return 10
    if any(k in z for k in ['未滿十四歲','十四歲以上未滿十八歲','精神障礙','心智缺陷','辨識其行為違法']):return 9
    if '不知法規' in z:return 8
    if any(k in z for k in ['故意、過失','故意或過失','非出於故意或過失','推定為該等組織之故意']):return 7
    # §§1-6.
    if any(k in z for k in ['中華民國領域內','中華民國領域外','船艦','航空器']) and ('行政法上義務' in z or '行政罰' in z):return 6
    if any(k in z for k in ['裁處時之法律','最有利於受處罰者','行為後法律','自治條例有變更']):return 5
    if any(k in z for k in ['行為時之法律','處罰法定','明文規定者為限']) and ('行政' in z or '自治條例' in z):return 4
    if '行為人' in z and any(k in z for k in ['自然人','法人','非法人團體','中央或地方機關','其他組織']):return 3
    if any(k in z for k in ['其他種類行政罰','裁罰性之不利處分','裁罰性不利處分','限制或禁止行為之處分','剝奪或消滅資格','影響名譽之處分','警告性處分','講習','輔導教育','吊扣證照','吊銷證照']) and '行政罰' in z:return 2
    if '本法施行前' in z:return 45
    if '行政罰法' in q and any(k in z for k in ['特別規定','適用本法','罰鍰、沒入']):return 1
    return None

def group_for(n):
    if n is None:return ''
    if n<=13:return '法例與責任（§1～13）'
    if n<=23:return '共同違法與裁量、追繳沒入（§14～23）'
    if n<=32:return '一行為數行為、時效與管轄（§24～32）'
    return '裁處程序、扣留與附則（§33～46）'

def strict_relevant(r):
    q=S(r.get('question'))
    # Explicit Administrative Penalty Act questions are always eligible even if the fact pattern cites another special statute.
    if '行政罰法' in q:return article(r) is not None
    # Otherwise require the question itself to be explicitly about administrative penalties, and reject other-law-only questions.
    if '行政罰' not in q:return False
    if any(k in q for k in OTHER_LAW_ONLY):return False
    return article(r) is not None

def score(r):
    q=S(r.get('question')); ex=S(r.get('exam_name')); n=0
    if '行政罰法' in q:n+=50
    elif '行政罰' in q:n+=25
    if any(k in ex for k in PREF):n+=8
    if '警察' in ex or '升官' in ex:n+=6
    try:y=int(r.get('year_roc') or 0)
    except:y=0
    return n+max(0,y-90)*0.03

EXPL={
2:'其他種類行政罰係第2條所列裁罰性不利處分，包括限制禁止、剝奪資格權利、影響名譽及警告性處分。',
3:'行政罰法所稱行為人，包括自然人、法人、非法人團體、中央地方機關或其他組織。',
4:'違反行政法上義務之處罰，以行為時法律或自治條例有明文規定為限。',
5:'行為後法律或自治條例變更，原則適用裁處時法，但裁處前法規有利者適用最有利規定。',
6:'行政罰法之地域效力包括領域內行為及法定域外船艦、航空器等情形。',
7:'違反行政法上義務非出於故意或過失者不罰。',
8:'不得因不知法規而免責，但按情節得減輕或免除處罰。',
9:'未滿14歲不罰；14至未滿18歲得減輕；精神障礙或心智缺陷另依辨識控制能力處理。',
10:'依法有防止義務而能防止不防止者，與積極行為同。',
11:'依法令或法定職務命令之行為依第11條判斷是否不罰。',
12:'正當防衛不罰；防衛過當得減輕或免除。',
13:'緊急避難符合要件者不罰；避難過當得減輕或免除。',
14:'故意共同實施違反行政法上義務者，依各自行為情節輕重分別處罰。',
15:'私法人董事或有代表權之人於法定故意、重大過失或未盡防止義務情形，得併受罰鍰。',
16:'第15條關於私法人之規定，於設代表人或管理人之非法人團體或其他私法組織準用。',
17:'中央或地方機關或其他公法組織違反行政法上義務者，依法律或自治條例規定處罰。',
18:'裁處罰鍰應審酌責難程度、影響、所得利益，並得考量資力；加重或減輕幅度另依法定規則。',
19:'法定最高額三千元以下罰鍰且情節輕微，認不處罰適當者得免予處罰，並得糾正或勸導。',
20:'因違反行政法上義務受有財產上利益而未受處罰者，得在利益價值範圍內酌予追繳。',
21:'得沒入之物原則以屬於受處罰者所有為限，但法律另有規定者除外。',
22:'第三人所有物因所有人故意或重大過失成為違法工具，或規避沒入取得所有權者，得沒入。',
23:'得沒入物不能裁處或不能執行沒入時，得依法裁處或追徵價額。',
24:'一行為違反數個行政法上義務應處罰鍰時，原則依法定罰鍰額最高者裁處；沒入等另有規定。',
25:'數行為違反同一或不同行政法上義務者，分別處罰。',
26:'一行為同時觸犯刑事法律與行政法義務，依第26條處理刑事處罰、行政罰及扣抵。',
27:'行政罰裁處權原則因三年經過而消滅，起算點依第27條判斷。',
28:'裁處權時效遇法定不能開始或進行情形時停止。',
29:'行政罰管轄原則依行為地、結果地、住所居所或營業事務所在地等判斷。',
30:'故意共同實施違法而分屬不同管轄區時，依第30條決定各主管機關管轄。',
31:'一行為涉及數機關管轄時，依處理在先、協議、指定或法定罰鍰額最高等規則決定。',
32:'同時涉及刑事部分時，依第32條移送司法機關並辦理後續通知。',
33:'執行行政罰職務時應出示證明或標誌，並告知違反法規。',
34:'對現行違反行政法上義務之行為人，得即時制止、製作紀錄、保全證據及確認身分。',
35:'對強制排除抗拒保全證據或強制到指定處所查證身分不服，得當場陳述理由表示異議。',
36:'得沒入或可為證據之物得扣留；證據物扣留以保全證據必要範圍及期間為限。',
37:'對應扣留物得要求提出或交付；無正當理由拒絕或抗拒者，得以強制力扣留。',
38:'扣留應作成紀錄；法定情形並應製作收據交付。',
39:'扣留物之封緘、看守、拍賣變賣及危險物毀棄，依第39條處理。',
40:'扣留物無留存必要或不予處罰、未沒入時原則應發還；不能發還者依公告等規定處理。',
41:'對扣留不服得聲明異議；依法不得對實體裁處聲明不服者，得單獨對扣留逕行提起行政訴訟。',
42:'行政機關於裁處前原則應給予受處罰者陳述意見機會，但有法定例外。',
43:'對第2條第1款、第2款之裁罰性不利處分，原則上應依受處罰者申請舉行聽證。',
44:'行政機關裁處行政罰時，應作成裁處書並送達。',
45:'本法施行前違反行政法上義務而未裁處者，依第45條過渡規定處理。'
}

df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()
df['article']=df.apply(article,axis=1); df['group']=df.article.apply(group_for); df['eligible']=df.apply(strict_relevant,axis=1); df['score']=df.apply(score,axis=1)
c=df[(df.eligible)&(df.group!='')].copy()
c['sig']=c.apply(lambda r:sig(S(r.get('question')),[S(r.get(x)) for x in 'ABCD']),axis=1)
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

targets=[('法例與責任（§1～13）',25),('共同違法與裁量、追繳沒入（§14～23）',25),('一行為數行為、時效與管轄（§24～32）',25),('裁處程序、扣留與附則（§33～46）',25)]
sel=[];used=set()
for g,n in targets:
    rows=c[c.group==g]
    if len(rows)<n:raise RuntimeError(f'Strict original-question pool for {g} has only {len(rows)}, need {n}')
    for _,r in rows.head(n).iterrows():sel.append(r);used.add(r.sig)
assert len(sel)==100

qs=[]
for i,r in enumerate(sel,1):
    a=S(r.get('answer')).strip().upper(); assert a in 'ABCD'
    opts=[S(r.get(x)) for x in 'ABCD']; n=int(r['article'])
    qs.append({'id':i,'question':S(r.get('question')),'options':opts,'answer':a,'topic':group_for(n),'basis':f'第{n}條','explanation':EXPL.get(n,f'依行政罰法第{n}條規定判斷。'),'source':f"{int(r.get('year_roc'))}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",'source_papers':S(r.get('source_papers')),'year_roc':int(r.get('year_roc'))})

assert len(qs)==100 and len({sig(q['question'],q['options']) for q in qs})==100
assert all(('行政罰法' in q['question'] or '行政罰' in q['question']) for q in qs)
assert not any(('行政罰法' not in q['question'] and any(k in q['question'] for k in OTHER_LAW_ONLY)) for q in qs)
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'count':100,'scope':'行政罰法第1條至第46條（全法）','groups':dict(Counter(q['topic'] for q in qs)),'articles':dict(Counter(q['basis'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'original_questions_unedited':True,'source_required':True,'strict_scope_filter':True,'other_law_only_questions':0,'classification_uses_question_and_correct_option':True,'current_law_articles':46,'current_law_last_amended_roc':'111-06-15'}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
