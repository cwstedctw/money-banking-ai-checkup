# data/：這一夾要放的財報

> agent 會照這張表的網址自己下載、對 sha256；下載不了就請你用瀏覽器開網址、存進這一夾。PDF 不進 git。sha256 要相同才是同一份。

| 檔名（存成這個名字） | 是什麼 | 官方網址 | 頁數 | sha256 | 要看的頁 |
|---|---|---|---:|---|---|
| `CHB-2025-FY-consolidated-financial-report.pdf` | 彰化銀行 114 年度財務報告（官網「財務報告」頁的版本，10 頁：四大報表＋三頁附註摘錄） | https://www.bankchb.com/chb_2a_resource/leap_do/gallery/1775714798658/114年度財報.pdf （列在 https://www.bankchb.com/frontend/mashup.jsp?funcId=864385a215 ） | 10 | `27e72e334f13b794fad5ec0c8aa96095195645bec6eaa36656c2d3541abd153f` | **合併資產負債表＝PDF 第 1 頁（紙本頁碼 8）**；單位新臺幣千元；欄位 114 年 12 月 31 日／113 年 12 月 31 日 |
| `CHB-2025-annual-report.pdf` | 彰化銀行 2025 年年報（股東會年報，刊印 2026 年 3 月） | https://www.bankchb.com/chb_2a_resource/leap_do/annual_report_picture/1779097600166/彰化銀行2025年年報.pdf （列在 https://www.bankchb.com/frontend/annualReport.jsp ） | 123 | `2d19eb17fb948515b6dfce44c3f9cc7e62a4251c9d97220b7d3f4dda3c2705bb` | 業務內容（存款、放款…各業務比重）＝PDF 第 82 頁起（紙本 80）；財務狀況摘要＝PDF 第 98 頁（紙本 96）。⚠️年報裡**沒有**完整的合併資產負債表，只有三個總額 |

中文網址：用程式下載時要先把檔名那段做網址編碼（URL encode）；用瀏覽器直接開就好。
