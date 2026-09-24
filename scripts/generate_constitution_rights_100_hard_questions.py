from pathlib import Path
import io, json, re, urllib.request
from pypdf import PdfReader

DST=Path("constitution-rights-100-hard")
DST.mkdir(parents=True,exist_ok=True)

CHOICES=["\ue18c","\ue18d","\ue18e","\ue18f"]  # MoEx PDF glyphs: A/B/C/D

def fetch_text(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=45) as r:
        data=r.read()
    reader=PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages)

def clean_piece(s):
    lines=[]
    for line in s.splitlines():
        z=line.strip()
        if not z: continue
        if z.startswith("代號：") or z.startswith("頁次："): continue
        # Occasional page header fragment
        if re.fullmatch(r"\d+－\d+",z): continue
        lines.append(z)
    return re.sub(r"\s+"," "," ".join(lines)).strip()

def parse_first_questions(text, upto=20):
    # Question starts in MoEx PDFs are left-aligned "<number> <text>".
    starts=[]
    for m in re.finditer(r"(?m)^(\d{1,2})\s+(?=\S)",text):
        n=int(m.group(1))
        if 1 <= n <= upto+1:
            starts.append((n,m.start(),m.end()))
    # Keep first occurrence of a new sequential number; this rejects numbers in wrapped prose.
    seq=[]
    expected=1
    for n,s,e in starts:
        if n==expected:
            seq.append((n,s,e)); expected+=1
            if expected>upto+1: break
    if len(seq)<upto:
        raise RuntimeError(f"Could not locate first {upto} sequential questions; got {[x[0] for x in seq]}")
    out={}
    for i,(n,s,e) in enumerate(seq):
        if n>upto: break
        end=seq[i+1][1] if i+1<len(seq) else len(text)
        block=text[e:end]
        marks=[]
        for ch in CHOICES:
            p=block.find(ch)
            marks.append(p)
        if any(p<0 for p in marks) or marks!=sorted(marks):
            raise RuntimeError(f"Question {n}: option markers not found in order: {marks}\n{block[:1000]}")
        q=clean_piece(block[:marks[0]])
        opts=[]
        for j,p in enumerate(marks):
            stop=marks[j+1] if j<3 else len(block)
            opts.append(clean_piece(block[p+1:stop]))
        # Strip accidental next-page headers that survived in the last option.
        opts=[re.sub(r"\s*代號：\s*\d+\s*頁次：\s*\d+－\d+\s*$","",x).strip() for x in opts]
        if not q or len(opts)!=4 or any(not x for x in opts):
            raise RuntimeError(f"Question {n} malformed")
        out[n]=(q,opts)
    return out

def topic_basis(q):
    pairs=[
      (["平等","差別待遇"],("平等權","憲法第7條及相關解釋、憲法法庭判決")),
      (["人身自由","逮捕","拘禁","收容","強制工作"],("人身自由","憲法第8條及相關解釋、憲法法庭判決")),
      (["遷徙","入出國"],("居住遷徙自由","憲法第10條及相關解釋")),
      (["言論","出版","廣告","表現自由","強制道歉"],("言論自由","憲法第11條及相關解釋、憲法法庭判決")),
      (["秘密通訊","通訊監察"],("秘密通訊自由","憲法第12條及相關解釋")),
      (["宗教"],("宗教自由","憲法第13條及相關解釋")),
      (["集會"],("集會自由","憲法第14條及相關解釋")),
      (["結社","政黨"],("結社自由／政黨","憲法第14條、增修條文及相關解釋")),
      (["生存權","社會保險","老弱殘廢"],("生存權／社會權","憲法第15條、第155條及相關解釋")),
      (["工作權","職業自由","營業自由"],("工作權／職業自由","憲法第15條及相關解釋、憲法法庭判決")),
      (["財產權","徵收","土地"],("財產權","憲法第15條及相關解釋、憲法法庭判決")),
      (["訴訟權","救濟","法定法官"],("訴訟權／正當程序","憲法第16條及相關解釋、憲法法庭判決")),
      (["服公職"],("服公職權","憲法第18條及相關解釋")),
      (["納稅","租稅"],("納稅義務／租稅法律主義","憲法第19條及相關解釋")),
      (["教育","大學自治","學生"],("教育權／大學自治","憲法第11條、第21條、第22條及相關解釋")),
      (["隱私","個人資料","指紋","採尿"],("隱私權／資訊自主","憲法第22條及相關解釋、憲法法庭判決")),
      (["原住民"],("原住民族權利","憲法第22條、增修條文及相關解釋")),
      (["性傾向","婚姻"],("平等權／人格自由","憲法第7條、第22條及相關解釋")),
      (["法律保留","法律明確性","明確性原則"],("法治國原則","憲法第23條及相關解釋")),
      (["比例原則"],("比例原則","憲法第23條及相關解釋")),
      (["修憲"],("憲法基本原則／修憲","憲法增修條文及相關解釋、憲法法庭判決")),
      (["基本國策"],("憲法基本國策","憲法基本國策章及相關解釋")),
    ]
    for kws,val in pairs:
        if any(k in q for k in kws): return val
    return ("憲法基本原則／基本權","憲法本文、增修條文及相關司法院解釋、憲法法庭判決")

