from pathlib import Path
import json, re, urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('police-promotion-111-sergeant-to-inspector')
OUT.mkdir(parents=True, exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists():
    urllib.request.urlretrieve(URL,P)

def S(x): return '' if x is None else str(x)
def norm(s): return re.sub(r'\s+','',S(s))
def sig(r): return norm(r.get('question'))+'|'+'|'.join(norm(r.get(x)) for x in 'ABCD')

df=pd.read_parquet(P)
year=pd.to_numeric(df.get('year_roc'), errors='coerce')
exam=df.get('exam_name',pd.Series(['']*len(df),index=df.index)).astype(str)
subj=df.get('subject_zh',pd.Series(['']*len(df),index=df.index)).astype(str)

# 111年警察人員升官等考試－警正－行政警察人員。
mask=(year.eq(111)
      & exam.str.contains('警察',regex=False)
      & exam.str.contains('升官',regex=False))
pool=df[mask].copy()

wanted=[
 '國文',
 '法學知識與英文',
 '行政法',
 '警察法規'
]
def subject_group(s):
    for w in wanted:
        if w in s:
            return w
    return ''
pool['topic']=pool['subject_zh'].astype(str).map(subject_group)
pool=pool[pool.topic!=''].copy()

# Exclude the two non-single-answer items so the existing single-answer quiz engine remains literally unchanged:
# 法學知識與英文第29題：一律給分；警察法規第2題：A/B均給分。
def qnum(r):
    try:return int(r.get('q_no'))
    except:return -1
pool['qnum']=pool.apply(qnum,axis=1)
special=((pool.topic=='法學知識與英文') & (pool.qnum==29)) | ((pool.topic=='警察法規') & (pool.qnum==2))
excluded=pool[special].copy()
pool=pool[~special].copy()

pool['sig']=pool.apply(sig,axis=1)
pool=pool.drop_duplicates('sig').sort_values(['topic','qnum'])

counts=Counter(pool.topic)
expected={'國文':10,'法學知識與英文':49,'行政法':50,'警察法規':49}
if dict(counts)!=expected:
    raise RuntimeError(f'Unexpected counts {dict(counts)} expected {expected}; exam_names={sorted(set(pool.exam_name.astype(str)))}; subjects={sorted(set(pool.subject_zh.astype(str)))}')

questions=[]
for i,(_,r) in enumerate(pool.iterrows(),1):
    ans=S(r.get('answer')).strip().upper()
    opts=[S(r.get(x)) for x in 'ABCD']
    if ans not in 'ABCD' or len(opts)!=4:
        raise RuntimeError(f'bad single-answer row topic={r.topic} q={r.qnum} ans={ans}')
    source=f"111年警察人員升官等考試｜警正－行政警察人員｜{S(r.get('subject_zh'))}｜第{r.qnum}題"
    if r.topic=='行政法':
        basis='111年警察升官等－行政法｜官方標準答案'
        explanation='本題保留111年警察人員升官等考試原題與選項，正確答案依考選部該年度官方標準答案。'
    elif r.topic=='警察法規':
        basis='111年警察升官等－警察法規｜官方標準答案'
        explanation='本題保留111年警察人員升官等考試原題與選項，正確答案依考選部該年度官方標準答案。'
    elif r.topic=='法學知識與英文':
        basis='111年警察升官等－法學知識與英文｜官方標準答案'
        explanation='本題保留原題與選項，正確答案依考選部111年警察人員升官等考試官方標準答案。'
    else:
        basis='111年警察升官等－國文測驗｜官方標準答案'
        explanation='本題保留原題與選項，正確答案依考選部111年警察人員升官等考試官方標準答案。'
    questions.append({
      'id':i,'question':S(r.get('question')),'options':opts,'answer':ans,
      'topic':r.topic,'basis':basis,'explanation':explanation,'source':source,
      'year_roc':111,'q_no':r.qnum
    })

assert len(questions)==158
assert len({norm(q['question'])+'|'+'|'.join(map(norm,q['options'])) for q in questions})==158
(OUT/'questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
summary={
 'count':158,
 'scope':'111年警察人員升官等考試－警正－行政警察人員（可用單選題）',
 'subjects':dict(Counter(q['topic'] for q in questions)),
 'original_questions_unedited':True,
 'source_required':True,
 'official_answer_basis':True,
 'program_unchanged_requires_single_answer':True,
 'excluded_official_special_items':[
   {'subject':'法學知識與英文','q_no':29,'official':'一律給分'},
   {'subject':'警察法規','q_no':2,'official':'A或B均給分'}
 ]
}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
