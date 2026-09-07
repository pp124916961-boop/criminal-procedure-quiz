from pathlib import Path
import json

P=Path('administrative-penalty-act-full/questions.json')
qs=json.loads(P.read_text(encoding='utf-8'))

EXPL35='對強制排除抗拒保全證據或強制到指定處所查證身分不服，得當場陳述理由表示異議；執行機關認有理由應停止或變更，認無理由得繼續執行並依規定處理。'
EXPL41='對扣留不服者得向扣留機關聲明異議；無理由時送直接上級機關決定。依法不得對實體裁處聲明不服者，得單獨對扣留逕行提起行政訴訟。'

def text(q):
    return q['question']+' '+q['options']['ABCD'.index(q['answer'])]

def set_basis(q,n,exp):
    q['basis']=f'第{n}條'
    q['topic']='裁處程序、扣留與附則（§33～46）'
    q['explanation']=exp

for q in qs:
    z=text(q)
    # §41 has priority over the generic §36 detention rule.
    if '扣留' in z and any(k in z for k in [
        '單獨對扣留','逕行提起行政訴訟','不得對裁處案件之實體決定聲明不服',
        '不得對裁處案件的實體決定聲明不服','直接上級機關','聲明異議'
    ]):
        set_basis(q,41,EXPL41)
        continue
    # §35 has priority over the generic §34 identity-verification rule.
    if ('指定處所' in z or '查證身分' in z) and '不服' in z and any(k in z for k in ['異議','法院','陳述理由']):
        set_basis(q,35,EXPL35)
        continue
    if any(k in z for k in ['當場陳述理由','表示異議']) and any(k in z for k in ['保全證據','查證身分','強制']):
        set_basis(q,35,EXPL35)

# Regression checks use stem + correct option because the legal trap can appear in the correct option.
q41=[q for q in qs if '不得對裁處案件之實體決定聲明不服' in text(q) or '單獨對扣留' in text(q)]
assert q41 and all(q['basis']=='第41條' for q in q41), q41
q35=[q for q in qs if '強制其到指定處所查證身分不服' in text(q)]
assert q35 and all(q['basis']=='第35條' for q in q35), q35

P.write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
print('audited', {'section41':len(q41),'section35':len(q35)})
