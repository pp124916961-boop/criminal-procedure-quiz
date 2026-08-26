from pathlib import Path
import json,re,urllib.request
import pandas as pd

OUT=Path('admin-procedure-54-91-102-109')
P=Path('/tmp/tw_legal_benchmark_v2.parquet')
URL='https://huggingface.co/datasets/lianghsun/tw-legal-benchmark-v2/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet?download=true'
if not P.exists(): urllib.request.urlretrieve(URL,P)

def rule(topic, stem, focus):
    t=stem+' '+focus
    if topic=='聽證':
        if '訴願' in focus or '先行程序' in focus: return '第109條','不服依聽證程序作成之行政處分者，免除訴願及其先行程序，得逕行提起行政訴訟。'
        if '再為聽證' in focus or '重新聽證' in focus: return '第66條','聽證終結後、行政處分作成前，行政機關認有必要時，得再為聽證。'
        if '聲明異議' in focus: return '第63條','當事人認為主持人於聽證程序所為處置違法或不當者，得即時聲明異議，由主持人即時處理。'
        if '聽證紀錄' in focus or ('紀錄' in focus and '聽證' in t): return '第64條','聽證應作成聽證紀錄並記載法定事項；當事人對紀錄有異議時，得即時提出。'
        if '預備聽證' in focus: return '第58條','為使聽證順利進行，必要時得於聽證期日前舉行預備聽證，以議定程序、釐清爭點及處理證據等事項。'
        if '公開' in focus or '言詞' in focus: return '第59條','聽證除法律另有規定外，以公開、言詞為原則；有法定情形時得全部或一部不公開。'
        if '主持人' in focus:
            if '首長' in focus or '指定' in focus: return '第57條','聽證由行政機關首長或其指定人員為主持人。'
            return '第62條','主持人應本中立、公正立場主持聽證，並依法行使程序指揮、發問、維持秩序等權限。'
        if '終結' in focus: return '第65條','當事人意見已充分陳述、案件達可為決定之程度時，主持人應終結聽證。'
        if '期日' in focus or '場所' in focus or '書面通知' in focus: return '第55條、第56條','行政機關舉行聽證前應以書面通知法定事項；有正當理由時得變更聽證期日或場所並依法通知、公告。'
        if '提出證據' in focus or '發問' in focus or '陳述意見' in focus: return '第61條','當事人於聽證時得陳述意見、提出證據，經主持人許可並得向相關人員發問。'
        if '斟酌全部聽證結果' in focus or '依聽證紀錄' in focus: return '第108條','經聽證作成行政處分時，應斟酌全部聽證結果；法律明定應依聽證紀錄作成者，應依紀錄為之。'
        if '法規命令' in focus or '行政計畫' in focus: return 'OUT',''
        if '法規明文' in focus or '認為有必要' in focus or '申請舉行聽證' in focus or '僅於' in focus: return '第107條','行政處分之聽證，於法規明文規定，或行政機關認為有必要時舉行；並非只有法規明文時才能聽證。'
        return '第54條至第66條','行政程序法第54條至第66條規範聽證的通知、主持、公開、程序進行、異議、紀錄、終結及再為聽證。'
    if topic=='陳述意見':
        if any(k in focus for k in ['得不給予','不給予','大量作成','急迫','公益','客觀上明白','顯屬輕微','已依第三十九條','已舉行聽證']): return '第103條','第103條列舉得不給予陳述意見機會的例外；未落入例外時仍應依第102條給予陳述意見機會。'
        if '書面通知' in focus or ('通知' in focus and '陳述意見' in t): return '第104條','行政機關給予陳述意見機會時，原則應以書面通知相對人並記載法定事項；得以言詞通知時應作成紀錄。'
        if '書面陳述' in focus or '逾期' in focus or '放棄' in focus: return '第105條','相對人以書面陳述意見者，應於期限內提出；逾期未提出者，視為放棄陳述機會。'
        if '言詞陳述' in focus or '口頭' in focus: return '第106條','相對人得於期限內以言詞陳述代替書面陳述，行政機關應作成紀錄並依法確認。'
        if '聽證' in focus and ('必要' in focus or '法規' in focus): return '第107條','行政處分之聽證，於法規明文規定或行政機關認為有必要時舉行。'
        return '第102條','行政機關作成限制或剝奪人民自由或權利的行政處分前，原則應給予相對人陳述意見的機會。'
    # 送達
    if '公示送達' in t:
        if any(k in focus for k in ['二十日','20日','六十日','60日','發生效力']): return '第81條','公示送達原則自公告之日起經20日發生效力；對境外送達的特定情形為60日，重複公示送達另有特別規定。'
        if any(k in focus for k in ['公告欄','政府公報','新聞紙','保管']): return '第80條','公示送達由行政機關保管文書並於公告欄黏貼公告；必要時得刊登政府公報或新聞紙。'
        if any(k in focus for k in ['處所不明','治外法權','外國','境外','依申請','依職權']): return '第78條、第79條','第78條規定公示送達的法定原因及依申請、依職權方式；對同一當事人的後續公示送達，第79條另有規定。'
        return '第78條至第82條','公示送達須具法定原因，並依公告方式、效力期間及證書規定辦理。'
    if '寄存' in focus: return '第74條','不能依通常、補充或留置方式送達時，得依法寄存文書並製作兩份送達通知書。'
    if any(k in focus for k in ['同居人','受雇人','接收郵件人員','補充送達']): return '第73條第1項','於應送達處所不獲會晤本人時，得交付有辨別事理能力的同居人、受雇人或接收郵件人員，但與本人利益相反者除外。'
    if '拒絕收領' in focus or '留置送達' in focus: return '第73條第3項','應受送達人或有權收受者無正當理由拒絕收領時，得將文書留置於應送達處所，以為送達。'
    if any(k in focus for k in ['自行送達','郵政機關','電子交換','掛號']): return '第68條','送達由行政機關自行或交郵政機關為之；依法以電子交換者視為自行送達，對權益有重大影響的文書原則應採掛號。'
    if any(k in focus for k in ['法定代理人','代表人','管理人','無行政程序行為能力']): return '第69條','對無行政程序行為能力人應向其法定代理人送達；對機關、法人或非法人團體，向其代表人或管理人送達。'
    if '外國法人' in focus: return '第70條','對外國法人或團體在我國有事務所或營業所者，向其在我國代表人或管理人送達。'
    if '代理人' in focus: return '第71條','代理人受送達權限未受限制時，原則應向代理人送達；必要時亦得送達於當事人本人。'
    if any(k in focus for k in ['住所','居所','事務所','營業所','就業處所','送達處所']): return '第72條','送達原則於應受送達人的住居所、事務所或營業所為之；必要時得於就業處所送達。'
    if '送達證書' in focus: return '第76條','送達人應作成送達證書，記載法定事項，並由收領人簽名、蓋章或按指印。'
    if '送達代收人' in focus: return '第83條','在中華民國無住居所、事務所或營業所者，行政機關得命其指定境內送達代收人。'
    if any(k in focus for k in ['星期日','休息日','日出前','日沒後']): return '第84條','送達原則不得於星期日、其他休息日或日出前、日沒後為之，但有法定例外或受領人不拒絕者不在此限。'
    if '不能送達' in focus: return '第85條','送達不能時，送達人應作成報告書記載不能送達的事由，並將文書繳回行政機關。'
    if '外國' in focus or '境外' in focus: return '第86條','於外國或境外送達，原則囑託該國管轄機關或我國駐外機構等為之；不能依此辦理時得依法以雙掛號郵寄。'
    if '治外法權' in focus: return '第87條','對享有治外法權之人送達，得囑託外交部為之。'
    if '軍人' in focus or '軍艦' in focus: return '第88條','對現役軍人或軍艦乘員送達，囑託其服務機關或艦長為之。'
    if '監獄' in focus or '看守所' in focus or '在監' in focus: return '第89條','對在監所人送達，囑託監所長官為之。'
    if '外國機關' in focus: return '第90條','應向外國機關或團體送達時，得囑託外交部為之。'
    return '第67條至第91條','行政程序法第67條至第91條規範行政文書送達的方式、處所、特殊送達、公示送達及效力。'

