from pathlib import Path
import base64,gzip,json,re,urllib.request
from collections import Counter
import pandas as pd

URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
OLD=Path('admin-procedure-1-19')
OUT=Path('admin-procedure-1-19-round2'); OUT.mkdir(parents=True,exist_ok=True)
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
if not P.exists(): urllib.request.urlretrieve(URL,P)

def S(x): return '' if x is None else str(x)
def norm(s): return re.sub(r'\s+','',S(s))
def sig(q,opts): return norm(q)+'|'+'|'.join(norm(x) for x in opts)

def extract_old_signatures():
    names=['p1.txt','p2.txt','p2b.txt','p3.txt','p4.txt','p5.txt','p6.txt']
    existing=[n for n in names if (OLD/n).exists()]
    if not existing: raise RuntimeError('old 1-19 bundle not found')
    b64=''.join((OLD/n).read_text(encoding='utf-8') for n in existing)
    html=gzip.decompress(base64.b64decode(b64)).decode('utf-8')
    arrays=[]
    for mm in re.finditer(r'((?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=\s*)(\[.*?\])(?=\s*;)',html,re.S):
        try:a=json.loads(mm.group(2))
        except:continue
        if isinstance(a,list) and len(a)>=50 and a and isinstance(a[0],dict) and ('opts' in a[0] or 'options' in a[0]):
            arrays.append(a)
    if not arrays: raise RuntimeError('could not extract old 1-19 question array')
    a=max(arrays,key=len)
    out=set()
    for x in a:
        q=S(x.get('q',x.get('question','')))
        opts=x.get('opts',x.get('options',[]))
        if q and isinstance(opts,list) and len(opts)==4: out.add(sig(q,opts))
    if len(out)<50: raise RuntimeError(f'only extracted {len(out)} old signatures')
    return out

OLD_SIGS=extract_old_signatures()

df=pd.read_parquet(P)
df=df[df['subject'].isin(['admin','public','foundational'])].copy()
PREF=['警察','一般警察','警察升官','升官','司法人員','司法官','律師','高等考試','普通考試','地方政府','關務','身心障礙','原住民族','鐵路','警大','警佐']

GROUPS={
 '法例與適用範圍':[
  '行政程序法之目的','行政程序之定義','行政機關之定義','受託行使公權力','視為行政機關','不適用行政程序法','不適用本法','程序規定','民意機關','司法機關','監察機關','外交行為','軍事行為','國家安全','犯罪偵查','犯罪矯正','教育目的之內部程序','人事行政行為','考選命題','評分'],
 '行政法一般原則':[
  '依法行政','法律原則','明確性原則','平等原則','比例原則','適當性','必要性','狹義比例','誠實信用','信賴保護','有利及不利','職權調查','裁量權','裁量逾越','裁量濫用','授權目的'],
 '管轄與指定管轄':[
  '管轄權','土地管轄','不動產所在地','受理在先','共同上級機關','指定管轄','管轄權有爭議','管轄爭議','臨時處置','不得聲明不服','組織法規變更','公告變更管轄','移轉管轄','無管轄權','喪失管轄權','移送有管轄權'],
 '權限委任委託':[
  '權限委任','權限委託','委任所屬下級機關','不相隸屬','委託民間團體','委託民間','受託行使公權力','法規依據公告','刊登政府公報','權限之一部分'],
 '行政協助':[
  '行政協助','職務協助','共同一體之行政機能','請求協助','被請求機關','嚴重妨害其自身職務','協助所需費用','顯較經濟','人員、設備不足','必要之文書','無隸屬關係之其他機關']
}

def ans_text(r):
    a=S(r.get('answer')).strip().upper()
    return S(r.get(a)) if a in 'ABCD' else ''
def focus(r): return S(r.get('question'))+' '+ans_text(r)

def classify(r):
    q=S(r.get('question')); a=ans_text(r)
    sc={g:0 for g in GROUPS}
    for g,ps in GROUPS.items():
        for p in ps:
            if p in q: sc[g]+=8
            if p in a: sc[g]+=5
    # Specific priority rules
    z=q+' '+a
    if any(k in z for k in ['行政協助','職務協助','請求協助','被請求機關']): sc['行政協助']+=20
    if any(k in z for k in ['權限委任','權限委託','委任所屬下級機關','委託民間團體','不相隸屬']): sc['權限委任委託']+=20
    if any(k in z for k in ['指定管轄','管轄權有爭議','土地管轄','受理在先','喪失管轄權','無管轄權']): sc['管轄與指定管轄']+=20
    if any(k in z for k in ['比例原則','平等原則','明確性原則','誠實信用','信賴保護','裁量權','有利及不利']): sc['行政法一般原則']+=20
    return max(sc,key=sc.get) if max(sc.values())>0 else ''

def score(r):
    q=S(r.get('question')); a=ans_text(r); z=q+' '+a; g=classify(r); n=0
    if g:n+=25
    for ps in GROUPS.values():
        for p in ps:
            if p in q:n+=5
            elif p in a:n+=2
    if '行政程序法' in q:n+=3
    ex=S(r.get('exam_name'))
    if any(k in ex for k in PREF):n+=5
    if '警察' in ex or '升官' in ex:n+=4
    # Penalize questions clearly centered on later chapters unless 1-19 rule is the correct answer.
    later=['行政處分之附款','行政契約','行政指導','行政計畫','陳情','法規命令','行政規則','送達','聽證','程序再開','訴願']
    if any(k in q for k in later) and not any(p in z for ps in GROUPS.values() for p in ps):n-=25
    try:y=int(r.get('year_roc') or 0)
    except:y=0
    return n+max(0,y-90)*0.02