def add_moex(bank, year, code, c, s, qnos, answers, label):
    qurl=f"https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c={c}&code={code}&q=1&s={s}&t=Q"
    aurl=f"https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c={c}&code={code}&q=1&s={s}&t=S"
    text=fetch_text(qurl)
    parsed=parse_first_questions(text,max(max(qnos)+1,20))
    for qno in qnos:
        q,opts=parsed[qno]
        topic,basis=topic_basis(q)
        ans=answers[qno]
        bank.append({
          "id":len(bank)+1,
          "question":q,
          "options":opts,
          "answer":ans,
          "topic":topic,
          "basis":basis,
          "explanation":f"本題依{year}年官方標準答案，答案為{ans}。",
          "source":f"{year}年{label}｜第{qno}題",
          "source_url":qurl,
          "answer_url":aurl,
          "year_roc":year,
          "q_no":qno
        })

bank=[]

# 司法官／律師第一試：以高難度題為主，並排除中央政府組織題與已因新憲法判決明顯變動之舊題。
sources=[
 (115,"115110","303","0101",list(range(2,15)),
  {2:"A",3:"C",4:"C",5:"A",6:"A",7:"C",8:"D",9:"C",10:"B",11:"B",12:"B",13:"C",14:"D"}),
 (114,"114110","303","0101",list(range(2,15)),
  {2:"D",3:"B",4:"D",5:"A",6:"D",7:"A",8:"D",9:"A",10:"B",11:"A",12:"D",13:"B",14:"D"}),
 (113,"113110","303","0101",list(range(1,13)),
  {1:"D",2:"A",3:"D",4:"D",5:"D",6:"A",7:"D",8:"D",9:"D",10:"A",11:"D",12:"B"}),
 (112,"112120","303","0101",list(range(1,14)),
  {1:"A",2:"A",3:"D",4:"A",5:"D",6:"B",7:"C",8:"D",9:"C",10:"B",11:"B",12:"C",13:"D"}),
 (111,"111120","302","0101",[2,3,4,5,6,7,8,10,11,12,13,14],
  {2:"C",3:"C",4:"A",5:"D",6:"C",7:"D",8:"D",10:"B",11:"B",12:"B",13:"D",14:"A"}),
 (110,"110120","302","0101",[1,2,3,4,5,6,7,8,9,10,12],
  {1:"C",2:"A",3:"D",4:"D",5:"C",6:"D",7:"B",8:"B",9:"A",10:"C",12:"C"}),
 (109,"109120","302","0101",list(range(1,9)),
  {1:"B",2:"C",3:"D",4:"C",5:"B",6:"A",7:"C",8:"B"}),
]
for year,code,c,s,qnos,answers in sources:
    add_moex(bank,year,code,c,s,qnos,answers,"司法官／律師第一試｜綜合法學（一）（憲法、行政法、國際公法、國際私法）")

# 114司法三等：只取憲法基本原則、基本權與違憲審查範圍。
add_moex(
 bank,114,"114120","101","0309",
 [1,2,3,4,5,6,11,12,14,17],
 {1:"D",2:"C",3:"A",4:"D",5:"B",6:"C",11:"C",12:"C",14:"C",17:"D"},
 "司法人員三等考試｜法學知識與英文（中華民國憲法、法學緒論、英文）"
)

