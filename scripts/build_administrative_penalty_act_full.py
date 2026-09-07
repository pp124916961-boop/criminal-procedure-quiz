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
STRONG=['行政罰法','行政罰','違反行政法上義務','裁處罰鍰','罰鍰','裁處權','沒入','追繳','追徵','扣留','裁罰性不利處分','裁罰性之不利處分','緩起訴','一行為違反','數行為違反']

def article(r):
    q=S(r.get('question')); a=ans_text(r); z=q+' '+a
    # An article number expressly named in the stem controls the legal-basis label.
    m=re.search(r'行政罰法第\s*(\d+)\s*條',q)
    if m:
        n=int(m.group(1))
        if 1<=n<=46:return n
    # Procedure §§33-44.
    if '聽證' in z and any(k in z for k in ['申請','裁處','裁罰性','不包括','第2條','第二條']):return 43
    if '陳述意見' in z:return 42
    if '扣留' in z and any(k in z for k in ['聲明異議','直接上級機關','逕行提起行政訴訟']):return 41
    if '扣留' in z and any(k in z for k in ['發還','六個月','歸屬公庫']):return 40
    if '扣留' in z and any(k in z for k in ['封緘','看守','拍賣','變賣','毀棄','易生危險']):return 39
    if '扣留' in z and any(k in z for k in ['收據','作成紀錄','簽名','蓋章','按指印']):return 38
    if '扣留' in z and any(k in z for k in ['提出','交付','強制力']):return 37
    if '扣留' in z:return 36
    if any(k in z for k in ['當場陳述理由','表示異議']) and any(k in z for k in ['保全證據','查證身分','強制']):return 35
    if any(k in z for k in ['現行違反行政法上義務','即時制止','查證身分','隨同到指定處所','保全證據']):return 34
    if any(k in z for k in ['執行職務之證明文件','足資辨別之標誌','告知其所違反之法規']):return 33
    # Concurrence, limitation and jurisdiction §§24-32.
    if '移送' in z and '司法機關' in z:return 32
    if '管轄' in z and any(k in z for k in ['處理在先','法定罰鍰額最高','共同上級機關','不能協議']):return 31
    if '管轄' in z and '故意共同' in z:return 30
    if '管轄' in z and any(k in z for k in ['行為地','結果地','住所','居所','營業所','船艦本籍地','最初停泊地','最初降落地','行為人所在地']):return 29
    if '裁處權時效' in z and any(k in z for k in ['停止','天災','事變','不能開始','不能進行']):return 28
    if '裁處權時效' in z or ('三年' in z and '裁處' in z):return 27
    if any(k in z for k in ['緩起訴','緩刑','不起訴處分','免刑','無罪','免訴','不受理','義務勞務','刑事法律']) and ('行政' in z or '罰鍰' in z):return 26
    if '數行為' in z:return 25
    if '一行為' in z and any(k in z for k in ['數個行政法上義務','從一重','罰鍰','沒入','拘留']):return 24
    # Discretion, benefits and confiscation §§14-23.
    if any(k in z for k in ['追徵','不能執行沒入','減損之差額']) or ('沒入其物之價額' in z):return 23
    if any(k in a for k in ['所有人之故意或重大過失','規避沒入','不知該物得沒入']) or ('不屬於受處罰者所有' in z and '所有人' in z):return 22
    if '沒入' in z and any(k in z for k in ['受處罰者所有','屬於受處罰者','以屬於']):return 21
    if '追繳' in z or ('財產上利益' in z and '未受處罰' in z):return 20
    if any(k in z for k in ['三千元','3000元','免予處罰','糾正或勸導']):return 19
    if any(k in z for k in ['應受責難程度','所生影響','所得利益','所得之利益','受處罰者之資力','法定罰鍰最高額之二分之一','法定罰鍰最高額之三分之一']):return 18
    if ('中央或地方機關' in z or '公法組織' in z) and '處罰' in z:return 17
    if '非法人團體' in z and ('準用' in z or '第十五條' in z):return 16
    if any(k in z for k in ['私法人','董事','其他有代表權之人','未盡其防止義務','一百萬元','100萬元']):return 15
    if '故意共同' in z or '共同實施' in z:return 14
    # Responsibility §§7-13.
    if any(k in z for k in ['緊急避難','緊急危難','避難過當']):return 13
    if any(k in z for k in ['正當防衛','現在不法之侵害','防衛過當']):return 12
    if '職務命令' in z or '依法令之行為' in z:return 11
    if any(k in z for k in ['能防止而不防止','依法有防止之義務','發生違反行政法上義務事實之危險']):return 10
    if any(k in z for k in ['未滿十四歲','十四歲以上未滿十八歲','精神障礙','心智缺陷','辨識其行為違法']):return 9
    if '不知法規' in z:return 8
    if any(k in z for k in ['故意、過失','故意或過失','非出於故意或過失','推定為該等組織之故意']):return 7
    # General provisions §§1-6.
    if any(k in z for k in ['中華民國領域內','中華民國領域外','船艦','航空器']) and ('行政法上義務' in z or '行政罰' in z):return 6
    if any(k in z for k in ['裁處時之法律','最有利於受處罰者','行為後法律','自治條例有變更']):return 5
    if any(k in z for k in ['行為時之法律','處罰法定','明文規定者為限']) and ('行政' in z or '自治條例' in z):return 4
    if '行為人' in z and any(k in z for k in ['自然人','法人','非法人團體','中央或地方機關','其他組織']):return 3
    if any(k in z for k in ['其他種類行政罰','裁罰性之不利處分','裁罰性不利處分','限制或禁止行為之處分','剝奪或消滅資格','影響名譽之處分','警告性處分','講習','輔導教育','吊扣證照','吊銷證照']) and '行政罰' in z:return 2
    if '本法施行前' in z:return 45
    if '公布後一年施行' in z:return 46
    if '行政罰法' in q and any(k in z for k in ['特別規定','適用本法','罰鍰、沒入']):return 1
    return None

