from pathlib import Path
import json
p=Path('admin-contract-plan-guidance-petition/questions.json')
qs=json.loads(p.read_text(encoding='utf-8'))
for q in qs:
    ans=q['answer']; correct=q['options']['ABCD'.index(ans)]; z=q['question']+' '+correct
    if q['topic']=='行政指導':
        if '明確拒絕' in z or ('拒絕' in z and '不利' in z):
            q['basis']='第166條'; q['explanation']='相對人明確拒絕行政指導時，行政機關應即停止，且不得據此為不利處置。'
        elif any(k in z for k in ['負責指導者','請求交付文書','應明示','明示之事項','書面']):
            q['basis']='第167條'; q['explanation']='行政指導時應明示目的、內容及負責指導者；相對人請求交付文書時，除行政上有特別困難外，應以書面為之。'
        else:
            q['basis']='第165條、第166條'; q['explanation']='行政指導以輔導、協助、勸告、建議等不具法律上強制力的方法促請特定人作為或不作為，且不得濫用。'
    elif q['topic']=='陳情':
        if any(k in z for k in ['言詞','朗讀','簽名或蓋章']):
            q['basis']='第169條'; q['explanation']='陳情得以書面或言詞為之；言詞陳情應作成紀錄並供陳情人確認。'
        elif '保密' in z:
            q['basis']='第170條'; q['explanation']='行政機關應迅速、確實處理陳情；有保密必要者，處理時應不予公開。'
        elif any(k in z for k in ['補陳','有理由','無理由']):
            q['basis']='第171條'; q['explanation']='陳情有理由者應採適當措施；無理由者應通知並說明；內容不明確或有疑義者得通知補陳。'
        elif any(k in z for k in ['移送','訴願','國家賠償','訴訟']):
            q['basis']='第172條'; q['explanation']='陳情應向其他機關為之者，得告知或移送並通知；事項依法得提起訴願、訴訟或國賠者，應告知陳情人。'
        elif any(k in z for k in ['不予處理','一再陳情','真實姓名','匿名']):
            q['basis']='第173條'; q['explanation']='無具體內容或真實姓名住址、同一事由已適當處理仍一再陳情等法定情形，得不予處理。'
        else:
            q['basis']='第168條'; q['explanation']='人民對行政興革建議、行政法令查詢、行政違失舉發或行政上權益維護，得向主管機關陳情。'
p.write_text(json.dumps(qs,ensure_ascii=False,indent=2),encoding='utf-8')
print('audited',len(qs),'questions')
