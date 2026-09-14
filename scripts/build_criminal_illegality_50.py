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

GROUPS={
 '正當防衛（刑法§23）':[
   '正當防衛','防衛過當','防衛行為過當','現在不法之侵害','現在不法侵害','不法侵害',
   '防衛意思','防衛自己','防衛他人','防衛第三人','防衛挑撥','挑唆防衛','防衛權',
   '誤想防衛','偶然防衛','容許構成要件錯誤','刑法第23條','第23條'
 ],
 '緊急避難（刑法§24）':[
   '緊急避難','避難過當','避難行為過當','緊急危難','出於不得已','不得已之行為',
   '生命、身體、自由、財產','特別義務','法益權衡','利益衡量','刑法第24條','第24條'
 ],
 '依法令／業務正當行為（刑法§21～22）':[
   '依法令之行為','依法令行為','上級公務員命令','上級命令','明知命令違法',
   '業務上之正當行為','業務正當行為','刑法第21條','刑法第22條','第21條','第22條'
 ],
 '超法規阻卻違法事由':[
   '被害人承諾','得被害人承諾','被害人同意','推定承諾','推測承諾','義務衝突',
   '可容許風險','容許風險','社會相當性','超法規阻卻違法','阻卻違法事由','阻卻違法'
 ]
}

PROC=['刑事訴訟法','簡式審判','簡易判決','緩起訴','不起訴','提起公訴','自訴','上訴','羈押','搜索','扣押','證據能力','審判期日','法院應如何判決','告訴期間']

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
mask=(subj.str.contains('criminal',case=False,regex=False)
      | subjzh.str.contains('刑法',regex=False)
      | subjzh.str.contains('法學',regex=False)
      | exam.str.contains('警察|司法|律師|警大|警佐',regex=True))
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

if len(selected)<50:
    raise RuntimeError(f'Only {len(selected)} unique substantive wrongfulness originals; available={dict(Counter(df.group))}')
selected=selected[:50]

# Require the requested core areas to dominate the bank.
cnt=Counter(r['group'] for r in selected)
if cnt['正當防衛（刑法§23）']<20 or cnt['緊急避難（刑法§24）']<10:
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
