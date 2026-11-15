# data/ — 示範用的官方財報（PDF 不進 git，照下表重抓）

> 2026-11-15 洄瀾抓的，三份都是官方網站原檔，sha256 要相同才算同一份。數字的唯一來源在上一層 `bank_numbers.py`／`numbers.json`（每個數字旁有頁碼與交叉驗證）。

| 檔名（本夾） | 是什麼 | 官方網址 | 頁數 | sha256 | 課堂用到的頁 |
|---|---|---|---:|---|---|
| `CHB-2025-FY-consolidated-financial-report.pdf` | 彰化銀行 114 年度財務報告（官網「財務報告」頁的版本，10 頁：四大報表＋三頁附註摘錄） | https://www.bankchb.com/chb_2a_resource/leap_do/gallery/1775714798658/114年度財報.pdf （列在 https://www.bankchb.com/frontend/mashup.jsp?funcId=864385a215 ） | 10 | `27e72e334f13b794fad5ec0c8aa96095195645bec6eaa36656c2d3541abd153f` | **合併資產負債表＝PDF 第 1 頁（紙本頁碼 8）**；單位新臺幣千元；欄位 114 年 12 月 31 日／113 年 12 月 31 日 |
| `CHB-2025-annual-report.pdf` | 彰化銀行 2025 年年報（股東會年報，刊印 2026 年 3 月） | https://www.bankchb.com/chb_2a_resource/leap_do/annual_report_picture/1779097600166/彰化銀行2025年年報.pdf （列在 https://www.bankchb.com/frontend/annualReport.jsp ） | 123 | `2d19eb17fb948515b6dfce44c3f9cc7e62a4251c9d97220b7d3f4dda3c2705bb` | 業務內容（存款、放款…各業務比重）＝PDF 第 82 頁起（紙本 80）；財務狀況摘要＝PDF 第 98 頁（紙本 96）。⚠️年報裡**沒有**完整的合併資產負債表，只有三個總額，數字跟財報相同 |
| `JPM-2025-annual-report.pdf` | JPMorgan Chase & Co. 2025 Annual Report（內含 2025 Form 10-K） | https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/annualreport-2025.pdf | 364 | `2a3ee9733eafd01e7667c5540fbd797c4cc688d14f00638a877f5623d1316d9d` | **Consolidated balance sheets＝PDF 第 199 頁（10-K 紙本頁碼 167）**；單位百萬美元；Business Segment & Corporate Results＝PDF 94（紙本 62）；uninsured deposits＝PDF 135（紙本 103）；存放比與存款占負債比＝PDF 136（紙本 104）；HTM 未實現損失＝PDF 261（紙本 229） |

矽谷銀行（SVB Financial Group）**沒有官方 PDF**：10-K 在 SEC EDGAR 只有網頁版 https://www.sec.gov/Archives/edgar/data/719739/000071973923000021/sivb-20221231.htm （Consolidated Balance Sheets＝紙本頁碼 95；未受保障存款 p.80；HTM 附註 p.125）。課堂用的是我們照原文重排的一頁摘錄 `../demo/svb/SVB-2022-balance-sheet-excerpt.pdf`（數字在 `bank_numbers.py` 的 `SVB["excerpt_rows"]`，逐格對過 EDGAR 原文與 XBRL）。要整本 10-K 的 PDF，只能由 Ted 用 Chrome 打開上面網址「列印→另存 PDF」（程式抓會被 SEC 擋：Your Request Originates from an Undeclared Automated Tool）。

重抓方式（Windows PowerShell，中文網址要先 URL 編碼，別用 Git Bash 的 curl 帶中文）：

```powershell
python -X utf8 -c "import requests,urllib.parse;u='https://www.bankchb.com/chb_2a_resource/leap_do/gallery/1775714798658/'+urllib.parse.quote('114年度財報.pdf');open('CHB-2025-FY-consolidated-financial-report.pdf','wb').write(requests.get(u,timeout=180).content)"
```

抓完 `Get-FileHash <檔> -Algorithm SHA256` 對上表。
