const EXACT_PAGES = [
  {c:"dense",h:`
    <h1>行政法 NO1</h1>
    <div class="headrow"><h2>＊行程法</h2><span class="red memo">（公公民法人效信）</span></div>
    <h2>一、法例</h2>
    <div class="item">（一）本法功能：<span class="red">公公民法人效信</span></div>
    <div class="item">（二）<div class="tree wide">
      <div><b>行政程序：</b><span class="red">VA、VV、法規命令、行政規則、行政計畫、行政指導、陳情</span><small>①　②　③　④　⑤　⑥</small></div>
      <div><b>行政 H</b><div class="tree"><div class="red">國家</div><div class="red">地方團體</div><div><span class="red">其他行政主體</span>（公法人、行政法人）</div></div></div>
      <div class="red star">準行政 H：受託行使公權力之個人 or 團體</div>
    </div></div>
    <div class="item">（三）<div class="tree">
      <div><b>H 排除</b><div class="tree tight"><div>民意</div><div>軍</div><div>監</div></div></div>
      <div><b>事項排除：</b><span class="red">外交刑務執行及考</span><div class="tree tight"><div>改變身分 or 處分</div><div>重大改變身分 or 重大利益</div></div><span class="red side">例外要<br>適用本法</span></div>
    </div></div>
    <div class="item">（四）原則：</div>
    <div class="item star">裁量目的性原則</div>
    <div class="diagram">瑕疵<div class="tree horizontal"><div><span class="circ">外</span> → <span class="red">裁量逾越</span></div><div><span class="circ">內</span><div class="tree tight"><div>考量不必要因素：<span class="red">裁量濫用</span>（事實錯誤）</div><div>怠惰：<span class="red">裁量怠惰</span></div></div></div></div></div>
  `},
  {c:"dense",h:`
    <h2>二、管轄 <span class="red">（事務、土地、層級）</span></h2>
    <div class="item">（一）<div class="tree">
      <div>管轄<span class="red">法定</span>：管轄權依<div class="tree tight"><div>組織法規</div><div>其他行政法規</div></div><span class="red side">而取得</span></div>
      <div>管轄<span class="red">恆定</span>：移轉要<span class="red">依法規</span>（非行政規則）</div>
    </div></div>
    <div class="item">（二）變更管轄</div>
    <div class="tree num">
      <div><b>1. 要件</b><div class="tree tight"><div class="red">組織法規變更</div><div class="red">公告義務（如果後接的 H 法規也有更，就不用）</div><div class="red">公告日起等 3 日生效（除非另定）</div></div></div>
      <div><b>2. 誰公告</b><div class="tree tight"><div><span class="red">原 H ＋ 後接收 H</span>（原 H 被裁，後 H 自己公告就行）</div><div class="red">共同上級選由</div></div></div>
    </div>
    <div class="item star">（三）移轉管轄</div>
    <table><tr><th></th><th>隸屬</th><th>管轄移轉</th><th>VA</th><th>救濟</th></tr>
      <tr><td>委任</td><td class="red">上 H ＞ 下 H</td><td></td><td></td><td>上級</td></tr>
      <tr><td>委託</td><td class="red">×</td><td class="red">×</td><td class="red">原委託 H</td><td><span class="red">高原委</span></td></tr>
      <tr><td>委辦</td><td class="red">中央 ＞ 地方</td><td></td><td></td><td>上級</td></tr>
      <tr><td>行政委託<br>（委託私人）</td><td class="red">×</td><td class="red">個人團體<br>移轉</td><td class="red">私人</td><td><span class="red boxword">向原委</span><br>（私人為 H 上級）<br>（VA 是以私人名義作成）</td></tr>
    </table>
  `},
  {c:"dense",h:`
    <div class="item">2、移轉要件<div class="tree">
      <div>委任委託<div class="tree tight"><div class="red">依法規</div><div class="red">應公告 and 登報</div><div class="red">委任託行為</div></div></div>
      <div>委託私人<br>（行政委託）<div class="tree tight"><div class="red">依法規</div><div class="red">應公告 and 登報</div><div class="red">委託行為</div><div class="red">締約</div></div></div>
    </div></div>
    <div class="item">（四）競合</div>
    <div class="tree">
      <div>均有管轄：<span class="red">受理在先 → H 協議</span></div>
      <div><span class="circ">有爭議</span>：<span class="red longarrow">共同上級指定 → 各該上級協議</span></div>
    </div>
    <div class="tree red marks"><div>人民得申請指定</div><div>向共同上級 or 各該上級某一</div><div>指定後人民不能不服</div><div><span class="circ">10 日內決定</span></div></div>
    <div class="item">（五）H 義務<div class="tree"><div>管轄有無之<span class="red">應職權調查</span></div><div>通知人民，<span class="red">移送義務</span></div></div></div>
    <div class="item">（六）不停止後轉<div class="tree"><div><span class="red">因法規 or 事實變更，喪失管轄</span>（不是其他無管轄）</div><div><span class="red underline">當事人 ＋ 後 H 同意</span></div></div></div>
  `},
  {c:"dense",h:`
    <h2>（七）職務協助</h2>
    <div class="item"><b>1. 得請求</b><div class="tree red bigbrace"><div>法律不能</div><div>事實不能</div><div>不能調查</div><div>資料被持</div><div>較經濟</div><div>其他</div></div><div class="tree side-tree"><div>原則：書面</div><div>例外：口頭</div></div></div>
    <div class="item"><b>2. 拒絕</b><div class="tree">
      <div><span class="circ">得</span>：<span class="red">有正當理由不能</span></div>
      <div><span class="circ">應</span>：<div class="tree tight red"><div>非權限 or 依法不得為</div><div>妨害自身職務</div></div></div>
    </div></div>
    <div class="flow">3. 拒絕 → 請求的 H 異議 → 共同上級決定 → 被求上級 H 決定</div>
    <div class="item"><b>4. 錢：</b><div class="tree"><div>被請 <span class="red">要錢</span> → 請求</div><div>金額爭議：雙 H 協議 → 共同上級 H 定之</div></div></div>
  `},
  {c:"dense",h:`
    <h1>行程法 NO2</h1><h2>三、當事人</h2>
    <div class="item">（一）<div class="tree">
      <div>當事人：<span class="red">被作用者</span><small class="red">（SO 沒有行政 H，因為他是作用的）</small><div class="tree tight"><div>申請</div><div>VA</div><div>VV <span class="red">（無計劃、無法規）</span></div><div>指導</div><div>陳情</div><div>其他</div></div></div>
      <div>當事人能力：<span class="red">誰可以被作用</span><div class="tree tight"><div>自然人</div><div>法人</div><div>非法人團但有代表人</div><div>行政 H</div><div>其他</div></div></div>
      <div>行為能力：<span class="red">被作用，而有法律行為能力</span><div class="tree tight"><div>有行為能力自然人 <span class="red side">法代<br>本人<br>（本國可以）</span></div><div>法人</div><div>非法人團的代表 or 管理人</div><div>行政 H 首長、代理、授權人</div></div></div>
    </div></div>
    <div class="item">（二）視為當事人：<p>程序進行影響第三人權益 <span class="red">（被作用之第三人）</span></p><div class="tree horizontal"><div>職權</div><div>申請</div></div>→ <span class="red">通知其參加為當事人</span></div>
  `},
  {c:"dense",h:`
    <h2>（三）代理人 <span class="red">（本人不到）</span></h2>
    <div class="item"><b>程序</b><div class="tree red"><div>當事人，不得超過 3 人</div><div>委任書（無口頭） → 最初行政程序時</div><div>法規 or 程序禁止 → 就不能委任</div></div></div>
    <div class="item"><b>效力</b><div class="tree">
      <div>單獨代理權：2 代理人，得單獨代理</div>
      <div>再委任權：本人同意，代理人<span class="red">委任</span>→複代理人</div>
      <div>代理權授受：<div class="tree tight"><div>原：<span class="red">全部權利</span></div><div>例：<span class="red">申請撤回權，重大人特別授權</span></div></div></div>
      <div>代理權撤回：<span class="red">要通知 H</span></div>
      <div>代理權存續：本人死亡、能力消滅、變更代理規定……<br><span class="red center">均不改變代理權。</span></div>
    </div></div>
    <h2>（四）選定 or 指定當事人 <span class="red">（當事人多挑幾個當代表）</span></h2>
    <div class="item"><b>程序</b><div class="tree"><div><span class="red">1～5 人</span></div><div>選任<div class="tree tight"><div>人民自主選</div><div>H 認協程序，<span class="red">得命其選 → 逾期未選 → 職權指定</span></div></div></div></div></div>
    <div class="item"><b>效力</b><div class="tree"><div>單獨代理權</div><div>代理權授受<div class="tree tight"><div>原：<span class="red">全部權利</span></div><div>例：<span class="red">申請撤回、權利拋棄、全體同意</span></div></div></div><div>代理權撤回：<span class="red">書面通知 H</span></div></div></div>
  `},
  {c:"dense",h:`
    <h2>（五）輔佐人 <span class="red">（本人要到－偕同）</span></h2>
    <div class="tree"><div>當事人 or 代理人 經 H 同意</div><div>H 認有必要</div></div><span class="red side">偕同輔佐人到場</span>
    <h2>四、迴避</h2>
    <div class="item"><b>應自行</b><div class="tree"><div>配、前配、<span class="red">四血三姻</span>（當事人 or 當事共同權利義務）</div><div><span class="red">現曾</span>代理、輔佐人</div><div><span class="red">曾</span>證人、鑑定人</div></div></div>
    <div class="item"><b>申請</b><div class="tree"><div>應自行不自行</div><div><span class="boxword">事實偏頗</span><small class="red">（抗議這個不應自行）</small></div></div>⇒<div class="tree"><div>向原 H 申請，應釋明</div><div>不服 <span class="red">5 日提上級覆決，10 日裁定</span></div><div>程序<span class="red">停止</span>（除必要處置）</div></div></div>
    <div class="item"><b>職權：</b>應自行不自行 ＋ 未申請 → <span class="red">亦即依職權</span></div>
    <p>※ 現為證人、鑑定人不用迴避</p>
    <p class="red">若現為證、鑑，代表必不為 H</p>
  `},
  {c:"dense",h:`
    <h2>五、程序開始</h2>
    <div class="tree"><div>職權</div><div>當事人申請<div class="tree tight"><div>言詞</div><div>書面 → <span class="red">H 製作紀錄、閱覽簽章（≠送達）</span></div></div></div></div>
    <h2>六、調查事實及證據</h2>
    <div class="item">（一）職權調查主義 <span class="red">（不受當事人拘束）</span></div>
    <div class="item">（二）有利不利一律注意原則 → <span class="red">源自「依法行政原則」</span></div>
    <div class="item">（三）當事人為輔<div class="tree red"><div>得自行提證據</div><div>得向 H 申請調查及鑑識</div></div></div>
    <div class="item">（四）手段<div class="tree"><div>詢問當事人：<span class="red">得通知陳述意見</span></div><div>鑑定：<span class="red">必要，鑑人到場</span></div><div>勘驗：<span class="red">應，通知當事人到場</span></div><div>要求當事人 or <span class="red">第 3 人</span>提供文書資料物品：<span class="red">必要</span></div></div></div>
    <div class="item">（五）紀錄：<span class="star">必要時</span>，製作書面紀錄<br><span class="red center">（≠程序開始，人民言詞<span class="circ">應作</span>）</span></div>
  `},
  {c:"dense",h:`
    <h2>七、資訊公開</h2>
    <table><tr><th></th><th>行程法</th><th>政府資訊公開法</th></tr>
      <tr><td>核心性質</td><td>閱卷權</td><td>人民資訊請求</td></tr>
      <tr><td>誰申請</td><td>當事人 or 利害關係人</td><td>一般人民、法人、團體</td></tr>
      <tr><td>目的</td><td>主張維護其法律<br>利益之必要</td><td>不用證明其法律利益</td></tr>
      <tr><td>時點</td><td>程序進行中</td><td>不限</td></tr>
      <tr><td>更正請求</td><td>只能更正自己的</td><td>更正 or 補充資訊</td></tr>
      <tr><td>處理期限</td><td>無，<span class="red">但注意程序中</span></td><td>15 日 ＋ 15 日（延）</td></tr>
      <tr><td>救濟</td><td>§174 不能單獨<br>要併實體</td><td>不服，直接行政救濟</td></tr>
    </table>
    <div class="item">得拒絕公開<div class="tree"><div>擬稿、準備文件</div><div>國防、軍事、公務機密</div><div>個人、職業、營業秘密 <span class="red side">無保密必要<br>仍要給閱</span></div><div>侵害第三人權益</div><div>妨礙社會公安職務</div></div></div>
  `},
  {c:"dense",h:`
    <div class="item">不得接觸：<div class="tree"><div>程序內 <span class="red">✓ 可接觸</span></div><div>程序外<div class="tree tight"><div>原 <span class="red">×</span></div><div><span class="circ">例</span> <span class="red">✓ 基於職務必要</span><div class="tree tight red"><div>書面（無書面要作書面）</div><div>對其他當事人公開</div></div></div></div></div></div></div>
    <h2>八、期間與期日</h2>
    <div class="item">（一）<div class="tree"><div>時：<span class="red">即時計</span></div><div>日：<span class="red">始日不算</span></div><div>月：<span class="red">相當日前一天</span>（1/3～1/2）</div><div>末遇假：<span class="red">次日／禮拜六：週一上午</span></div><div>不利 VA、處罰：<span class="red">始日一日論，末日遇假照計</span></div></div></div>
    <div class="item">（二）掛號郵寄給 H：<span class="red">交郵當日郵戳為憑</span></div>
    <div class="item">（三）回復原則<div class="tree red"><div>10 日內</div><div>其他行政行為一併補</div><div>逾一年不得申 <span class="black">（刑訴沒有效）</span></div></div></div>
    <div class="item">（四）未規定的公明處理期間<div class="tree"><div><span class="red">2 月 ＋ 2 月（延）</span></div><div>延前通知申請人</div><div>天災等不可歸責，處理期間<span class="red">停止</span></div></div></div>
  `},
  {c:"dense",h:`
    <h2>九、費用</h2>
    <div class="item">（一）<div class="tree"><div>程序所生：<span class="red">H</span></div><div>實為人民利益所支出<br>可歸責人民之延滯費：<span class="red">人民負擔</span></div></div></div>
    <div class="item">（二）<div class="tree horizontal"><div>證</div><div>鑑</div></div>日費 ＋ 旅費 ＋ <span class="red">報酬</span> → <span class="red">標準行政院定</span></div>
    <h2>十、聽證 <span class="red">（處分前最嚴密調查程序）</span></h2>
    <div class="item">（一）<span class="red">當事人：其他已知利害關係人</span></div>
    <div class="item">（二）書面通知；必要公告（若要預先公告，登報）</div>
    <div class="item">（三）主持人：H 首長 or 其指定／必要律師專業人員協助</div>
    <div class="item">（四）H 得預備聽證：<span class="red">應作紀錄</span></div>
    <div class="item">（五）聽證<div class="tree"><div>原：<span class="red">公開、言詞為之</span></div><div>例：全 or 一部不公開<div class="tree tight red"><div>違公益</div><div>當事人利益重大損害</div></div></div></div></div>
  `},
  {c:"dense",h:`
    <div class="item">（六）當事人權利<div class="tree red"><div>陳述意見</div><div>提出證據</div><div>經主持同意之辯論權</div><div>程序中聲明異議權</div></div></div>
    <div class="item">（七）聽證紀錄<div class="tree"><div>應作成，得錄音影輔助</div><div>當場閱簽；未當場指定時日閱覽</div><div>陳述發問拒簽，記明事由</div><div>紀錄記載有異議 <span class="red">有理由應補　無理由應記明</span></div></div></div>
    <div class="item">（八）終結及後續<div class="tree red"><div>充分陳述可決定應終結</div><div>H 後續必要再為聽證</div></div></div>
    <div class="item">（九）應聽證（強制）<div class="tree red"><div>人民申請 <span class="black">×</span> <span class="black">（但行政罰法有）</span></div><div>都更計畫</div><div>土地徵收有爭議</div></div><br>得：<span class="red">VA、行政計畫、訂定命令</span>（VV、陳情、指導 ×）<small class="red">（重大關係）</small></div>
    <div class="item star red">聽證後，免除訴願及其先行程序</div>
  `},
  {c:"loose",h:`
    <h2>十一、陳述意見 <span class="red">（較弱於聽證之調查程序）</span></h2>
    <div class="item">（一）<span class="red">被處分相對人；利害關係人</span></div>
    <div class="item">（二）H 作限制剝奪人民自由權利，<span class="red"><span class="circ">應</span>通知相對人陳述意見</span><br>殊<div class="tree tight"><div>得陳述意見（關係人的）</div><div>聽證</div></div></div>
    <div class="item">（三）H 得不給陳述：§103</div>
    <div class="item">（四）提出方式<div class="tree"><div>書面：<span class="red">陳述書</span></div><div>言詞：<span class="red">陳述書期限內提，H 應紀錄供簽</span></div></div></div>
    <div class="item">（五）H 應通知相對人可提出陳述書<div class="tree"><div>書面</div><div>口頭告知相對人，<span class="red">要作成紀錄供簽</span></div><div>必要時公告</div></div></div>
  `},
  {c:"dense",h:`
    <h2>十二、送達</h2>
    <div class="item">（一）送達人<div class="tree"><div><span class="red">H 承辦人</span>（行政關係）</div><div><span class="red">郵務員</span>（交由郵政 H）<div class="tree tight"><div>一般</div><div>掛號：<span class="red">人民權益重大影響</span></div></div></div></div></div>
    <div class="item">（二）受送達人<div class="tree">
      <div>原則<div class="tree tight"><div>法代</div><div>H、法人、非法人團 代表人 or 管理人</div><div>外國法人（在臺有事務所）代表 or 管理人</div></div><span class="red side">僅送其中一人即可</span></div>
      <div>例外<div class="tree tight"><div>代理人：<span class="red">H 認有必要，得送本人</span></div><div>無行為能力人：<span class="red">沒說法代前，都是送無行為能力人</span></div><div>第三人（同居、受僱、處所收郵人、當事人指定代收人）</div></div></div>
    </div></div>
    <div class="item red">※ 未成年人受送達效力</div>
    <div class="tree red"><div>本人為受送達 × §69，<span class="black">無行為能力應向父母送達</span></div><div>未成年人幫父母收送達 ✓ §73，<span class="black">有辨別事理能力可以代收</span></div></div>
    <div class="item">（三）送達處所<div class="tree"><div>一般受達人：<span class="red">住居、事務、營業處</span>、會晤處</div><div>H、法人、非法人團：<span class="red">機關的所在地、事務、營業處</span><br>必要時會晤、必要時住居</div><div>受達人就業處所</div></div></div>
  `},
  {c:"dense",h:`
    <h2>（四）送達方式</h2>
    <div class="tree">
      <div>補充：<span class="red">辨別事理 同居</span>（共同生活者）、<span class="red">受僱：處所收郵人</span><small>（委員會圖職 ×）</small></div>
      <div>留置：<span class="red">上述不收，放在應送達處所</span></div>
      <div>寄存（補充性）<div class="tree tight"><div>存：<span class="red">地方自治 H、PH、郵政 H</span></div><div>保存 <span class="red circ">3 月</span>（訴訟文書：2 月）</div></div><span class="red side boxword">送達即生效<br>≠10 日（≠行政訴訟）</span></div>
      <div>公示<div class="tree">
        <div>①<div class="tree tight"><div>送達處不明</div><div>治外法權人住所送達而無效</div><div>外國 or 境外不能囑託 or 預計無效</div><div>處所變更不陳明</div></div><span class="red side">H 依申請<br>職權認有<br>送後應為必要</span></div>
        <div>② 生效日<div class="tree tight"><div><span class="red">20 日</span>：一般情形，最後刊登日</div><div><span class="red">60 日</span>：外國、境外之人不送達</div><div><span class="red">即刻</span>：同一人公示後再公示</div></div></div>
      </div>
      <div>囑託<div class="tree tight"><div>外國境外：<span class="red">駐外領事館</span></div><div>駐外人員：<span class="red">外交部</span></div><div>軍人：<span class="red">軍事 H or 長官</span></div><div>治外法權人：<span class="red">外交部</span></div><div>監所人：<span class="red">監所長官</span></div></div></div>
    </div>
  `},
  {c:"loose",h:`
    <h2>（五）時間限制</h2>
    <div class="tree"><div>星期六、日</div><div>日出前、日沒後</div></div> → <span class="red">×　受達人同意就 OK</span>
    <h2>（六）公示送達 vs 公告</h2>
    <div class="tree"><div>公示：特定人、貼公告欄、<span class="red circ">得</span>加上公告方式</div><div>公告：不特定人、刊登政府公報 or 新聞紙</div></div>
    <p class="red center">所以 公示 ≠ 公告</p>
    <h2>（七）送達證書</h2>
    <div class="tree"><div><span class="circ">得</span>製作，沒作不影響送達效力 <small>（但有作<span class="circ">應</span>附卷）</small></div><div>公示送達：<span class="circ">應</span>作事由時間證書附卷</div></div>
    <h2>（八）送達生效日</h2>
    <div class="tree"><div>當日：<span class="red">效力看當日</span></div><div>始日不算：<span class="red">期間看翌日</span></div></div>
    <p class="star">ex：8/26 收 VA 則 <span class="tree inline"><span>8/26 生效</span><span>8/27 算訴願期限第 1 天</span></span></p>
  `},
  {c:"dense",h:`
    <h2>（九）電子送達</h2>
    <div class="item">1、電報交換、電傳文件、傳真、其他電子文件</div>
    <div class="item red">2、視為 H 自行送達</div>
    <div class="item">3、收領人未要求簽章</div>
    <h2>十三、教示救濟</h2>
    <div class="item">（一）何種 VA 須予教示</div>
    <div class="item">1、<span class="boxword">書面</span> VA or 口頭 VA 但被相對人要求<span class="boxword">書面</span></div>
    <div class="item">2、<div class="tree"><div>負擔處分 ✓</div><div>授益處分 <span class="red">但是 ✓（專利核准案）</span></div></div></div>
    <div class="item star red">3、口頭 VA 也要救濟教示 ✓（112 大法庭）<br><span class="black">（但沒說一般 VA）</span></div>
    <div class="item">4、其他法特設的救濟途徑 <span class="red">✓（112 大法庭）</span><br>ex：政府採購法「異議 → 申訴」</div>
    <h2 class="star">（二）教示欠缺處理 <span class="red">（錯誤教示的信賴保護）</span></h2>
    <div class="item">1、教示錯誤更正：<span class="red">應以通知送達</span><br><span class="red center">（法定期間是為送達之翌日起算）</span></div>
  `},
  {c:"loose",h:`
    <div class="item">2、誤載較長（5 日載成 10 日）</div>
    <div class="item center">有更正：<span class="red">信賴保護，以 10 日（98Ⅱ）</span></div>
    <div class="item center">未更正：<span class="red">1 年（98Ⅲ）</span></div>
    <div class="item">3、誤載較短（10 日載成 5 日）</div>
    <div class="item center">有更正：以更正送達翌日算（98Ⅰ）<br><span class="red star">但無信賴保護（Ⅱ）適用（98Ⅱ）</span></div>
    <div class="item center">未更正：<span class="red">1 年（98Ⅲ）</span></div>
  `},
  {c:"dense",h:`
    <h1>行政法 NO3</h1><h2>十四、行政立法</h2>
    <div class="item">（一）<div class="tree">
      <div>法規命令：<span class="red">直接對外</span></div>
      <div>行政規則<div class="tree tight"><div>一般性 <span class="red">×</span></div><div>解釋性、裁量性 <span class="red">間接對外</span></div></div></div>
      <div>職權命令（中標約）：<span class="red">早期可對外，後因法律保留原則不能對外（威權）</span></div>
      <div>授權命令（中標約）：<span class="red underline">同法規命令</span></div>
    </div></div>
    <div class="item">（二）法規命令訂定程序</div>
    <div class="tree num"><div>1、軍事外交、重大涉國家秘密、國安：<span class="red">法規命令訂定不依本法程序</span></div>
      <div>2、<div class="tree tight"><div>H 自行草擬</div><div class="red">人民 or 團體提議：要以書面提議</div></div></div>
      <div>3、要公告 <span class="red">（≠公示）</span><div class="tree tight"><div>擬訂時：除情況急迫、顯無法事先公告</div><div>有聽證時（不一定要聽證，但有辦就應公布）</div><div>發布 <span class="red">（後 3 日生效 or 特定日生效）</span></div></div></div>
      <div>4、核定<div class="tree tight"><div>法有說上級 H 核定，就要上 H 核定才能發布</div><div>數 H：上級 H or 共同上級 H 核定，均得發布</div></div></div>
    </div>
  `},
  {c:"dense",h:`
    <div class="item">5、立院審查</div>
    <h2>（三）行政規則下達、發布</h2>
    <div class="tree"><div>一般性：<span class="red">下達下級 H、屬官</span></div><div>解釋性、裁量性：<span class="red">首長簽署 ＋ 公告發布</span><small>（因為會間接對外故要發布）</small></div></div><span class="side">應<br>適<br>用</span>
    <h2>（四）行政規則生效時間</h2>
    <div class="tree"><div>解釋性：<span class="red">溯回法規生效日（因為它在解釋法規）</span></div><div>裁量基準：自公布 or 發布後 3 日 <span class="red">（有爭議）</span></div><div>對內行政規則：下達即發生效力</div></div>
    <h2 class="star underline">（五）下達</h2>
    <div class="item">1、所有行政規則，含解釋、裁量性，<span class="red">都要下達</span></div>
    <div class="item">2、只有間接對外的（解釋、裁量），<span class="red">要公告</span></div>
    <div class="item star red">3、但最高行：核發布不影響其效力<br>要以「下達」為核心</div>
  `},
  {c:"dense",h:`
    <h2>（六）解釋性行政規則解釋變更怎麼適用</h2>
    <div class="item">1、<span class="red">視案件是否確定</span>：<div class="tree"><div>確定：<span class="red">舊解釋（法安定性）</span></div><div>未確：<span class="red">新</span></div></div></div>
    <div class="item">2、<div class="tree"><div>新解釋侵害合規</div><div>實際非解釋，而是創設</div></div> → <span class="red">違信賴保護等原則審查</span></div>
    <h2>（七）審查</h2>
    <div class="item">1、立法審查<div class="tree horizontal"><div>法規命令 ✓</div><div>行政規則 ×</div><div>職權命令 ✓</div></div> → <span class="red circ">送立院審</span> → <span class="red">2 月內 H 更改 or 廢止</span></div>
    <div class="item">2、司法審查</div>
    <div class="item">（1）法意「<span class="red">具體審查</span>」vs「<span class="red">抽象審查</span>」<br><small>（審個案）　　　　（審法條）</small></div>
    <div class="item">（2）法規命令<div class="tree"><div>具：<span class="red">一般法院拒絕適用</span>（但僅個案）</div><div>抽：<span class="red">憲判宣告違憲</span>（大家之後都不能用）</div></div></div>
    <div class="item star">（3）行政規則（無效）<div class="tree"><div>具：<span class="red">法院拒絕</span>（僅個案）</div><div>抽：<span class="red">憲判 ×</span>（不審）<br><span class="red">也不送立院，也沒辦法審</span></div></div></div>
  `},
  {c:"loose",h:`
    <h2>※ 選擇法意</h2>
    <div class="item">1、法規命令應公告（除情況急迫）</div>
    <div class="item">2、得聽證</div>
    <div class="item">3、未公告，要刊報公告「任何人得向 H 陳述意見」→ <span class="red">陳述意見權</span></div>
    <div class="item">4、未公告，應聽證未聽證 → 程序瑕疵 <span class="red underline">≠ 不生效力</span></div>
    <div class="item">5、行政規則不拘束地方自治規則，但法規命令有拘束</div>
  `},
  {c:"dense",h:`
    <h1>行政法 NO4</h1>
    <h2>一、VA 定義</h2><p class="red memo">關公效外個單</p>
    <h2>二、VA 分類</h2>
    <div class="tree"><div>要式、不要式</div><div>羈束、裁量 <span class="red">（得、應）</span></div><div>下命、形成、確認 <span class="red">（罰鍰、許可認可特許、土地登記）</span></div><div>授益、負擔</div></div>
    <h2>三、書面否定</h2>
    <div class="tree"><div>原：<span class="red">書面、口頭、其他</span></div><div class="star">例<div class="tree tight red"><div>相對人、利害人有正當理由要求</div><div>聽證後所作成 VA</div></div> → <span class="red">應書面</span></div></div>
    <h2>四、送達（生效）</h2>
    <div class="tree"><div>書面：<span class="red">送達至相對人、利害人</span></div><div>其他：<span class="red">應以其他適當法通知 or 使其知悉</span></div></div>
    <h2>五、誤寫誤算</h2>
    <div class="flow"><span class="underline">H 隨時更正</span> or 申請 → 存據原處書 or 休 → 不將原記作更正書 → <span class="red">通知相對人、利害人</span></div>
  `},
  {c:"dense",h:`
    <h2>六、概括回答覆性質 <span class="red">（保護規範理論）</span></h2>
    <div class="tree"><div>觀念通知：<span class="red">99.9%</span></div><div>VA<div class="tree tight red"><div>專利舉發</div><div>商標異議／評定</div><div>檢舉金（查賄）<span class="black">（要視個案）</span></div></div></div></div>
    <h2>七、一般處分</h2>
    <div class="item">（一）<div class="tree"><div>對人：<span class="red">交通指揮、封山、交通號誌</span><span class="side boxed">對物一般 VA<br>反射鏡　屬觀通<br>火山爆行</span></div><div>對物：<span class="red">古蹟認定、公物確定</span></div></div></div>
    <div class="item">（二）非特定相對人：<span class="red">一般性特徵</span><div class="tree tight red"><div>時間</div><div>空間</div></div></div>
    <div class="item">（三）程序（vs VA）</div>
    <table><tr><th>VA</th><th>一般</th></tr><tr><td>特定人</td><td>不特定人</td></tr><tr><td><span class="red">要記明理由</span><br>（除非 §97）</td><td><span class="red">得不記明</span></td></tr><tr><td>向前送達</td><td><span class="red">公告「最後登載日」</span></td></tr></table>
  `},
  {c:"dense",h:`
    <h2>八、其他各種分類角度之 VA</h2>
    <h2 class="star">（一）暫時性 VA <span class="red">（115 國考）</span></h2>
    <p>工程尚未完工，工程費不明，H 輔助費無法確認</p>
    <div class="item">1、預估 1 億 → 補助 3000 萬 <span class="red">（暫時 VA）</span><br>↓<br>完工、總費用 8000 萬 → 補助 2400 萬 <span class="red">（最終 VA）</span></div>
    <div class="item">2、暫時性 VA <span class="red">≠</span> 附期限 VA <span class="red">≠</span> 定暫時狀態處分（假處分）<br><small class="red">（未終局）　　　　（已終局）</small></div>
    <div class="item">3、侵益性暫時 VA，<span class="red">應有法律授權</span></div>
    <div class="item">4、<table><tr><th></th><th>效力</th><th>信賴保護</th><th>救濟</th></tr><tr><td>終局未作</td><td>✓</td><td>✓</td><td>✓</td></tr><tr><td>終局已作</td><td>×<br><span class="red">原 VA 不用撤銷<br>當然失效</span></td><td>×<br>（115 學三）</td><td>×<br><span class="red">先救濟，後作成終局<br>對象自動變更終局 VA</span></td></tr></table></div>
  `},
  {c:"dense",h:`
    <h2>（二）第三人效力 VA</h2>
    <div class="item">1、<div class="tree"><div>對相對<span class="underline">授益</span>；第三人<span class="underline">負擔</span></div><div>對相對<span class="underline">負擔</span>；第三人<span class="underline">授益</span></div></div></div>
    <div class="item">2、常見種類</div>
    <div class="pairlist"><span>建照核准</span><span>鄰照權之鄰居</span><span>建築變更室內裝修</span><span>同棟人欲設置結構</span><span>都更計畫</span><span>範圍外受影響人民</span><span>政府採購審標</span><span>其他落標廠商</span><span>環評／重大開發</span><span>居民</span><span class="star">三接、海岸開發</span><span>解釋明因工程而危險者</span></div>
    <div class="item">3、因對第三人產生負擔（≠反射利益），而許其提 <span class="red">訴願、行政訴訟</span> → 第三人權益有遭侵害 <span class="red">（保護規範理論）</span></div>
    <div class="item">4、第三人對原 VA 提訴該，<span class="red">≠ 再提訴該</span>。而原授益相對人不服第三人訴願決定，再提行政訴訟 <span class="red">（不限再訴願）</span></div>
    <div class="item star">5、第三人同意<div class="tree"><div>VA：第三人不同意 → <span class="red">VA 仍生效</span></div><div>VV：第三人不同意 → <span class="red">VV 不生效</span></div></div></div>
  `},
  {c:"dense",h:`
    <h2>（三）重複處分與二次裁決</h2>
    <div class="item">1、<table><tr><th></th><th>重新實體審查</th><th>法效果</th><th>新 VA</th><th>重算救濟 TIME</th></tr><tr><td>重複 VA</td><td>×</td><td>×</td><td>×</td><td>×</td></tr><tr><td>第二次裁決</td><td>✓</td><td>✓</td><td>✓</td><td>✓</td></tr></table></div>
    <div class="item">2、重複 VA 被視為 → <span class="red">觀念通知（無法救濟）</span></div>
    <div class="item">3、注意不要跟 128 程序再開搞混</div>
    <p class="center">§128：人民要求 H 重新審理</p>
    <p class="center">二次裁決：不問有無義務，實際重審就算</p>
    <p class="red center">⇒ §128 不符要件<br>但 H 仍重新實體審查<br>→ 仍可能構成二次裁決（108 判 253）</p>
    <div class="item">4、<div class="tree"><div>原 VA 在事實、法律均未變更，得在<span class="underline">二次裁決</span> ✓</div><div>違反存續力、既判力，只要 H 重作審查，得被定義二裁 ✓</div></div><p class="red underline">二裁是定性，不是在討論它違法性問題</p></div>
  `},
  {c:"dense",h:`
    <h2>（四）須協力之 VA</h2>
    <div class="item">1、<div class="tree"><div>廣：人民 ＋ 他 H 協力（多階段）</div><div>狹：人民<div class="tree tight"><div>須申請 → <span class="red">申請補助、建照</span></div><div>須同意 → <span class="red">公務員任命</span></div></div></div></div></div>
    <div class="item">2、<table><tr><th></th><th>須協 VA</th><th>VV</th></tr><tr><td>人民有意思表示</td><td>✓</td><td>✓</td></tr><tr><td>人民共同決定規制</td><td>×</td><td>✓</td></tr><tr><td>性質</td><td class="red">單方行為</td><td class="red">雙方行為</td></tr><tr><td>欠缺人民意思</td><td class="red">補正（114）</td><td class="red">契約不成立</td></tr></table></div>
    <div class="item star underline">3、多階段 VA</div>
    <div class="item">（1）<div class="tree"><div>多階段 VA：A 前階內部參與 ＋ B 後階 VA</div><div>多階段行政程序：<span class="underline">A VA</span> ＋ <span class="underline">B VA</span></div></div></div>
  `},
  {c:"dense",h:`
    <div class="item">（2）救濟</div>
    <div class="tree"><div>多階段 VA：<span class="red">法院可以審 A＋B</span></div><div class="star">多階行程<div class="tree tight red"><div>法院審 A ✓</div><div>法院審 B ✓</div><div>法院審 A＋B × <span class="black">（B 救濟不能審 A）</span></div></div></div></div>
    <div class="item">（3）構成要件效力 vs 違法性繼承</div>
    <p>多階行程</p>
    <p>法院原則審 B，不能審 A　→ A 為 VA 有構成要件效力</p>
    <p>但 A 違法，理論上 B VA 無違法</p>
    <p>整體來看 B VA 也侵害人民，卻不能將 B 撤銷？</p>
    <p class="red">故使用違法性繼承，打破 A 的構成要件效力<br>讓法院審 B，雖 B 無違法，但 A 違法<br>使 B 認定有誤，進而違法，撤銷 B 之效力</p>
    <div class="item">（4）考題有時候會將多階行程稱多階 VA</div>
    <p>ex：財政部認定欠稅（自有送達），再函內政部限制行為人出境</p>
    <p>A：限制是 VA<br>B：限制內政部作成<br>C：屬多階 VA <span class="red">（但這也錯，應該是多階行程）</span><br><span class="red">×</span> D：不得對財政部救濟 <span class="red">→ 錯誤，選最錯的</span></p>
  `},
  {c:"dense",h:`
    <h2>九、VA 之附款</h2>
    <div class="item">（一）期限、條件、負擔、<span class="underline">保留</span>、保證</div>
    <p class="red center">不是保留 VA 撤銷，是廢止</p>
    <h2>（二）負擔 v.s 條件</h2>
    <div class="badges"><span>VA<span class="red">負</span></span><span>VA<span class="red">條</span></span></div>
    <table><tr><th></th><th>負擔</th><th>條件</th></tr>
      <tr><td>獨立</td><td>✓</td><td>×</td></tr>
      <tr><td>生效</td><td><span class="red">VA 生效，負擔生效</span></td><td>解除：條件成就 VA 失效<br>停止：條件成就 VA 生效</td></tr>
      <tr><td>強制</td><td>✓ <span class="red">可強制履行<br>可強制執行</span></td><td>× <span class="red">無執行力</span></td></tr>
      <tr><td>爭訟</td><td><span class="red">獨立對負擔</span></td><td>× §104</td></tr>
      <tr><td>不履行<br>原 VA 效力</td><td><span class="red">原 VA 效力仍在<br>故要對 VA 額外廢止</span></td><td><span class="red">VA 自然失效<br>無需另廢止</span></td></tr>
    </table>
    <h2>（三）VA 可加附款</h2>
    <div class="tree"><div>裁量 VA ✓</div><div>羈束 VA<div class="tree tight"><div>原 ×</div><div>例：<span class="red">① 法有明文 or ② 確保 VA 要件履行</span></div></div></div></div>
  `}
];
