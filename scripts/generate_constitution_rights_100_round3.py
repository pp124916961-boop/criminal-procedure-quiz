from pathlib import Path
import io, json, re, urllib.request, unicodedata
from difflib import SequenceMatcher
from pypdf import PdfReader

DST=Path("constitution-rights-100")
DST.mkdir(parents=True,exist_ok=True)
CHOICES=["\ue18c","\ue18d","\ue18e","\ue18f"]

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=45) as r:
        return r.read()

def pdf_text(url,layout=False):
    mode={"extraction_mode":"layout"} if layout else {}
    return "\n".join((p.extract_text(**mode) or "") for p in PdfReader(io.BytesIO(fetch(url))).pages)

def clean_piece(s):
    lines=[]
    for line in s.splitlines():
        z=line.strip()
        if not z: continue
        if z.startswith("代號：") or z.startswith("頁次："): continue
        lines.append(z)
    z=re.sub(r"\s+"," "," ".join(lines)).strip()
    z=re.sub(r"(?<=[\u3400-\u9fff])\s+(?=[\u3400-\u9fff])","",z)
    return z

def parse_questions(text, upto):
    starts=[]; expected=1
    for m in re.finditer(r"(?m)^(\d{1,2})\s+(?=\S)",text):
        n=int(m.group(1))
        if n==expected:
            starts.append((n,m.start(),m.end()))
            expected+=1
            if expected>upto+1: break
    out={}
    for i,(n,s,e) in enumerate(starts):
        if n>upto: break
        end=starts[i+1][1] if i+1<len(starts) else len(text)
        block=text[e:end]
        pos=[block.find(ch) for ch in CHOICES]
        if any(x<0 for x in pos) or pos!=sorted(pos): continue
        q=clean_piece(block[:pos[0]])
        opts=[]
        for j,p in enumerate(pos):
            stop=pos[j+1] if j<3 else len(block)
            opts.append(clean_piece(block[p+1:stop]))
        if q and len(opts)==4 and all(opts):
            out[n]=(q,opts)
    return out

def parse_answers(url):
    parsed={}
    reader=PdfReader(io.BytesIO(fetch(url)))
    for page in reader.pages:
        txt=page.extract_text(extraction_mode="layout") or ""
        lines=[ln.strip() for ln in txt.splitlines()]
        for i,line in enumerate(lines):
            if not line.startswith("題號"): continue
            nums=[int(x) for x in re.findall(r"第(\d+)題",line)]
            if not nums: continue
            j=i+1
            while j<len(lines) and not lines[j]: j+=1
            if j>=len(lines) or not lines[j].startswith("答案"): continue
            ans=re.findall(r"(?<![A-Z])([ABCD])(?![A-Z])",lines[j])
            parsed.update(dict(zip(nums,ans)))
    return parsed

def canon(s):
    s=unicodedata.normalize("NFKC",s)
    s=re.sub(r"[\s，。、「」『』：；？！,.!?:;（）()【】\[\]《》〈〉—–\-．·…]","",s)
    return s.lower()

def near_duplicate(a,b):
    if a==b:return True
    la,lb=len(a),len(b)
    if min(la,lb)<18:return False
    if min(la,lb)/max(la,lb)<0.80:return False
    return SequenceMatcher(None,a,b).ratio()>=0.955

excluded=[]
for p,label in [
    ("constitution-rights-50/questions.json","第一回"),
    ("constitution-rights-50-round2/questions.json","第二回"),
    ("constitution-rights-100-hard/questions.json","第四回"),
]:
    data=json.loads(Path(p).read_text(encoding="utf-8"))
    for x in data:
        excluded.append((canon(x["question"]),label,x["question"]))

def topic_basis(q):
    pairs=[
      (["平等","差別待遇"],("平等權","憲法第7條及相關司法院解釋、憲法法庭判決")),
      (["人身自由","收容","拘禁","管束"],("人身自由","憲法第8條及相關司法院解釋、憲法法庭判決")),
      (["居住遷徙","入境","出境"],("居住遷徙自由","憲法第10條及相關司法院解釋")),
      (["言論","出版","猥褻","廣告"],("言論自由","憲法第11條及相關司法院解釋、憲法法庭判決")),
      (["秘密通訊","書信"],("秘密通訊自由","憲法第12條及相關司法院解釋")),
      (["宗教","信仰"],("宗教自由","憲法第13條及相關司法院解釋")),
      (["集會","遊行"],("集會自由","憲法第14條及相關司法院解釋")),
      (["結社","政黨"],("結社自由","憲法第14條及相關司法院解釋")),
      (["工作權","職業自由","競業"],("工作權／職業自由","憲法第15條及相關司法院解釋")),
      (["財產權","徵收"],("財產權","憲法第15條及相關司法院解釋")),
      (["訴訟權","正當法律程序","正當程序"],("訴訟權／正當法律程序","憲法第16條及相關司法院解釋")),
      (["應考試","服公職"],("應考試服公職權","憲法第18條及相關司法院解釋")),
      (["納稅","租稅"],("納稅義務／租稅法律主義","憲法第19條及相關司法院解釋")),
      (["教育","大學自治","學生"],("教育權／大學自治","憲法第11條、第21條、第22條及相關司法院解釋")),
      (["隱私","肖像","個人資料","行動自由"],("隱私權／一般人格權","憲法第22條及相關司法院解釋")),
      (["婚姻"],("婚姻自由／人格自由","憲法第22條及相關司法院解釋")),
      (["法律保留","明確性","溯及既往","信賴保護"],("法治國原則","憲法第23條及相關司法院解釋")),
      (["比例原則"],("比例原則","憲法第23條及相關司法院解釋")),
      (["民主","共和","國民主權","權力分立","修憲"],("憲法基本原則","憲法第1條、第2條、增修條文及相關司法院解釋")),
      (["基本國策","社會保險","國民健康","民生福利"],("基本國策／社會國原則","憲法基本國策章及增修條文")),
    ]
    for kws,val in pairs:
        if any(k in q for k in kws): return val
    return ("憲法基本原則／基本權","憲法本文、增修條文及相關司法院解釋")