def tp_text(row):
    s=' '.join(str(row.get(c) or '') for c in ['question','A','B','C','D'])
    if '陳述意見' in s or '書面陳述' in s or '言詞陳述' in s: return '陳述意見'
    if '聽證' in s: return '聽證'
    return '送達'

def make_from_row(r):
    ans=str(r['answer']).strip().upper(); opts=[str(r[x] or '') for x in 'ABCD']; stem=str(r['question'] or ''); tp=tp_text(r)
    basis,exp=rule(tp,stem,opts['ABCD'.index(ans)])
    if basis=='OUT': return None
    return {'question':stem,'options':opts,'answer':ans,'topic':tp,'basis':basis,'explanation':exp,'source':f"{int(r['year_roc'])}年｜{str(r['exam_name'])}｜{str(r['subject_zh'])}｜第{int(r['q_no'])}題",'source_papers':str(r['source_papers'] or ''),'year_roc':int(r['year_roc'])}

qs=json.loads((OUT/'questions.json').read_text(encoding='utf-8'))
kept=[]; seen=set(); missing={'聽證':0,'陳述意見':0,'送達':0}
for q in qs:
    focus=q['options']['ABCD'.index(q['answer'])]
    basis,exp=rule(q['topic'],q['question'],focus)
    sig=q['question']+'|'.join(q['options'])
    if basis=='OUT': missing[q['topic']]+=1; continue
    q['basis'],q['explanation']=basis,exp; kept.append(q); seen.add(sig)