# 中央警察大學114年警佐班（原題文字；官方公告頁含試題與答案附件）
cpu_police_source="https://se.cpu.edu.tw/p/404-1006-44002.php"
cpu_police=[
(12,"關於服公職權的差別對待標準，我國司法院大法官曾認為下列何者違憲？",
 ["以年齡作為報考國家考試之標準","以學歷資格作為國防法務官報考資格之標準","以有無色盲作為報考警察之標準","以是否曾受刑之宣告作為國軍志願役預備軍官應考資格之標準"],"D"),
(13,"下列哪一事項屬於得由行政機關依據法律授權而訂定行政命令予以規範之事項？",
 ["公務員一次記二大過免職之構成要件","保險業務員停止招攬處分之構成要件","警察實施臨檢之要件、程序與救濟方式","公法或私法上之請求權消滅時效"],"B"),
(14,"依司法院大法官解釋，關於學生之訴訟權，下列敘述何者正確？",
 ["學校對學生之處分或公權力措施，若非屬對於學生之受教育權之侵害，則學生不得提起行政爭訟請求救濟","依目前之大法官解釋，中小學學生之權利因學校之處分而遭受侵害時，原則上僅能循學校內部申訴途徑謀求救濟","如學校基於教育目的或維持學校秩序，對學生所為之教育或管理等公權力措施，僅屬顯然輕微之干預，則學生不得提起行政爭訟","學生遭學校記過或申誡時，原則上不得就該不利處分提起行政爭訟"],"C"),
(15,"關於「受國民教育之權利」與「受國民教育以外教育之權利」的比較，下列敘述何者正確？",
 ["兩者皆兼具權利與義務之性質","兩者之憲法條文基礎皆為《憲法》第 22 條","兩者不僅皆具有防禦權之性質，亦具有請求國家提供特定教育給付之性質","不論是提供國民教育或國民教育以外之教育，各級學校皆有遵守《憲法》第 7 條平等權保障之義務"],"D"),
(16,"司法院大法官釋字第 432 號解釋中提及「法律明確性原則」的基本內涵。下列何者並非該解釋所提及關於該原則的基本內涵之一？",
 ["法律規範之意義須非難以理解","法律規範應使受規範者能預見何種作為或不作為構成義務之違反，及所應受之懲戒為何","嚴重拘束人身自由之法律規範，其明確性應受較為嚴格之審查","爭議發生時，可經由司法審查加以確認"],"C"),
]
for qno,q,opts,ans in cpu_police:
    topic,basis=topic_basis(q)
    bank.append({"id":len(bank)+1,"question":q,"options":opts,"answer":ans,"topic":topic,"basis":basis,
      "explanation":f"本題依中央警察大學114年警佐班第45期官方更正版答案，答案為{ans}。",
      "source":f"114年中央警察大學警佐班第45期｜國文與憲法｜第{qno}題",
      "source_url":cpu_police_source,"answer_url":cpu_police_source,"year_roc":114,"q_no":qno})

# 中央警察大學114學年度二技（原題文字；官方公告頁含試題及修正版答案）
cpu_2tech_source="https://se.cpu.edu.tw/p/406-1006-44317%2Cr257.php"
cpu_2tech=[
(15,"司法院大法官釋字第 509 號解釋理由書指出，《憲法》第十一條規定人民之言論自由應予保障，其具有之功能，不包括下列何者？",
 ["追求真理、滿足人民知的權利","形成公意，促進各種合理的政治及社會活動","保障個人內心精神活動","實現自我、溝通意見"],"C"),
(16,"司法院大法官釋字第 631 號解釋理由書指出，秘密通訊自由乃《憲法》保障隱私權之具體態樣之一，其所維護權利，不包括下列何者？",
 ["人性尊嚴、個人主體性","保障個人生活私密領域免於國家、他人侵擾","人格發展之完整","維護個人財產之自主控制"],"D"),
(17,"下列對於《國民年金法》之遺屬年金請領之司法院大法官釋字第 766 號解釋之敘述，何者錯誤？",
 ["如其內容涉及人民最低限度生存需求，則應兼受《憲法》第 15 條生存權之保障。對此等兼受生存權保障之社會保險給付請求權之限制，即應受較為嚴格之審查","人民依社會保險相關法律享有之社會保險給付請求權，具有財產上價值，應受《憲法》第 15 條財產權之保障","社會保險給付之請領要件及金額，應由立法者盱衡國家財政資源之有限性、人口增減及結構變遷可能對社會保險帶來之衝擊等因素而為規範","《憲法》第 155 條前段規定：「國家為謀社會福利，應實施社會保險制度。」基於前開《憲法》委託，立法者對於社會保險制度有較小之自由形成空間"],"D"),
]
for qno,q,opts,ans in cpu_2tech:
    topic,basis=topic_basis(q)
    bank.append({"id":len(bank)+1,"question":q,"options":opts,"answer":ans,"topic":topic,"basis":basis,
      "explanation":f"本題依中央警察大學114學年度學士班二年制技術系入學考試修正版答案，答案為{ans}。",
      "source":f"114學年度中央警察大學二年制技術系入學考試｜國文與憲法｜第{qno}題",
      "source_url":cpu_2tech_source,"answer_url":cpu_2tech_source,"year_roc":114,"q_no":qno})

assert len(bank)==100, len(bank)
assert all(len(x["options"])==4 and x["answer"] in "ABCD" for x in bank)
norm=lambda s: re.sub(r"\s+","",s)
groups={}
for x in bank:
    groups.setdefault(norm(x["question"]),[]).append(x)
dups=[v for v in groups.values() if len(v)>1]
if dups:
    raise RuntimeError("duplicate questions: "+json.dumps([[{"id":x["id"],"source":x["source"],"question":x["question"]} for x in g] for g in dups],ensure_ascii=False))
assert len(groups)==100

(DST/"questions.json").write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({
 "count":len(bank),
 "judicial_lawyer":82,
 "judicial_third":10,
 "police_sergeant":5,
 "police_university_two_year":3,
 "first":bank[0]["source"],
 "last":bank[-1]["source"],
},ensure_ascii=False,indent=2))
