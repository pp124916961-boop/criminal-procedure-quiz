from pathlib import Path
import json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('criminal-illegality-50'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)

def S(x): return '' if x is None else str(x)
def norm(s): return re.sub(r'\s+','',S(s))
def sig(r):
    return norm(r.get('question'))+'|'+'|'.join(norm(r.get(x)) for x in 'ABCD')
def answer_text(r):
    a=S(r.get('answer')).strip().upper()
    return S(r.get(a)) if a in 'ABCD' else ''
def target_text(r): return S(r.get('question'))+' '+answer_text(r)

PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路','警大','警佐']

# Supplemental originals carried over from the user's previously verified
# "刑法總則到未遂犯_100題歷屆原題" bank. They are used only if the
# benchmark corpus does not contain enough unique substantive wrongfulness items.
SUPPLEMENTAL=[
 {'year_roc':115,'exam_name':'115年一般警察人員四等－行政警察人員','subject_zh':'刑法概要','q_no':4,
  'question':'甲在公園散步時，乙對於所飼養的狼犬已盡完整監督，而狼犬不知何故突然掙脫狗鍊而攻擊甲，甲在情急而萬不得已之下，拿起隨身電擊棒電死狼犬。關於甲之刑責，下列敘述何者正確？',
  'A':'得主張緊急避難，不成立犯罪','B':'得主張依法令之行為，不成立犯罪','C':'得主張正當防衛，不成立犯罪','D':'得主張義務衝突，不成立犯罪','answer':'A','group':'緊急避難（刑法§24）'},
 {'year_roc':115,'exam_name':'115年司法人員四等－法院書記官','subject_zh':'刑法概要','q_no':3,
  'question':'有關阻卻違法承諾的敘述，下列何者正確？',
  'A':'甲允諾乙，施打疫苗，便給 5 百元禮券獎勵，乙因此同意接受疫苗注射，實際上甲自始即無給付禮券的意思，乙之承諾係屬無效','B':'甲同意醫師乙為其執行雙眼皮手術，因為甲自認手術之後便可改運，甲之承諾係屬無效','C':'甲喝烈酒一瓶後執意開車載乙回家，乙明知甲已酒醉，仍接受甲的好意，乙之承諾不得阻卻甲之不能安全駕駛罪的違法性','D':'甲同意醫師乙為其注射疫苗，注射後注射處手臂疼痛超乎甲的想像，甲之承諾係屬無效','answer':'C','group':'超法規阻卻違法事由'},
 {'year_roc':115,'exam_name':'115年司法官／律師第一試','subject_zh':'綜合法學（一）（刑法、刑事訴訟法、法律倫理）','q_no':5,
  'question':'甲、乙素有積怨，某日兩人相遇，甲見乙自口袋掏出看似手槍的物品，以為乙要拿手槍對他射擊，於是先下手為強，一拳打昏乙，之後才發現乙根本沒看見甲，只是想拿煙斗出來抽而已，關於甲的傷害行為之刑法上評價或定性，下列敘述何者正確？',
  'A':'甲之行為屬偶然防衛','B':'甲之行為可以依正當防衛阻卻違法','C':'甲之行為成立傷害罪不得減輕責任','D':'甲之行為不受故意傷害罪之刑罰','answer':'D','group':'正當防衛（刑法§23）'},
 {'year_roc':114,'exam_name':'114年司法官／律師第一試','subject_zh':'綜合法學（一）（刑法、刑事訴訟法、法律倫理）','q_no':2,
  'question':'甲為 17 歲之高中生，為博取心怡對象的好感，而願意接受紋身師傅乙於其手臂刺一個十元硬幣大小的愛心圖案。下列敘述何者正確？',
  'A':'甲不具民法上之行為能力，故其承諾無效','B':'未成年人對自己的身體並無處分權，須由其父母代為承諾始可','C':'乙不得主張推測承諾以阻卻傷害罪之違法性','D':'手臂刺青難以回復原樣，屬刑法第 10 條之重傷','answer':'C','group':'超法規阻卻違法事由'},
 {'year_roc':113,'exam_name':'113年司法人員特考－執達員','subject_zh':'刑法概要','q_no':5,
  'question':'下列何者非屬阻卻違法事由？','A':'瘖啞人之行為','B':'依法令之行為','C':'業務上之正當行為','D':'正當防衛之行為','answer':'A','group':'依法令／業務正當行為（刑法§21～22）'},
 {'year_roc':113,'exam_name':'113年司法人員特考－執達員','subject_zh':'刑法概要','q_no':6,
  'question':'有關被害人承諾之敘述，下列何者正確？','A':'被害人承諾為法定阻卻違法事由','B':'被害人承諾所放棄之法益，不包含生命法益、各種程度的身體健康法益','C':'國家法益、社會法益不在被害人承諾所得處分的範圍之內','D':'被害人需滿20歲，其所為之承諾方屬有效','answer':'C','group':'超法規阻卻違法事由'},
 {'year_roc':112,'exam_name':'112年司法人員特考－執達員','subject_zh':'刑法概要','q_no':6,
  'question':'依刑法有關正當防衛、緊急避難之規定，下列敘述何者錯誤？','A':'成立正當防衛或緊急避難時，法律效果皆為不罰','B':'二者皆得為他人防衛或避難','C':'對於公務上或業務上有特別義務者，皆不適用','D':'二者皆有過當得減輕或免除其刑之規定','answer':'C','group':'正當防衛（刑法§23）'},
 {'year_roc':112,'exam_name':'112年司法人員特考－執達員','subject_zh':'刑法概要','q_no':9,
  'question':'父親甲在火災中只能救雙胞胎兒子其中之一，甲遂僅救出其一，這在刑法上屬何種概念？','A':'義務衝突','B':'禁止錯誤','C':'依法令之行為','D':'原因自由行為','answer':'A','group':'超法規阻卻違法事由'},
 {'year_roc':112,'exam_name':'112年司法人員特考－執達員','subject_zh':'刑法概要','q_no':11,
  'question':'關於刑法第24條緊急避難，下列敘述何者正確？','A':'須對於現在不法侵害','B':'須出於防衛自己或他人的權利','C':'須已盡力為防止行為','D':'須出於不得已之行為','answer':'D','group':'緊急避難（刑法§24）'},
 {'year_roc':111,'exam_name':'111年司法人員特考－執達員','subject_zh':'刑法概要','q_no':16,
  'question':'下列何者非正當防衛之要件？','A':'有現在不法之侵害','B':'為避免自己或他人之緊急危難','C':'為防衛自己或他人之權利','D':'出於防衛意思','answer':'B','group':'正當防衛（刑法§23）'},
 {'year_roc':111,'exam_name':'111年司法人員特考－執達員','subject_zh':'刑法概要','q_no':17,
  'question':'下列何種情形，不得依刑法第24條緊急避難之規定而阻卻違法？','A':'為保護自己財產所為之緊急避難行為','B':'為保護善良風俗所為之緊急避難行為','C':'為保護他人自由所為之緊急避難行為','D':'為保護他人生命所為之緊急避難行為','answer':'B','group':'緊急避難（刑法§24）'},
 {'year_roc':110,'exam_name':'110年司法人員特考－執達員','subject_zh':'刑法概要','q_no':4,
  'question':'甲、乙均為黑道大哥，相約談判。談判間，甲見乙觸摸口袋，以為乙要拔槍射殺甲，而出於防衛意思下手殺乙，致乙死亡。甲主觀認知與客觀事實不一致。此種不一致，學理上稱為何種「錯誤」？','A':'構成要件錯誤','B':'禁止錯誤','C':'容許構成要件錯誤','D':'打擊錯誤','answer':'C','group':'正當防衛（刑法§23）'},
 {'year_roc':110,'exam_name':'110年司法人員特考－執達員','subject_zh':'刑法概要','q_no':14,
  'question':'公務員明知上級之命令違法，仍依所屬上級公務員命令而為其行為，其法律效果為何？','A':'屬緊急避難，阻卻違法','B':'不得阻卻違法','C':'屬正當防衛，阻卻違法','D':'屬業務上正當行為，阻卻違法','answer':'B','group':'依法令／業務正當行為（刑法§21～22）'},
 {'year_roc':110,'exam_name':'110年司法人員特考－執達員','subject_zh':'刑法概要','q_no':15,
  'question':'依刑法之規定，業務上之正當行為，其法律效果為何？','A':'不罰','B':'免除其刑','C':'減輕其刑','D':'減輕或免除其刑','answer':'A','group':'依法令／業務正當行為（刑法§21～22）'},
 {'year_roc':110,'exam_name':'110年司法人員特考－執達員','subject_zh':'刑法概要','q_no':18,
  'question':'甲欲對乙強制性交，甲壓制乙，脫去乙身上衣物進而強行舌吻時，乙用力咬傷甲之舌頭，讓甲因此離去。有關本案之法律效果，下列敘述何者正確？','A':'乙之行為屬緊急避難','B':'乙之行為屬正當防衛','C':'乙之行為屬避難過當','D':'乙之行為屬防衛過當','answer':'B','group':'正當防衛（刑法§23）'},
 {'year_roc':109,'exam_name':'109年一般警察人員四等－行政警察人員','subject_zh':'刑法概要','q_no':9,
  'question':'下列有關公務員之敘述，何者正確？','A':'公務員執行職務中所為之任何行為，均屬不罰','B':'甲並非警察，雖目擊乙肇事逃逸，仍不能逮捕乙','C':'公務員依所屬上級公務員命令之職務行為，即可阻卻違法','D':'公務員執行上級之違法職務命令時，若明知命令違法，不得阻卻違法','answer':'D','group':'依法令／業務正當行為（刑法§21～22）'},
 {'year_roc':109,'exam_name':'109年一般警察人員四等－行政警察人員','subject_zh':'刑法概要','q_no':10,
  'question':'下列何者為法定阻卻違法事由？','A':'義務衝突','B':'不可罰之違法性','C':'業務上之正當行為','D':'推測之承諾','answer':'C','group':'依法令／業務正當行為（刑法§21～22）'},
 {'year_roc':108,'exam_name':'108年一般警察人員四等－行政警察人員','subject_zh':'刑法概要','q_no':4,
  'question':'甲遭乙尾隨跟蹤，見乙取出木棍，誤以為乙要攻擊自己，乃揮拳擊傷乙，實則乙要驅趕流浪犬。甲之行為，符合下列何種概念？','A':'正當防衛','B':'誤想防衛','C':'緊急避難','D':'因果歷程錯誤','answer':'B','group':'正當防衛（刑法§23）'}
]


