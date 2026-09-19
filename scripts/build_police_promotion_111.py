from pathlib import Path
import json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('police-promotion-111-admin-law'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)

def S(x): return '' if x is None else str(x)
def norm(s): return re.sub(r'\s+','',S(s))
def sig(r): return norm(r.get('question'))+'|'+'|'.join(norm(r.get(x)) for x in 'ABCD')

df=pd.read_parquet(P)
year=pd.to_numeric(df.get('year_roc'),errors='coerce')
exam=df.get('exam_name',pd.Series(['']*len(df),index=df.index)).astype(str)
subj=df.get('subject_zh',pd.Series(['']*len(df),index=df.index)).astype(str)

pool=df[
    year.eq(111)
    & exam.str.contains('警察',regex=False)
    & exam.str.contains('升官',regex=False)
    & subj.str.contains('行政法',regex=False)
].copy()

pool['qnum']=pd.to_numeric(pool.get('q_no'),errors='coerce')
pool['sig']=pool.apply(sig,axis=1)
pool=pool.drop_duplicates('sig').sort_values('qnum')

if len(pool)!=50:
    raise RuntimeError(f'Expected 50 original admin-law questions, got {len(pool)}; exams={sorted(set(pool.exam_name.astype(str)))}; subjects={sorted(set(pool.subject_zh.astype(str)))}')

qs=[]
for i,(_,r) in enumerate(pool.iterrows(),1):
    ans=S(r.get('answer')).strip().upper()
    opts=[S(r.get(x)) for x in 'ABCD']
    if ans not in 'ABCD' or len(opts)!=4:
        raise RuntimeError(f'bad row q={r.qnum} ans={ans}')
    qno=int(r.qnum)
    qs.append({
      'id':i,
      'question':S(r.get('question')),
      'options':opts,
      'answer':ans,
      'topic':'111警察升官等－行政法',
      'basis':'111年警察人員升官等考試－行政法｜官方標準答案',
      'explanation':'本題保留111年警察人員升官等考試行政法原題與選項，正確答案依該年度官方標準答案。',
      'source':f'111年警察人員升官等考試｜警正－行政警察人員｜行政法｜第{qno}題',
      'year_roc':111,
      'q_no':qno
    })

assert len(qs)==50
assert len({norm(q['question'])+'|'+'|'.join(map(norm,q['options'])) for q in qs})==50
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={
 'count':50,
 'scope':'111年警察人員升官等考試－警正－行政警察人員－行政法',
 'original_questions_unedited':True,
 'source_required':True,
 'official_answer_basis':True
}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