def group_for(n):
    if n is None:return ''
    if n<=13:return '法例與責任（§1～13）'
    if n<=23:return '共同違法與裁量、追繳沒入（§14～23）'
    if n<=32:return '一行為數行為、時效與管轄（§24～32）'
    return '裁處程序、扣留與附則（§33～46）'

def relevant(r):
    n=article(r); q=S(r.get('question')); z=focus(r)
    if n is None:return False
    if '行政罰法' in q:return True
    return sum(1 for k in STRONG if k in z)>=1

def score(r):
    q=S(r.get('question')); z=focus(r); n=0
    if '行政罰法' in q:n+=35
    elif '行政罰' in q:n+=18
    n+=sum(3 for k in STRONG if k in z)
    ex=S(r.get('exam_name'))
    if any(k in ex for k in PREF):n+=6
    if '警察' in ex or '升官' in ex:n+=5
    try:y=int(r.get('year_roc') or 0)
    except:y=0
    return n+max(0,y-90)*0.03

EXPL={
1:'違反行政法上義務而受罰鍰、沒入或其他種類行政罰，原則適用行政罰法；其他法律有特別規定者從其規定。',
2:'其他種類行政罰係第2條所列裁罰性不利處分，包括限制禁止、剝奪資格權利、影響名譽及警告性處分。',
3:'行政罰法所稱行為人，包括自然人、法人、設代表人或管理人之非法人團體、中央地方機關或其他組織。',
4:'違反行政法上義務之處罰，以行為時法律或自治條例有明文規定為限。',
5:'行為後法律或自治條例變更，原則適用裁處時法，但裁處前法規有利者適用最有利規定。',
6:'領域內違反行政法上義務適用本法；域外中華民國船艦航空器、可行使管轄區域及行為或結果一部在領域內者亦有規定。',
7:'違反行政法上義務非出於故意或過失者不罰；法人或組織之故意過失依代表人、職員等之故意過失推定。',
8:'不得因不知法規而免除行政處罰責任，但按情節得減輕或免除。',
9:'未滿14歲不罰；14至未滿18歲得減輕；精神障礙或心智缺陷影響辨識或控制能力者依程度不罰或得減輕。',
10:'依法有防止義務而能防止不防止者，與積極行為同；自行造成違反行政法上義務事實之危險者亦負防止義務。',
11:'依法令之行為不罰；依上級公務員職務命令之行為原則不罰，但明知命令違法而未依法陳述意見者例外。',
12:'對現在不法侵害出於防衛自己或他人權利之行為不罰；防衛過當得減輕或免除。',
13:'為避免自己或他人生命、身體、自由、名譽或財產之緊急危難而不得已之行為不罰；過當得減輕或免除。',
14:'故意共同實施違反行政法上義務者，依各自行為情節輕重分別處罰；身分或特定關係另依第14條處理。',
15:'私法人董事或有代表權之人於法定故意、重大過失或未盡防止義務情形，得與私法人併受同一規定罰鍰，並有一百萬元上限例外。',
16:'第15條私法人代表人等併同處罰規定，於設代表人或管理人之非法人團體或其他私法組織準用。',
17:'中央或地方機關或其他公法組織違反行政法上義務者，依各該法律或自治條例規定處罰。',
18:'裁處罰鍰應審酌責難程度、影響、所得利益，並得考量資力；利益超過法定最高額及減輕幅度另有特別規定。',
19:'法定最高額三千元以下罰鍰且情節輕微，認不處罰適當者得免予處罰，並得糾正或勸導。',
20:'行為人或他人因違反行政法上義務受有財產上利益而未受處罰者，得在利益價值範圍內酌予追繳。',
21:'得沒入之物原則以屬於受處罰者所有為限，但本法或其他法律另有規定者除外。',
22:'第三人所有之物因所有人故意或重大過失成為違法工具，或明知可沒入而為規避沒入取得所有權者，仍得沒入。',
23:'得沒入物在裁處前不能沒入時得裁處沒入價額；裁處後不能執行沒入時得追徵價額或價值減損差額。',
24:'一行為違反數個行政法上義務而應處罰鍰，原則依法定罰鍰額最高規定裁處；其他種類行政罰、沒入及社維法拘留另依第24條處理。',
25:'數行為違反同一或不同行政法上義務者，分別處罰。',
26:'一行為同時觸犯刑事法律與行政法義務原則依刑事法律處罰；不起訴、緩起訴或特定裁判確定後得再裁行政罰，並有金額或勞務扣抵規定。',
27:'行政罰裁處權原則因三年經過而消滅，並依行為終了、結果發生或特定司法程序確定等時點起算。',
28:'裁處權時效遇天災、事變或依法不能開始或進行裁處時停止，原因消滅翌日起與先前期間合併計算。',
29:'行政罰管轄原則依行為地、結果地、住所居所或營業事務所在地；域外船艦航空器另有特別管轄規則。',
30:'故意共同實施違反行政法上義務行為而分屬不同管轄區時，各相關行為地或行為人所在地主管機關均有管轄權。',
31:'一行為涉及數機關管轄時，依處理在先、協議／共同上級指定或法定罰鍰額最高等規則定管轄。',
32:'一行為同時觸犯刑事法律及違反行政法上義務時，涉及刑事部分應移送司法機關，後續法定裁判或處分結果並應通知行政機關。',
33:'行政機關執行職務人員應出示證明文件或顯示足資辨別之標誌，並告知所違反法規。',
34:'對現行違反行政法上義務之行為人，行政機關得即時制止、製作紀錄、保全證據及確認身分；強制措施須符合必要性。',
35:'對強制排除抗拒保全證據或強制到指定處所查證身分不服，得當場陳述理由表示異議。',
36:'得沒入或可為證據之物得扣留；證據物之扣留範圍及期間以保全證據所必要者為限。',
37:'對應扣留物得要求提出或交付；無正當理由拒絕或抗拒者，得以強制力扣留。',
38:'扣留應作成紀錄；所有人、持有人或保管人在場或請求時，應製作收據交付。',
39:'扣留物應適當封緘或標識保管；不便保管者得交人看守，得沒入物可拍賣變賣，易生危險者得毀棄。',
40:'扣留物無留存必要或不予處罰、未沒入時原則應發還；不能發還時公告滿六個月無人申請，歸屬公庫。',
41:'對扣留不服者得向扣留機關聲明異議；無理由時送直接上級機關決定，後續救濟依第41條處理。',
42:'行政機關於裁處前原則應給予受處罰者陳述意見機會；第42條但書列有例外。',
43:'對第2條第1款、第2款之裁罰性不利處分，原則上應依受處罰者申請舉行聽證，但有法定例外。',
44:'行政機關裁處行政罰時，應作成裁處書並送達。',
45:'本法施行前違反行政法上義務而未裁處者，於施行後裁處之適用範圍及時效，依第45條過渡規定處理。',
46:'行政罰法自公布後一年施行；修正條文自公布日施行。'
}

