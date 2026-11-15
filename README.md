# 銀行體檢：把財報交給 AI，要它每一句指回頁碼

**網站（一個網址，手機可開）：https://cwstedctw.github.io/money-banking-ai-checkup/**

國立東華大學經濟學系「貨幣銀行學」AI 客座第二輪的上課包（陳文盛，通識教育中心；2026-11-16 中文場、11-18 英文場）。50 分鐘：先把一章講義交給 AI 練手 → 矽谷銀行開場 → 把病人銀行的財報交給 AI 做一張每格有頁碼的表 → 五個比率自己算 → 抽三格回原文查 → 壓力測試（T 字帳）→ 回家作業卡。

| 場 | 病人銀行 | 報表 | 網站入口 |
|---|---|---|---|
| 中文場 11/16（一）11:35–12:25 | 彰化銀行（2801） | 114 年度財報，2025-12-31 合併資產負債表（PDF 第 1 頁，紙本 8） | [投影片](https://cwstedctw.github.io/money-banking-ai-checkup/zh/deck.html)・[提示語](https://cwstedctw.github.io/money-banking-ai-checkup/zh/prompts.html)・[練習單](https://cwstedctw.github.io/money-banking-ai-checkup/zh/worksheet.html) |
| English session Wed 11/18 11:00–11:50 | JPMorgan Chase & Co. | 2025 Annual Report, balance sheet PDF p.199 (10-K p.167) | [Slides](https://cwstedctw.github.io/money-banking-ai-checkup/en/deck.html)・[Prompts](https://cwstedctw.github.io/money-banking-ai-checkup/en/prompts.html)・[Worksheet](https://cwstedctw.github.io/money-banking-ai-checkup/en/worksheet.html) |

開場案例兩場都是矽谷銀行（SVB Financial Group）2022-12-31 的資產負債表（照 10-K 第 95 頁重排的一頁摘錄在網站上）。

## 學生怎麼用

1. **主線：用你的 AI agent 開資料夾。** 下載這個 repo 的 ZIP（網站首頁有按鈕）、解開，用 Antigravity（File → Open Folder）、ChatGPT 桌面版的 Codex（新增專案 → 選資料夾）或 Claude 桌面版（Code 分頁 → 開啟資料夾）打開 `kit/zh`（英文場 `kit/en`），貼一句「請照這個資料夾的 AGENTS.md 做完 任務.md 的任務一」。agent 會自己照 `data/README.md` 抓財報、做出每格有 PDF 頁碼的表、列出比率算式。
2. **沒有 agent？** 從網站下載財報，上傳到 ChatGPT 或 Claude 網頁，貼提示語 ③。
3. 拿到表之後，**五個比率自己再算一次**（體檢表範本會算）——agent 算得快，核對是你的事。
4. 抽三格回原文查：單位、年度欄、合併還是個體。
5. 壓力測試：先在紙上動 T 字帳，再做任務二（或貼提示語 ④），把 AI 的每一句標成「表上／算的／推論」。
6. 回家作業＝任務三：換成你們挑的兩家銀行。交作業附揭露句。

## 老師怎麼用

- 把網站網址放進 e學苑（或任何課程平台）就好；也可以下載 `student/` 裡的 Word、Excel 自己上傳。
- 老師用的檔（壓力測試參考答案、體檢表老師版）**不在這個 repo 與網站上**，請向作者索取。
- 想換一家銀行、改成自己的課：見下一節，讓 AI 助理照規則幫你改。

## 這個 repo 內建 AI 助理規則

用 **Claude 桌面版（Code 分頁）／Claude Code、Codex、Antigravity** 或任何會讀 `AGENTS.md` 的工具打開這個資料夾，直接用中文講需求。`AGENTS.md` 已經告訴它：數字只能從 `numbers.json` 來、每個數字附頁碼、找不到就停下來問、學生資料不進 repo、怎麼跑產線。可以直接說：

- 「幫我加一家銀行：這是它的財報網址、資產負債表在第幾頁。」→ 它會照 `bank_numbers.py` 的格式加進去、重算五個比率、重產投影片與練習單。
- 「第 17 頁的參考答案是怎麼算的？」→ 它會引 `內容規格.md` §〇 F 與 `numbers.json` 回答。
- 「把提示語 ③ 改成某某銀行的科目名。」→ 它只改 `內容規格.md` §三，投影片、練習單、網站都會跟著更新。
- 「更新網站。」→ 跑 `tools/make_site.py`，改 `docs/`，push。

## 資料夾

| 路徑 | 是什麼 |
|---|---|
| `docs/` | GitHub Pages 網站（首頁、中英投影片、提示語頁、練習單、下載檔、QR） |
| `內容規格.md` | 課的正本：場次、三家銀行的數字與頁碼、50 分鐘流程、22 頁逐頁表、五個提示語全文、壓力測試參考答案、建置規則、複驗紀錄 |
| `bank_numbers.py` → `numbers.json`、`numbers.md` | 數字唯一來源（三家銀行逐格對過 PDF 原文與公開資訊觀測站／SEC XBRL） |
| `deck/make_slides.py`、`build_web.py`、`export_pdf.py` | 投影片產線（一份頁面規格產中英各 22 頁；提示語從規格讀、數字從 json 讀） |
| `tools/build_student_docs.py` | 練習單、回家作業卡、壓力測試題、體檢表範本（Word／Excel／HTML，中英） |
| `tools/make_site.py` | 產 `docs/` 網站與 QR（QR 程式產生＋反向解碼驗證） |
| `check_econ2.py` | 機械檢查：數字全在 json、提示語逐字相同、零外部資源、無簡體與大陸用語 |
| `student/`、`elearn/` | 產出的學生檔與 e學苑 可貼文字 |
| `kit/zh/`、`kit/en/` | **學生用的課程資料夾**：給 agent 的 `AGENTS.md`、`任務.md`（任務一體檢、任務二壓力測試、任務三回家換銀行）、`任務-老師示範.md`（老師台上跑的加碼版：比率圖、備忘、第二來源核對）、`README.md`（三種 agent 怎麼開）、`data/README.md`（財報網址＋sha256，PDF 不進 repo） |
| `demo/svb/` | 矽谷銀行摘錄頁產生器 |
| `data/README.md` | 三份官方財報的網址、頁碼與 sha256（PDF 本身不進 repo） |

## 來源與授權

- 財報：彰化銀行官網（114 年度財報、2025 年年報）、JPMorgan Chase 投資人關係網站（2025 Annual Report）、SEC EDGAR（SVB Financial Group Form 10-K FY2022）。著作權屬各發行機構，網站只連結官方檔；矽谷銀行摘錄頁是照公開申報文件逐格重排、供課堂使用。
- 教材本身：CC BY-NC-SA 4.0（見 `LICENSE`）。改成自己課堂的版本再發給別人時，請保留授權、註明改自這份。
- 課程：經濟學系「貨幣銀行學」（授課老師：王友利）；客座與教材：陳文盛 × AI 協作團隊（洄瀾／Claude、立霧／Codex、秀姑巒／Gemini、木瓜溪／OpenCode、美崙溪／Grok），2026-11-15。

## English

Teaching pack for an AI guest session in a Money and Banking course (NDHU, Taiwan). Students hand a bank's report to an AI, require a page for every sentence, compute five balance-sheet ratios themselves, spot-check against the original, then run a stress test. Site: https://cwstedctw.github.io/money-banking-ai-checkup/ — English session materials under `/en/`. The repo ships `AGENTS.md`, so an AI coding assistant opened in this folder knows the rules (numbers only from `numbers.json`, page references everywhere, no student data) and can add a new bank or regenerate slides and worksheets on request. License: CC BY-NC-SA 4.0.
