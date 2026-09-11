from pathlib import Path
import json,re,urllib.request
from collections import Counter,defaultdict
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OUT=Path('criminal-law-life-body-100'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)

def S(x): return '' if x is None else str(x)
def norm(s): return re.sub(r'\\s+','',S(s))
def sig(q,opts): return norm(q)+'|'+'|'.join(norm(x) for x in opts)
def answer_text(r):
    a=S(r.get('answer')).strip().upper()
    return S(r.get(a)) if a in 'ABCD' else ''
def focus(r): return S(r.get('question'))+' '+answer_text(r)

PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路','警大','警佐']

GROUPS={
 '殺人罪章（§271～276）':[
  r'第\\s*27[1-6]\\s*條',r'第二百七十[一二三四五六]條',
  '殺人罪','殺人未遂','殺人既遂','普通殺人','殺人預備','預備殺人','尊親屬殺人',
  '直系血親尊親屬.*殺','義憤殺人','激於義憤','生母殺嬰','殺嬰','囑託殺人','承諾殺人',
  '幫助自殺','教唆自殺','加工自殺','過失致死','謀為同死'
 ],
 '傷害罪章（§277～287）':[
  r'第\\s*27[7-9]\\s*條',r'第\\s*28[0-7]\\s*條',r'第二百七十[七八九]條',r'第二百八十[一二三四五六七]條',
  '傷害罪','普通傷害','重傷罪','使人受重傷','傷害致死','傷害致重傷','重傷致死',
  '尊親屬傷害','聚眾鬥毆','在場助勢','過失傷害','過失致重傷','凌虐未滿十八歲',
  '妨害幼童發育','未滿十八歲.*凌虐','傷害.*告訴乃論','告訴乃論.*傷害'
 ],
 '墮胎罪章（§288～292）':[
  r'第\\s*28[8-9]\\s*條',r'第\\s*29[0-2]\\s*條',r'第二百八十[八九]條',r'第二百九十[一二]條',
  '墮胎罪','墮胎','懷胎婦女','使之墮胎','介紹墮胎','墮胎方法','墮胎物品'
 ],
 '遺棄罪章（§293～295）':[
  r'第\\s*29[3-5]\\s*條',r'第二百九十[三四五]條',
  '遺棄罪','遺棄無自救力','無自救力','應扶助','應養育','應保護','扶助、養育或保護',
  '生存所必要之扶助','扶養義務.*遺棄','尊親屬.*遺棄'
 ],
 '發生交通事故逃逸（§185-4）':[
  r'185[-之]?4',r'第一百八十五條之四','肇事逃逸','事故逃逸','交通事故.*逃逸',
  '發生交通事故.*逃逸','駕駛動力交通工具.*逃逸'
 ]
}

def hits(text, pats):
    n=0
    for p in pats:
        if p.startswith('第\\') or '.*' in p or p.startswith('185'):
            if re.search(p,text): n+=1
        elif p in text: n+=1
    return n

def classify(r):
    q=S(r.get('question')); a=answer_text(r); z=q+' '+a
    scores={}
    for g,ps in GROUPS.items():
        scores[g]=hits(q,ps)*10 + hits(a,ps)*6
    # explicit priorities for the most distinctive chapters
    if re.search(r'185[-之]?4|第一百八十五條之四|肇事逃逸|交通事故.*逃逸',z): scores['發生交通事故逃逸（§185-4）']+=40
    if '墮胎' in z or '懷胎婦女' in z: scores['墮胎罪章（§288～292）']+=35
    if '遺棄' in z or '無自救力' in z: scores['遺棄罪章（§293～295）']+=30
    if any(k in z for k in ['聚眾鬥毆','重傷罪','過失傷害','傷害致死','傷害致重傷','使人受重傷']): scores['傷害罪章（§277～287）']+=25
    if any(k in z for k in ['殺人罪','殺人未遂','殺人預備','義憤殺人','生母殺嬰','囑託殺人','幫助自殺','教唆自殺','過失致死']): scores['殺人罪章（§271～276）']+=25
    g=max(scores,key=scores.get)
    return g if scores[g]>0 else ''

def relevant(r):
    q=S(r.get('question')); a=answer_text(r); z=q+' '+a
    g=classify(r)
    if not g:return False
    # Require at least one scope-specific signal in the stem or official correct option.
    return hits(z,GROUPS[g])>0

def score(r):
    q=S(r.get('question')); a=answer_text(r); z=q+' '+a; g=classify(r); n=0
    if not g:return -999
    n += hits(q,GROUPS[g])*12 + hits(a,GROUPS[g])*7
    ex=S(r.get('exam_name'))
    if any(k in ex for k in PREF): n+=8
    if any(k in ex for k in ['警察','司法人員','司法官','律師','升官','警大','警佐']): n+=6
    # favor direct chapter questions and recent years
    if any(k in q for k in ['依刑法','刑法第','下列何者','甲','乙']): n+=2
    try:y=int(r.get('year_roc') or 0)
    except:y=0
    n += max(0,y-90)*0.08
    return n