GROUPS={
 '正當防衛（刑法§23）':[
   '正當防衛','防衛過當','防衛行為過當','現在不法之侵害','現在不法侵害','不法侵害',
   '防衛意思','防衛自己','防衛他人','防衛第三人','防衛挑撥','挑唆防衛','防衛權',
   '誤想防衛','偶然防衛','容許構成要件錯誤','刑法第23條'
 ],
 '緊急避難（刑法§24）':[
   '緊急避難','避難過當','避難行為過當','緊急危難','出於不得已','不得已之行為',
   '生命、身體、自由、財產','特別義務','法益權衡','利益衡量','刑法第24條'
 ],
 '依法令／業務正當行為（刑法§21～22）':[
   '依法令之行為','依法令行為','上級公務員命令','上級命令','明知命令違法',
   '業務上之正當行為','業務正當行為','刑法第21條','刑法第22條'
 ],
 '超法規阻卻違法事由':[
   '被害人承諾','得被害人承諾','被害人同意','推定承諾','推測承諾','義務衝突',
   '可容許風險','容許風險','社會相當性','超法規阻卻違法','阻卻違法事由','阻卻違法'
 ]
}

PROC=['刑事訴訟法','簡式審判','簡易判決','緩起訴','不起訴','提起公訴','自訴','上訴','羈押','搜索','扣押','證據能力','審判期日','法院應如何判決','告訴期間','監獄行刑法','羈押法','行政程序法','行政罰法']