df['group']=df.apply(classify,axis=1); df['score']=df.apply(score,axis=1)
c=df[(df.group!='') & (df.score>=20)].copy()
c['sig']=c.apply(lambda r:sig(S(r.get('question')),[S(r.get(x)) for x in 'ABCD']),axis=1)
c=c[~c.sig.isin(OLD_SIGS)].copy()
c=c.sort_values(['score','year_roc'],ascending=[False,False]).drop_duplicates('sig')

# Keep a balanced second review set, then fill only with unused original questions from §§1-19.
targets=[('法例與適用範圍',20),('行政法一般原則',25),('管轄與指定管轄',25),('權限委任委託',15),('行政協助',15)]
sel=[]; used=set()
for g,n in targets:
    for _,r in c[c.group==g].head(n).iterrows():
        sel.append(r); used.add(r.sig)
for _,r in c.iterrows():
    if len(sel)>=100: break
    if r.sig not in used:
        sel.append(r); used.add(r.sig)
if len(sel)<100: raise RuntimeError(f'Only {len(sel)} new unique original questions after excluding round 1')
sel=sel[:100]

def law(r):
    z=focus(r); g=r['group']
    if '行政協助' in z or '職務協助' in z or '請求協助' in z or '被請求機關' in z:
        return '第19條','行政協助須由無隸屬關係之其他機關在法定事由下協助；原則以書面請求，並區分應拒絕、得拒絕及費用負擔。'
    if '委託民間' in z or '民間團體' in z or '受託行使公權力' in z:
        return '第2條第3項、第16條','私人或團體受託行使公權力，在委託範圍內視為行政機關；委託須有法規依據並依法公告。'
    if '委任' in z or ('不相隸屬' in z and '委託' in z) or '權限委託' in z:
        return '第15條','委任係對所屬下級機關，委託係對不相隸屬行政機關，均須有法規依據並公告。'
    if '喪失管轄權' in z:
        return '第18條','行政機關因法規或事實變更喪失管轄權時，原則應移送；經當事人及有管轄權機關同意，得由原機關續行。'
    if '無管轄權' in z or '移送有管轄權' in z:
        return '第17條','行政機關應依職權調查管轄；認無管轄權者應即移送並通知，法定期間內提出者保有期間利益。'
    if '指定管轄' in z or '管轄權有爭議' in z or '管轄爭議' in z:
        return '第14條','數機關管轄權有爭議時，由共同上級機關決定；人民就依法規申請事件得申請指定管轄，法定情形並有緊急臨時處置。'
    if '受理在先' in z or '均有管轄權' in z:
        return '第13條','同一事件數機關均有管轄權時，原則由受理在先者管轄；不能判斷先後時依協議或上級機關指定處理。'
    if '土地管轄' in z or '不動產所在地' in z:
        return '第12條','不能依組織法規定土地管轄時，依不動產、事業處所、住所或主事務所、事件原因等順序決定。'
    if '組織法規變更' in z or '移轉管轄' in z or '公告變更管轄' in z:
        return '第11條','管轄權原則依組織法規或其他行政法規定；組織法規變更時，得依法公告變更管轄事項及其生效。'
    if '裁量' in z:return '第10條','行政機關行使裁量權，不得逾越法定裁量範圍，並應符合法規授權目的。'
    if '有利及不利' in z:return '第9條','行政機關就該管行政程序，對當事人有利及不利之情形均應一律注意。'
    if '誠實信用' in z or '信賴' in z:return '第8條','行政行為應以誠實信用方法為之，並保護人民正當合理之信賴。'
    if '比例原則' in z or any(k in z for k in ['適當性','必要性','損害最少','顯失均衡']):return '第7條','比例原則包括適當性、必要性與衡量性三層次。'
    if '差別待遇' in z or '平等原則' in z:return '第6條','行政行為非有正當理由，不得為差別待遇。'
    if '明確' in z:return '第5條','行政行為之內容應明確。'
    if '法律' in z and '一般法律原則' in z:return '第4條','行政行為應受法律及一般法律原則之拘束。'
    if '不適用' in z or g=='法例與適用範圍':return '第1條至第3條','本法第1至3條規範立法目的、行政程序與行政機關定義，以及機關或事項不適用行政程序法程序規定之範圍。'
    return '第1條至第19條','本題依行政程序法總則法例及管轄章第1條至第19條判斷。'

qs=[]
for i,r in enumerate(sel,1):
    a=S(r.get('answer')).strip().upper()
    if a not in 'ABCD': raise RuntimeError(f'bad answer {i}')
    opts=[S(r.get(x)) for x in 'ABCD']
    b,e=law(r)
    qs.append({'id':i,'question':S(r.get('question')),'options':opts,'answer':a,'topic':r['group'],'basis':b,'explanation':e,'source':f"{int(r.get('year_roc'))}年｜{S(r.get('exam_name'))}｜{S(r.get('subject_zh'))}｜第{int(r.get('q_no'))}題",'source_papers':S(r.get('source_papers')),'year_roc':int(r.get('year_roc'))})

assert len(qs)==100
assert len({sig(q['question'],q['options']) for q in qs})==100
assert not ({sig(q['question'],q['options']) for q in qs} & OLD_SIGS)
(OUT/'questions.json').write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'count':100,'round':2,'scope':'行政程序法第1條至第19條','groups':dict(Counter(q['topic'] for q in qs)),'years':dict(Counter(q['year_roc'] for q in qs)),'round1_excluded_count':len(OLD_SIGS),'overlap_with_round1':0,'original_questions_unedited':True,'source_required':True}
(OUT/'build-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))