def article_and_note(r,g):
    z=focus(r)
    # 185-4 first
    if g.startswith('發生交通事故'):
        return '刑法§185-4','駕駛動力交通工具發生交通事故，致人傷害、重傷或死亡而逃逸，依刑法第185條之4判斷；歷屆題答案仍依原考試年度官方答案。'
    # explicit article in question/correct answer
    m=re.search(r'(?:刑法)?第\\s*(27[1-9]|28[0-9]|29[0-5])\\s*條',z)
    if m:
        n=int(m.group(1))
        return f'刑法§{n}',f'本題核心為刑法第{n}條。題幹與選項維持原考題文字；如該題後續曾遇修法，答案依原考試年度官方答案，並以現行法另行複習。'
    rules=[
      (['過失致死'],'276'),(['幫助自殺','教唆自殺','囑託','承諾而殺'],'275'),(['生母','甫生產','生產時'],'274'),(['義憤'],'273'),(['直系血親尊親屬','尊親屬'], '272'),
      (['重傷罪','使人受重傷'],'278'),(['傷害致死','傷害致重傷','傷害人之身體或健康'],'277'),(['聚眾鬥毆','在場助勢'],'283'),(['過失傷害','過失致重傷'],'284'),(['凌虐','妨害其身心之健全或發育'],'286'),(['告訴乃論'],'287'),
      (['懷胎婦女','服藥'],'288'),(['囑託','承諾','使之墮胎'],'289'),(['意圖營利','墮胎'],'290'),(['未受懷胎婦女','未得其承諾'],'291'),(['介紹墮胎'],'292'),
      (['遺棄無自救力'],'293'),(['應扶助','應養育','應保護','生存所必要'],'294'),(['直系血親尊親屬','尊親屬'],'295')
    ]
    for ks,n in rules:
        if all(k in z for k in ks):
            return f'刑法§{n}',f'本題核心依刑法第{n}條判斷；歷屆題答案依原考試年度官方答案。'
    defaults={
      '殺人罪章（§271～276）':('刑法§271～276','本題屬殺人罪章，依刑法第271條至第276條及相關總則規定判斷；歷屆題答案依原考試年度官方答案。'),
      '傷害罪章（§277～287）':('刑法§277～287','本題屬傷害罪章，依刑法第277條至第287條及相關總則規定判斷；歷屆題答案依原考試年度官方答案。'),
      '墮胎罪章（§288～292）':('刑法§288～292','本題屬墮胎罪章，依刑法第288條至第292條判斷；歷屆題答案依原考試年度官方答案。'),
      '遺棄罪章（§293～295）':('刑法§293～295','本題屬遺棄罪章，依刑法第293條至第295條判斷；歷屆題答案依原考試年度官方答案。')
    }
    return defaults[g]

df=pd.read_parquet(P)
# Keep criminal-law multiple-choice subjects; dataset subject labels vary, so use both subject and Chinese subject name.
subj=df.get('subject',pd.Series(['']*len(df),index=df.index)).astype(str)
subjzh=df.get('subject_zh',pd.Series(['']*len(df),index=df.index)).astype(str)
mask=subj.str.contains('criminal|刑',case=False,regex=True) | subjzh.str.contains('刑法',regex=False)
df=df[mask].copy()
df['group']=df.apply(classify,axis=1)
df['score']=df.apply(score,axis=1)
df=df[df.apply(relevant,axis=1)].copy()
df['sig']=df.apply(lambda r:sig(S(r.get('question')),[S(r.get(x)) for x in 'ABCD']),axis=1)
df=df.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

# Prefer the exam families requested by the user, but allow other national examinations if needed.
df['preferred']=df['exam_name'].astype(str).apply(lambda s:any(k in s for k in PREF))
pref=df[df.preferred].copy(); other=df[~df.preferred].copy()

# Minimum coverage, then fill by best remaining originals.
minimums={
 '殺人罪章（§271～276）':22,
 '傷害罪章（§277～287）':28,
 '墮胎罪章（§288～292）':8,
 '遺棄罪章（§293～295）':12,
 '發生交通事故逃逸（§185-4）':8
}
selected=[]; used=set()
for g,n in minimums.items():
    pool=pd.concat([pref[pref.group==g],other[other.group==g]]).drop_duplicates('sig')
    take=list(pool.head(n).iterrows())
    if len(take)<n:
        raise RuntimeError(f'Original-question pool for {g} has only {len(take)}, need minimum {n}')
    for _,r in take:
        if r.sig not in used:
            selected.append(r); used.add(r.sig)

for pool in [pref,other]:
    for _,r in pool.iterrows():
        if len(selected)>=100: break
        if r.sig not in used:
            selected.append(r); used.add(r.sig)
    if len(selected)>=100: break
if len(selected)<100:
    counts=Counter(r['group'] for r in selected)
    raise RuntimeError(f'Only {len(selected)} unique original questions. selected={counts}; available={Counter(df.group)}')
selected=selected[:100]

qs=[]
for i,r in enumerate(selected,1):
    a=S(r.get('answer')).strip().upper()
    opts=[S(r.get(x)) for x in 'ABCD']
    if a not in 'ABCD' or len(opts)!=4: raise RuntimeError(f'bad question {i}')
    basis,note=article_and_note(r,r['group'])
    year=int(r.get('year_roc') or 0)
    qno=int(r.get('q_no') or i)
    qs.append({
      'id':i,'question':S(r.get('question')),'options':opts,'answer':a,
      'topic':r['group'],'basis':basis,'explanation':note,
      'source':f"{year}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{qno}題",
      'source_papers':S(r.get('source_papers')),'year_roc':year
    })

assert len(qs)==100
assert len({sig(q['question'],q['options']) for q in qs})==100
assert all(q['source'] and q['answer'] in 'ABCD' for q in qs)
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={
 'count':100,
 'scope':'刑法分則：殺人罪章、傷害罪章、墮胎罪章、遺棄罪章＋刑法第185條之4',
 'groups':dict(Counter(q['topic'] for q in qs)),
 'years':dict(sorted(Counter(q['year_roc'] for q in qs).items())),
 'preferred_exam_count':sum(any(k in q['source'] for k in PREF) for q in qs),
 'original_questions_unedited':True,
 'source_required':True,
 'classification_uses_question_and_correct_option':True,
 'current_code_checked':'115-07-22'
}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('AVAILABLE',dict(Counter(df.group)))