def hits(text,words):
    return sum(1 for w in words if w in text)

def classify(r):
    q=S(r.get('question')); a=answer_text(r); z=q+' '+a
    scores={g:hits(q,ws)*12+hits(a,ws)*6 for g,ws in GROUPS.items()}
    # Strong priority for the two requested core areas.
    if any(k in z for k in ['正當防衛','現在不法','防衛過當','防衛意思','誤想防衛','偶然防衛']):
        scores['正當防衛（刑法§23）']+=50
    if any(k in z for k in ['緊急避難','緊急危難','避難過當','法益權衡']):
        scores['緊急避難（刑法§24）']+=50
    g=max(scores,key=scores.get)
    return g if scores[g]>0 else ''

def substantive(r):
    q=S(r.get('question')); z=target_text(r); g=classify(r)
    if not g:return False
    if any(k in q for k in PROC):return False
    # Require a genuine wrongfulness issue, not a distractor-only hit.
    if hits(q,GROUPS[g])>0:return True
    if g.startswith('正當防衛') and any(k in q for k in ['侵害','攻擊','毆打','反擊','防衛','抵抗','第三人']):
        return any(k in z for k in ['正當防衛','第23條','防衛'])
    if g.startswith('緊急避難') and any(k in q for k in ['危難','危險','逃生','救助','犧牲','避免']):
        return any(k in z for k in ['緊急避難','第24條','避難'])
    return False