# Deliberately uses sources not used by rounds 1, 2 or 4.
sources=[
  dict(year=108,label="司法官／律師第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=108120&q=1&s=0101&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=108120&q=1&s=0101&t=S",nos=[1,2,3,4,5,6,7,9,10,11]),
  dict(year=107,label="司法官／律師第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=107120&q=1&s=0101&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=107120&q=1&s=0101&t=S",nos=list(range(1,15))),
  dict(year=106,label="司法官／律師第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=106120&q=1&s=0101&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=106120&q=1&s=0101&t=S",nos=[1,3,5,6,8,10,11,12,13,14]),
  dict(year=105,label="司法官／律師第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=105110&q=1&s=0101&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=105110&q=1&s=0101&t=S",nos=[4,5,7,9,11,12,14]),
  dict(year=104,label="司法官／律師第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=104110&q=1&s=0101&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=104110&q=1&s=0101&t=S",nos=[1,2,3,4,5,6,7,16]),
  dict(year=103,label="司法官／律師第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=103110&q=1&s=0101&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=303&code=103110&q=1&s=0101&t=S",nos=[2,3,4,6,7,9,10,11,12,14]),
  dict(year=102,label="司法官第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=201&code=102121&q=1&s=0214&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=201&code=102121&q=1&s=0214&t=S",nos=[1,2,3,4,5,6]),
  dict(year=101,label="司法官第一試",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=201&code=101120&q=1&s=0214&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=201&code=101120&q=1&s=0214&t=S",nos=[5,6,8,10,11,12,13,14,15,19,20,21,22]),
  dict(year=115,label="警察人員三等｜中華民國憲法與警察專業英文",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=201&code=115060&q=1&s=0205&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=201&code=115060&q=1&s=0205&t=S",nos=[1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,25,26,27,28,29]),
  dict(year=115,label="一般警察人員三等｜法學知識與英文",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=401&code=115060&q=1&s=0503&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=401&code=115060&q=1&s=0503&t=S",nos=[1,3,4,5,6,7,8,9,10,21]),
  dict(year=114,label="一般警察人員三等｜法學知識與英文",q="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=301&code=114060&q=1&s=0503&t=Q",a="https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?c=301&code=114060&q=1&s=0503&t=S",nos=[1,2,3,4,5,6,7,8,9,15,16]),
]

candidates=[]
for src in sources:
    maxno=max(src["nos"])
    qs=parse_questions(pdf_text(src["q"]),maxno)
    ans=parse_answers(src["a"])
    for no in src["nos"]:
        if no not in qs:
            print("SKIP_PARSE",src["year"],src["label"],no); continue
        if ans.get(no) not in ("A","B","C","D"):
            print("SKIP_ANSWER",src["year"],src["label"],no,ans.get(no)); continue
        q,opts=qs[no]
        topic,basis=topic_basis(q+" "+" ".join(opts))
        candidates.append({
          "question":q,"options":opts,"answer":ans[no],
          "topic":topic,"basis":basis,
          "explanation":f"本題依{src['year']}年官方標準答案，答案為{ans[no]}。",
          "source":f"{src['year']}年{src['label']}｜第{no}題",
          "source_url":src["q"],"answer_url":src["a"],
          "year_roc":src["year"],"q_no":no
        })

chosen=[]; chosen_can=[]; skipped=[]
for x in candidates:
    c=canon(x["question"])
    exact=[e for e in excluded if e[0]==c]
    near=[]
    if not exact:
        for ec,label,eq in excluded:
            if near_duplicate(c,ec):
                near.append((label,eq)); break
    internal=any(near_duplicate(c,cc) for cc in chosen_can)
    if exact or near or internal:
        skipped.append({
          "source":x["source"],"question":x["question"],
          "reason":"exact-existing" if exact else ("near-existing" if near else "internal"),
          "matches":[e[1] for e in exact] if exact else ([near[0][0]] if near else [])
        })
        continue
    chosen.append(x); chosen_can.append(c)
    if len(chosen)==100: break

if len(chosen)<100:
    raise RuntimeError(f"Only {len(chosen)} unique fresh questions after exclusions; candidates={len(candidates)}, skipped={json.dumps(skipped,ensure_ascii=False)}")

for i,x in enumerate(chosen,1): x["id"]=i

# Final hard barriers against rounds 1,2,4 and internal duplicates.
assert len(chosen)==100
assert len({canon(x["question"]) for x in chosen})==100
for x in chosen:
    c=canon(x["question"])
    for ec,label,eq in excluded:
        if near_duplicate(c,ec):
            raise RuntimeError(f"Overlap survived with {label}: {x['question']} :: {eq}")

(DST/"questions.json").write_text(json.dumps(chosen,ensure_ascii=False,indent=2),encoding="utf-8")
audit={
 "question_count":100,
 "candidate_count":len(candidates),
 "skipped_overlap_or_duplicate":len(skipped),
 "excluded_against":["第一回","第二回","第四回"],
 "source_counts":{},
 "skipped":skipped
}
for x in chosen:
    k=x["source"].split("｜第")[0]
    audit["source_counts"][k]=audit["source_counts"].get(k,0)+1
(DST/"round3-source-audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in audit.items() if k!="skipped"},ensure_ascii=False,indent=2))