df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()
df['article']=df.apply(article,axis=1); df['group']=df.article.apply(group_for); df['relevant']=df.apply(relevant,axis=1); df['score']=df.apply(score,axis=1)
c=df[(df.relevant) & (df.group!='')].copy()
c['sig']=c.apply(lambda r:sig(S(r.get('question')),[S(r.get(x)) for x in 'ABCD']),axis=1)
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

targets=[('法例與責任（§1～13）',25),('共同違法與裁量、追繳沒入（§14～23）',25),('一行為數行為、時效與管轄（§24～32）',25),('裁處程序、扣留與附則（§33～46）',25)]
sel=[]; used=set()
for g,n in targets:
    for _,r in c[c.group==g].head(n).iterrows():sel.append(r);used.add(r.sig)
for _,r in c.iterrows():
    if len(sel)>=100:break
    if r.sig not in used:sel.append(r);used.add(r.sig)
if len(sel)<100:raise RuntimeError(f'Only {len(sel)} unique relevant original Administrative Penalty Act questions found')
sel=sel[:100]

qs=[]
for i,r in enumerate(sel,1):
    a=S(r.get('answer')).strip().upper()
    if a not in 'ABCD':raise RuntimeError(f'bad answer {i}')
    opts=[S(r.get(x)) for x in 'ABCD']; n=int(r['article'])
    qs.append({'id':i,'question':S(r.get('question')),'options':opts,'answer':a,'topic':group_for(n),'basis':f'第{n}條','explanation':EXPL.get(n,'依現行行政罰法規定判斷。'),'source':f"{int(r.get('year_roc'))}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",'source_papers':S(r.get('source_papers')),'year_roc':int(r.get('year_roc'))})

assert len(qs)==100
assert len({sig(q['question'],q['options']) for q in qs})==100
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'count':100,'scope':'行政罰法第1條至第46條（全法）','groups':dict(Counter(q['topic'] for q in qs)),'articles':dict(Counter(q['basis'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'original_questions_unedited':True,'source_required':True,'classification_uses_question_and_correct_option':True,'basis_detection':'explicit_article_or_stem_plus_correct_option','current_law_articles':46,'current_law_last_amended_roc':'111-06-15'}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