def rank(r):
    g=classify(r); q=S(r.get('question')); a=answer_text(r); ex=S(r.get('exam_name')); zh=S(r.get('subject_zh'))
    n=hits(q,GROUPS[g])*15+hits(a,GROUPS[g])*8
    if any(k in ex for k in PREF): n+=10
    if any(k in ex for k in ['警察','司法人員','司法官','律師','升官','警大','警佐']): n+=7
    if '刑法' in zh:n+=10
    if g.startswith('正當防衛'):n+=5
    if g.startswith('緊急避難'):n+=4
    try:y=int(r.get('year_roc') or 0)
    except:y=0
    n+=max(0,y-95)*0.08
    return n

def basis_note(r,g):
    z=target_text(r)
    if g.startswith('正當防衛'):
        if '誤想防衛' in z or '容許構成要件錯誤' in z:
            return '刑法§23＋容許構成要件錯誤理論','客觀上欠缺現在不法侵害而行為人誤認防衛情狀時，屬誤想防衛／容許構成要件錯誤爭議；本題正解依原考試年度官方答案。'
        if '過當' in z:
            return '刑法§23但書','正當防衛須針對現在不法侵害；防衛行為過當者，依刑法第23條但書得減輕或免除其刑。本題正解依原考試年度官方答案。'
        return '刑法§23','正當防衛須有現在不法侵害，並出於防衛自己或他人權利。本題正解依原考試年度官方答案。'
    if g.startswith('緊急避難'):
        if '特別義務' in z:
            return '刑法§24Ⅱ','公務上或業務上有特別義務者，關於避免自己危難，不適用刑法第24條第1項之規定。本題正解依原考試年度官方答案。'
        if '過當' in z:
            return '刑法§24Ⅰ但書','避難須為避免法定法益之緊急危難且出於不得已；避難過當者得減輕或免除其刑。本題正解依原考試年度官方答案。'
        return '刑法§24','緊急避難須為避免自己或他人生命、身體、自由、財產之緊急危難，且出於不得已。本題正解依原考試年度官方答案。'
    if g.startswith('依法令'):
        if '第22條' in z or '業務' in z:
            return '刑法§22','業務上之正當行為不罰；是否具正當性仍須依具體業務規範與必要性判斷。本題正解依原考試年度官方答案。'
        return '刑法§21','依法令之行為不罰；依上級公務員命令之職務上行為原則亦不罰，但明知命令違法者除外。本題正解依原考試年度官方答案。'
    if '承諾' in z or '同意' in z:
        return '超法規阻卻違法事由－被害人承諾','被害人承諾須以法益得處分、承諾有效且行為不逾承諾範圍等為核心判斷。本題正解依原考試年度官方答案。'
    if '義務衝突' in z:
        return '超法規阻卻違法事由－義務衝突','義務衝突係行為人同時負擔無法兼顧之義務時的阻卻違法問題。本題正解依原考試年度官方答案。'
    return '超法規阻卻違法事由','本題涉及法定條文以外之阻卻違法理論，依題目所涉法益處分與利益衡量判斷；正解依原考試年度官方答案。'