if any(missing.values()):
    df=pd.read_parquet(P)
    df=df[df['subject'].isin(['admin','public','foundational'])].copy()
    def text(r): return ' '.join(str(r.get(c) or '') for c in ['question','A','B','C','D'])
    kws=['聽證','陳述意見','書面陳述','言詞陳述','送達','公示送達','寄存送達','補充送達','留置送達']
    df=df[df.apply(lambda r:any(k in text(r) for k in kws),axis=1)]
    df=df.sort_values('year_roc',ascending=False)
    for tp,n in list(missing.items()):
        if n<=0: continue
        for _,r in df.iterrows():
            if tp_text(r)!=tp: continue
            q=make_from_row(r)
            if not q: continue
            sig=q['question']+'|'.join(q['options'])
            if sig in seen: continue
            kept.append(q); seen.add(sig); n-=1
            if n==0: break
        if n: raise RuntimeError(f'cannot replace {tp}: {n}')

# keep exactly 100, preserve original order as much as possible; assign ids
kept=kept[:100]
for i,q in enumerate(kept,1): q['id']=i
assert len(kept)==100 and all(q['basis']!='OUT' for q in kept)
(OUT/'questions.json').write_text(json.dumps(kept,ensure_ascii=False,indent=2),encoding='utf-8')
html=(OUT/'index.html').read_text(encoding='utf-8')
data=json.dumps(kept,ensure_ascii=False).replace('</','<\\/')
html=re.sub(r'const BASE=.*?;const KEY=', 'const BASE='+data+';const KEY=', html, count=1, flags=re.S)
(OUT/'index.html').write_text(html,encoding='utf-8')
from collections import Counter
summary={'count':len(kept),'topics':dict(Counter(q['topic'] for q in kept)),'basis_top':dict(Counter(q['basis'] for q in kept).most_common(20)),'audited':True,'outside_scope_replaced':sum(missing.values())}
(OUT/'audit-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