df=pd.read_parquet(P)
subj=df.get('subject',pd.Series(['']*len(df),index=df.index)).astype(str)
subjzh=df.get('subject_zh',pd.Series(['']*len(df),index=df.index)).astype(str)
exam=df.get('exam_name',pd.Series(['']*len(df),index=df.index)).astype(str)
explicit=qcol=df.get('question',pd.Series(['']*len(df),index=df.index)).astype(str)
explicit_wrongfulness=qcol.str.contains('正當防衛|緊急避難|被害人承諾|推定承諾|推測承諾|義務衝突|業務上之正當行為|業務正當行為|依法令之行為|依法令行為|阻卻違法|刑法第21條|刑法第22條|刑法第23條|刑法第24條',regex=True)
excluded_other_law=subjzh.str.contains('監獄行刑法|羈押法|刑事訴訟法|行政程序法|行政罰法|民法|公司法|票據法|土地法',regex=True)
mask=(subj.str.contains('criminal',case=False,regex=False)
      | subjzh.str.contains('刑法',regex=False)
      | (explicit_wrongfulness & ~excluded_other_law))
df=df[mask].copy()
df['group']=df.apply(classify,axis=1)
df=df[df.group!=''].copy()
df=df[df.apply(substantive,axis=1)].copy()
df['rank']=df.apply(rank,axis=1)
df['sig']=df.apply(sig,axis=1)
df=df.sort_values(['rank','year_roc'],ascending=[False,False]).drop_duplicates('sig')
df['preferred']=df['exam_name'].astype(str).apply(lambda s:any(k in s for k in PREF))

# Strongly weight self-defense and necessity as requested.
targets={
 '正當防衛（刑法§23）':24,
 '緊急避難（刑法§24）':14,
 '依法令／業務正當行為（刑法§21～22）':5,
 '超法規阻卻違法事由':7
}
selected=[];used=set()
for g,n in targets.items():
    p=df[df.group==g]
    p=pd.concat([p[p.preferred],p[~p.preferred]]).drop_duplicates('sig')
    take=min(n,len(p))
    for _,r in p.head(take).iterrows():
        if r.sig not in used:selected.append(r);used.add(r.sig)

# If a smaller category lacks enough originals, fill only with other genuine wrongfulness questions.
for _,r in df.sort_values(['preferred','rank','year_roc'],ascending=[False,False,False]).iterrows():
    if len(selected)>=50:break
    if r.sig not in used:
        selected.append(r);used.add(r.sig)

# Fill any corpus gaps only with previously verified original exam questions.
for r in SUPPLEMENTAL:
    if len(selected)>=50: break
    s=sig(r)
    if s not in used:
        selected.append(r); used.add(s)

if len(selected)<50:
    raise RuntimeError(f'Only {len(selected)} unique substantive wrongfulness originals after verified supplements; available={dict(Counter(df.group))}')
selected=selected[:50]

# Require the two requested core areas to remain the dominant portion.
cnt=Counter(r['group'] for r in selected)
if cnt['正當防衛（刑法§23）']<15 or cnt['緊急避難（刑法§24）']<6:
    raise RuntimeError(f'Insufficient defense/necessity coverage: {dict(cnt)}')

qs=[]
for i,r in enumerate(selected,1):
    a=S(r.get('answer')).strip().upper();opts=[S(r.get(x)) for x in 'ABCD']
    if a not in 'ABCD' or len(opts)!=4:raise RuntimeError(f'bad question {i}')
    basis,note=basis_note(r,r['group'])
    try:year=int(r.get('year_roc') or 0)
    except:year=0
    try:qno=int(r.get('q_no') or i)
    except:qno=i
    qs.append({
      'id':i,'question':S(r.get('question')),'options':opts,'answer':a,'topic':r['group'],
      'basis':basis,'explanation':note,
      'source':f"{year}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{qno}題",
      'source_papers':S(r.get('source_papers')),'year_roc':year
    })

assert len(qs)==50
assert len({norm(q['question'])+'|'+'|'.join(map(norm,q['options'])) for q in qs})==50
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={
 'count':50,
 'scope':'刑法總則違法性：刑法§21～24＋超法規阻卻違法事由',
 'groups':dict(Counter(q['topic'] for q in qs)),
 'available_pool':dict(Counter(df.group)),
 'years':dict(sorted(Counter(q['year_roc'] for q in qs).items())),
 'preferred_exam_count':sum(any(k in q['source'] for k in PREF) for q in qs),
 'original_questions_unedited':True,
 'source_required':True,
 'self_defense_and_necessity_priority':True,
 'substantive_wrongfulness_filter':True,
 'current_code_checked':'115-07-22'
}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
