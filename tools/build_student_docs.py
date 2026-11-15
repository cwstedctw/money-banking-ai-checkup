# -*- coding: utf-8 -*-
"""student-build.py — 貨銀課 AI 第二輪：學生檔（docx／html／xlsx／e學苑 md）單一來源產生器。
數字只讀 numbers.json；提示語只從 內容規格.md §三 的程式碼框抽（一字不漏）。
跑法（PowerShell）：python -X utf8 qa\\student-build.py
"""
import json, re, os, subprocess, html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / 'qa'
STU = ROOT / 'student'
EL = ROOT / 'elearn'
TEA = ROOT / 'teacher'  # 老師版（答案）一律放這裡，不進 student/（11/15 洄瀾）
TEACHER_DOCS = {'壓力測試參考答案-老師版', 'Stress-Test-Answer-Key-Teacher'}
STU.mkdir(exist_ok=True); EL.mkdir(exist_ok=True)
NODE_MODULES = ROOT.parent / 'econ-貨銀課AI客座演講' / 'tools' / 'node_modules'
SPECDIR = QA / 'student-specs'; SPECDIR.mkdir(exist_ok=True)

N = json.loads((ROOT / 'numbers.json').read_text(encoding='utf-8'))
B = N['banks']; CHB, JPM, SVB = B['CHB'], B['JPM'], B['SVB']
RD = N['ratio_definitions']

def f(x):  # 千分位
    return f'{x:,}'
def pct(x):
    return f'{x:.2f}'

# ---------- 提示語：從 內容規格.md 抽 ----------
def load_prompts():
    md = (ROOT / '內容規格.md').read_text(encoding='utf-8').splitlines()
    out = {}; i = 0
    while i < len(md):
        m = re.match(r'^\*\*(提示語|Prompt) ([①②③④⑤])', md[i])
        if m:
            lang = 'zh' if m.group(1) == '提示語' else 'en'
            j = i + 1
            while md[j].strip() != '```': j += 1
            k = j + 1; lines = []
            while md[k].strip() != '```': lines.append(md[k]); k += 1
            out[(lang, m.group(2))] = lines
            i = k
        i += 1
    return out
P = load_prompts()
assert len(P) == 10, P.keys()

L = lambda bank, key: bank['lines'][key]['label']
V = lambda bank, key: bank['lines'][key]['value']

# ================= 中文：學生練習單 =================
DISCLOSE_ZH = '本作業使用＿＿＿＿＿（AI 工具）協助＿＿＿＿＿＿＿（做了什麼）；數字已由本組對照原文核對。'
DISCLOSE_EN = 'This work used __________ (AI tool) to help with ______________ (what it did); our group checked the numbers against the original documents.'

def worksheet_zh():
    bl = []
    bl += [{'t': 'title', 'text': '銀行體檢學生練習單：彰化銀行'},
           {'t': 'subtitle', 'text': '貨幣銀行學 AI 第二輪｜2026-11-16（一）11:35–12:25｜陳文盛（東華大學通識教育中心）'}]
    bl.append({'t': 'h1', 'text': '0　今天要做什麼'})
    bl.append({'t': 'numbered', 'items': [
        '讓你的 AI agent（會自己開檔、做事的 AI 助手）打開課程資料夾，把彰化銀行財報的八個數字做成一張表，每一格都寫出在 PDF 第幾頁、每個比率列出算式。',
        '五個比率你自己再算一次，挑三格回原文查：單位、年度欄、合併或個體。',
        '做一次壓力測試：先在紙上用 T 字帳（左邊資產、右邊負債與權益的兩欄記帳格）算，再問 AI，標出它每一句是從報表來的、算出來的，還是它推的。',
    ]})
    bl.append({'t': 'h2', 'text': '要帶什麼'})
    bl.append({'t': 'bullets', 'items': [
        [['筆電，裝好一個 AI agent：', {}], ['Antigravity、ChatGPT 桌面版（Codex）或 Claude 桌面版', {'b': True}], ['，哪個有就用哪個。', {}]],
        '沒有 agent 的話：手機或筆電能開 ChatGPT／Claude 網頁也行（聊天版，見第 1 步備援）。',
        '計算機，或試算表範本「體檢表範本.xlsx」（在 e學苑，填數字比率自動算）。',
    ]})
    bl.append({'t': 'note', 'runs': [['怎麼讀這張表：', {'b': True}],
        ['每一步分四欄——做什麼、打什麼／貼什麼、你應該看到什麼、多久。「多久」寫的是這一步落在 50 分鐘課堂的第幾分鐘；老師沒有量過的就照實寫「沒量過」。卡住了先看第 3 節。', {}]]})

    bl.append({'t': 'h1', 'text': '1　步驟 1–7'})
    rows = [
        [[['1 下載課程資料夾', {'b': True}]],
         '打開課程網站 https://cwstedctw.github.io/money-banking-ai-checkup/ ，按「下載課程資料夾（ZIP）」（直接下載：https://github.com/cwstedctw/money-banking-ai-checkup/archive/refs/heads/main.zip ），下載後解壓縮。',
         '不用打。',
         '解開後的 kit/zh/ 裡有 AGENTS.md、任務.md、README.md 和 data/ 資料夾。',
         '第 13 分鐘開始；最好上課前先下載。'],
        [[['2 用 agent 打開 kit/zh', {'b': True}]],
         'Antigravity：File → Create Project → Add Folder → 選 kit/zh。ChatGPT 桌面版（Codex）：檔案 → 新增專案 → 新增 kit/zh → 信任資料夾。Claude 桌面版：Code 分頁 → 開啟資料夾 kit/zh。打開後貼右邊那一句。',
         '請照這個資料夾的 AGENTS.md 做完 任務.md 的任務一',
         'agent 先去抓財報（或請你把 PDF 放進 data/），然後產出 成品/體檢表.md——每格有 PDF 頁碼、每個比率有算式。',
         'agent 抓檔、做表的時間沒量過。'],
        [[['備援：聊天版', {'b': True}]],
         '沒有 agent：從課程網站下載 10 頁的財報（CHB-2025-FY-consolidated-financial-report.pdf），上傳到 ChatGPT 或 Claude 網頁（對話框旁的迴紋針 → 選檔）。年報（123 頁）回家做經營方式時再傳。',
         '提示語 ③（全文在第 2 節）。',
         '一張表：八個數字，每一格後面有 PDF 頁碼和科目原文；最後一句說是合併還是個體、哪一年的欄。',
         '等 AI 做表，沒量過。'],
        [[['3 核對 agent 的表', {'b': True}]],
         '打開 成品/體檢表.md（聊天版的人：看貼完提示語 ③ 拿到的表）。逐格看有沒有頁碼、比率有沒有算式。',
         '不用打。',
         '一張表、每格有頁碼、比率有算式；沒有頁碼的格先標起來。',
         '做到第 28 分鐘（含第 4 步）。'],
        [[['4 自己算五個比率', {'b': True}]],
         '把 AI 表上的數字抄進附表一「體檢表」，自己算；或打開「體檢表範本.xlsx」填分子、分母，比率自動算。證券投資＝三行金融資產相加（財報沒有「證券投資」這一列）。',
         '計算機：分子 ÷ 分母 × 100。',
         '五個百分比，每個都寫了分子、分母和 PDF 頁碼。跟同學不一樣先別改，第 5 步回原文查。',
         '做到第 28 分鐘。'],
        [[['5 抽三格回原文', {'b': True}]],
         '兩人一組。打開 PDF 翻到 AI 說的那一頁，各挑三格核對：單位（千元）、年度欄（114 年，不是 113 年）、合併或個體。',
         '不用打。',
         '附表三「抽查紀錄」填好三列；找到錯的舉手。',
         '第 28–35 分鐘。'],
        [[['6 壓力測試', {'b': True}]],
         '先在附表二的 T 字帳手算：明天一成存款被提走，先用「現金及約當現金」和「存放央行及拆借銀行同業」付，夠不夠？再接著同一個對話貼提示語 ④（用 agent 的人也可以說「做 任務.md 的任務二」）。',
         '提示語 ④（全文在第 2 節）。',
         'AI 列出 T 字帳、手上的錢夠不夠、五個新比率。你在它每一句旁標「表上」「算的」或「推論」，再拿自己算的對。',
         '第 35–44 分鐘；紙上先算 3 分鐘。'],
        [[['7 揭露句', {'b': True}]],
         '把揭露句抄在附表四，填上你用了哪個 AI、它幫你做了什麼。',
         '不用打。',
         '一句完整的揭露句；回家作業也要附。',
         '第 44–50 分鐘。'],
    ]
    bl.append({'t': 'table', 'widths': [1200, 2750, 1750, 3166, 1000],
               'header': ['步驟', '做什麼', '打什麼／貼什麼', '你應該看到', '多久'], 'rows': rows})

    bl.append({'t': 'h1', 'text': '2　要貼的提示語（一字不漏，整段複製）'})
    bl.append({'t': 'p', 'runs': '用 agent 的人：任務.md 的任務一、任務二就是這兩段，不必另外貼。用聊天版的人：提示語 ③ 在備援那一步貼；提示語 ④ 要接在同一個對話裡（它會用到上面那張表），第 6 步貼。ChatGPT、Claude 都能貼。'})
    bl.append({'t': 'prompt', 'label': '提示語 ③（銀行體檢）', 'lines': P[('zh', '③')], 'key': ('zh', '③')})
    bl.append({'t': 'prompt', 'label': '提示語 ④（壓力測試）', 'lines': P[('zh', '④')], 'key': ('zh', '④')})

    bl.append({'t': 'h1', 'text': '3　卡住了'})
    bl.append({'t': 'bullets', 'items': [
        [['agent 開不了或一直轉', {'b': True}], ['：換聊天版——ChatGPT 或 Claude 網頁上傳 10 頁財報、貼提示語 ③。', {}]],
        [['agent 說抓不到 PDF', {'b': True}], ['：自己從課程網站下載財報，放進 kit/zh/data/，再叫它重做。', {}]],
        [['數字找不到', {'b': True}], ['：先看 AI 說的是第幾頁；再確認你打開的是「財務報告」（10 頁），不是「年報」（123 頁）——年報裡沒有完整的合併資產負債表。合併資產負債表在財務報告 PDF 第 1 頁（頁面上印的頁碼是 8）。', {}]],
        [['AI 說「找不到」', {'b': True}], ['：它可能是對的。例如財報沒有「證券投資」這一列，要三行金融資產自己相加。翻到那一頁自己看。', {}]],
        [['比率跟同學差很多', {'b': True}], ['：最常見的四種錯——三行金融資產只加了一行、抄到 113 年那一欄、把千元當成元、拿到金控的報表。', {}]],
        [['其他狀況', {'b': True}], ['：把完整的畫面或錯誤訊息貼給 AI 問它怎麼辦；帳號、密碼不要貼。', {}]],
        [['都不行', {'b': True}], ['：看老師台上示範，數字用計算機手算。', {}]],
    ]})

    # 附表
    bl.append({'t': 'h1', 'text': '附表一　體檢表（比率自己算）', 'break': True})
    rows = []
    for r in RD:
        rows.append([[[f"{r['key'][1]}　{r['zh']}", {'b': True}]], '', '', '', '', ''])
    bl.append({'t': 'table', 'widths': [2266, 2300, 2300, 1100, 1100, 800], 'row_h': 720,
               'header': ['比率', '分子（科目＋數字）', '分母（科目＋數字）', '比率（%）', 'PDF 頁碼', '我查過 ✓'], 'rows': rows})
    bl.append({'t': 'table', 'widths': [1600, 1689, 1600, 1689, 1600, 1688],
               'header': None, 'row_h': 500, 'first_col_fill': 'F1F5F4', 'first_col_bold': True,
               'rows': [[{'text': '單位', 'b': True, 'fill': 'F1F5F4'}, '', {'text': '年度欄', 'b': True, 'fill': 'F1F5F4'}, '',
                         {'text': '合併／個體', 'b': True, 'fill': 'F1F5F4'}, '']]})
    bl.append({'t': 'p', 'runs': '證券投資＝透過損益按公允價值衡量之金融資產＋透過其他綜合損益按公允價值衡量之金融資產＋按攤銷後成本衡量之債務工具投資。'})

    bl.append({'t': 'h1', 'text': '附表二　壓力測試：一成存款被提走', 'break': True})
    bl.append({'t': 'table', 'widths': [3700, 3166, 3000], 'row_h': 480,
               'header': ['要用的數字（自己從財報找）', '金額（千元）', 'PDF 頁碼'],
               'rows': [['存款及匯款', '', ''], ['現金及約當現金', '', ''], ['存放央行及拆借銀行同業', '', ''],
                        ['一成存款＝存款及匯款 × 10%', '', '—'], ['手上的錢＝現金＋存放央行及同業', '', '—'],
                        ['夠不夠？不夠的話差多少？從哪裡來？', '', '—']]})
    bl.append({'t': 'note', 'runs': '先回財報 PDF 第 1 頁（紙本頁碼 8）抄兩列：現金及約當現金、存放央行及拆借銀行同業，再動 T 字帳。'})
    bl.append({'t': 'tacct', 'caption': [['T 字帳：哪幾行動、各動多少（減少寫負號）', {'b': True}]], 'left': '資產', 'right': '負債與權益', 'rows': 4})
    bl.append({'t': 'table', 'widths': [1973, 1973, 1973, 1973, 1974], 'row_h': 480,
               'header': [f"{r['key'][1]} {r['zh']}" for r in RD], 'rows': [['', '', '', '', '']]})
    bl.append({'t': 'p', 'runs': [['AI 的句子：表上、算的，還是推論？', {'b': True}], ['（挑三句抄下來）', {}]]})
    bl.append({'t': 'table', 'widths': [5866, 1800, 2200], 'row_h': 560,
               'header': ['AI 說的那一句', '表上／算的／推論', '根據（頁碼或理由）'], 'rows': [['', '', ''], ['', '', ''], ['', '', '']]})

    bl.append({'t': 'h1', 'text': '附表三　抽查紀錄（抽三格回原文）'})
    bl.append({'t': 'table', 'widths': [2000, 1300, 2266, 1300, 3000], 'row_h': 560,
               'header': ['格子（哪個數字）', 'PDF 頁', '原文數字', '對或錯', '原因（單位／年度欄／合併或個體／其他）'],
               'rows': [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']]})
    bl.append({'t': 'h1', 'text': '附表四　揭露句（抄一遍、填空）'})
    bl.append({'t': 'note', 'runs': [[DISCLOSE_ZH, {'b': True}]]})
    bl.append({'t': 'table', 'widths': [9866], 'row_h': 560, 'header': None, 'rows': [['']]})
    return {'lang': 'zh', 'title': '銀行體檢學生練習單：彰化銀行', 'header': '貨幣銀行學 AI 第二輪｜學生練習單', 'blocks': bl}

# ================= English worksheet =================
def worksheet_en():
    bl = []
    bl += [{'t': 'title', 'text': 'Bank Check-up Worksheet: JPMorgan Chase & Co.'},
           {'t': 'subtitle', 'text': 'Money and Banking, AI session 2 | 2026-11-18 (Wed) 11:00–11:50 | Wen-Sheng Chen (Center for General Education, National Dong Hwa University)'}]
    bl.append({'t': 'h1', 'text': '0  What we do today'})
    bl.append({'t': 'numbered', 'items': [
        'Let your AI agent (an AI assistant that opens files and does the work itself) open the course folder and build a table of nine numbers from JPMorgan Chase’s annual report, with the PDF page for every cell and the formula for every ratio.',
        'Compute the five ratios again yourself, then pick three cells and check them in the original: units, year column, consolidated or not.',
        'Run one stress test: work it out first on paper with T-accounts (a two-column sheet: assets on the left, liabilities and equity on the right), then ask the AI and mark whether each of its sentences is on the statement, calculated, or its own inference.',
    ]})
    bl.append({'t': 'h2', 'text': 'What to bring'})
    bl.append({'t': 'bullets', 'items': [
        [['A laptop with one AI agent installed: ', {}], ['Antigravity, ChatGPT desktop (Codex) or Claude desktop (Code tab)', {'b': True}], [' — whichever you have.', {}]],
        'No agent? A phone or laptop that can open ChatGPT or Claude on the web also works (the chat version; see the fallback after step 2).',
        'A calculator, or the spreadsheet “checkup-template.xlsx” (on the course e-Learning site; type the numbers and the ratios compute themselves).',
    ]})
    bl.append({'t': 'note', 'runs': [['How to read the step table: ', {'b': True}],
        ['each step has four columns — what to do, what to type or paste, what you should see, and how long. “How long” gives where the step falls in the 50-minute class; where the teacher has not timed it, it says so. If you get stuck, see section 3.', {}]]})

    bl.append({'t': 'h1', 'text': '1  Steps 1–7'})
    rows = [
        [[['1 Download the course folder', {'b': True}]],
         'Open the course website https://cwstedctw.github.io/money-banking-ai-checkup/ , click “Download the course folder (ZIP)” (direct link: https://github.com/cwstedctw/money-banking-ai-checkup/archive/refs/heads/main.zip ), then unzip it.',
         'Nothing to type.',
         'In the unzipped kit/en/ you see AGENTS.md, TASK.md, README.md and a data/ folder.',
         'From minute 13; better to download before class.'],
        [[['2 Open kit/en with your agent', {'b': True}]],
         'Antigravity: File → Create Project → Add Folder → choose kit/en → Next (older versions: File → Open Folder). ChatGPT desktop (Codex): File → New project → add the folder kit/en → create the project → trust the folder. Claude desktop: Code tab → open folder kit/en. Then paste the sentence on the right.',
         'Follow AGENTS.md in this folder and complete Task 1 in TASK.md.',
         'The agent first fetches the annual report (or asks you to put the PDF into data/), then writes a check-up table file — a page number for every cell and a formula for every ratio. README.md says where the file is saved.',
         'Fetching and table-making by the agent: not timed.'],
        [[['Fallback: chat version', {'b': True}]],
         'No agent: download the annual report from the course website and upload it to ChatGPT or Claude on the web (the paper-clip next to the chat box → choose the file). If 364 pages will not upload, give it only PDF page 199 (print that page to its own PDF).',
         'Prompt ③ (full text in section 2).',
         'A table of nine numbers; after each one, the PDF page, the printed page and the line name as printed; a last sentence on which year column and whether it is consolidated.',
         'Waiting for the AI; not timed.'],
        [[['3 Check the agent’s table', {'b': True}]],
         'Open the agent’s table file (chat version: the table you got from Prompt ③). Go cell by cell: is there a page number, does each ratio show its formula? The balance sheet is on PDF page 199, printed as page 167 — the book has two page numberings, so always say which one you mean.',
         'Nothing to type.',
         'A table with a page for every cell and a formula for every ratio; mark any cell without a page.',
         'Until minute 28 (with step 4).'],
        [[['4 Compute the five ratios', {'b': True}]],
         'Copy the numbers into Table 1 “Check-up table” and compute; or open “checkup-template.xlsx”, type numerator and denominator, and the ratio computes itself. Securities = “Investment securities, net” (trading assets not included).',
         'Calculator: numerator ÷ denominator × 100.',
         'Five percentages, each with its numerator, denominator and page. If yours differs from a classmate’s, do not change it yet — step 5 checks the original.',
         'Until minute 28.'],
        [[['5 Check three cells', {'b': True}]],
         'In pairs. Open the PDF at the page the AI gave and check three cells each: units (US$ millions), year column (2025, not 2024), consolidated or not, and PDF page vs printed page.',
         'Nothing to type.',
         'Table 3 “Spot-check log” has three rows filled in. Found a mistake? Raise your hand.',
         'Minutes 28–35.'],
        [[['6 Stress test', {'b': True}]],
         'First do the T-accounts in Table 2 by hand: 10% of deposits leave tomorrow and the bank pays first out of “Cash and due from banks” and “Deposits with banks”. Is it enough? Then paste Prompt ④ in the same chat (with an agent you can also say “do Task 2 in TASK.md”).',
         'Prompt ④ (full text in section 2).',
         'The AI lists the T-accounts, whether the cash is enough, and the five new ratios. Mark each of its sentences “on the statement”, “calculated” or “inference”, then compare with your own numbers.',
         'Minutes 35–44; 3 minutes on paper first.'],
        [[['7 Disclosure sentence', {'b': True}]],
         'Copy the disclosure sentence into Table 4 and fill in which AI you used and what it did.',
         'Nothing to type.',
         'One complete disclosure sentence; the homework needs one too.',
         'Minutes 44–50.'],
    ]
    bl.append({'t': 'table', 'widths': [1200, 2750, 1750, 3166, 1000],
               'header': ['Step', 'What to do', 'Type / paste', 'You should see', 'How long'], 'rows': rows})

    bl.append({'t': 'h1', 'text': '2  Prompts to paste (word for word; copy the whole block)'})
    bl.append({'t': 'p', 'runs': 'With an agent: Task 1 and Task 2 in TASK.md are these two prompts, so you do not paste them. With the chat version: paste Prompt ③ at the fallback step, and Prompt ④ in the same chat at step 6 — it builds on the table above. Both ChatGPT and Claude take them.'})
    bl.append({'t': 'prompt', 'label': 'Prompt ③ (Bank check-up)', 'lines': P[('en', '③')], 'key': ('en', '③')})
    bl.append({'t': 'prompt', 'label': 'Prompt ④ (Stress test)', 'lines': P[('en', '④')], 'key': ('en', '④')})

    bl.append({'t': 'h1', 'text': '3  If you get stuck'})
    bl.append({'t': 'bullets', 'items': [
        [['The agent will not open or keeps spinning', {'b': True}], [': switch to the chat version — upload the report to ChatGPT or Claude on the web and paste Prompt ③.', {}]],
        [['The agent says it cannot get the PDF', {'b': True}], [': download the annual report from the course website yourself, put it in kit/en/data/, and ask it again.', {}]],
        [['The upload fails (chat version)', {'b': True}], [': 364 pages may be too large for some chat tools. Give it only PDF page 199.', {}]],
        [['A number cannot be found', {'b': True}], [': look at the page the AI named, and check which numbering it used — PDF page 199 is printed as page 167.', {}]],
        [['The AI says “not found”', {'b': True}], [': it may be right. Open the page and look yourself.', {}]],
        [['Your ratios differ a lot from a classmate’s', {'b': True}], [': the usual four causes are PDF page vs printed page, gross loans (“Loans”) instead of “Loans, net of allowance for loan losses”, trading assets counted as securities or not, and copying the 2024 column.', {}]],
        [['Anything else', {'b': True}], [': paste the whole screen or the full error message into the AI and ask what to do. Never paste your account or password.', {}]],
        [['Nothing works', {'b': True}], [': follow the teacher’s demo and compute the numbers with a calculator.', {}]],
    ]})

    bl.append({'t': 'h1', 'text': 'Table 1  Check-up table (compute the ratios yourself)', 'break': True})
    rows = [[[[f"{r['key'][1]}  {r['en']}", {'b': True}]], '', '', '', '', ''] for r in RD]
    bl.append({'t': 'table', 'widths': [2266, 2300, 2300, 1100, 1100, 800], 'row_h': 720,
               'header': ['Ratio', 'Numerator (line + number)', 'Denominator (line + number)', 'Ratio (%)', 'PDF page', 'Checked ✓'], 'rows': rows})
    bl.append({'t': 'table', 'widths': [1600, 1689, 1600, 1689, 1600, 1688], 'header': None, 'row_h': 500,
               'rows': [[{'text': 'Units', 'b': True, 'fill': 'F1F5F4'}, '', {'text': 'Year column', 'b': True, 'fill': 'F1F5F4'}, '',
                         {'text': 'Consolidated?', 'b': True, 'fill': 'F1F5F4'}, '']]})
    bl.append({'t': 'p', 'runs': 'Securities = “Investment securities, net of allowance for credit losses” (= Available-for-sale securities + Held-to-maturity securities). Trading assets are a separate line: Prompt ③ asks the AI whether they should count.'})

    bl.append({'t': 'h1', 'text': 'Table 2  Stress test: 10% of deposits leave tomorrow'})
    bl.append({'t': 'table', 'widths': [3700, 3166, 3000], 'row_h': 480,
               'header': ['Numbers you need (find them in the report)', 'Amount (US$ million)', 'PDF page'],
               'rows': [['Deposits', '', ''], ['Cash and due from banks', '', ''], ['Deposits with banks', '', ''],
                        ['10% of deposits = Deposits × 10%', '', '—'], ['Cash on hand = Cash and due from banks + Deposits with banks', '', '—'],
                        ['Enough? If not, how much short, and where does the rest come from?', '', '—']]})
    bl.append({'t': 'note', 'runs': 'First copy two lines from PDF page 199: Cash and due from banks; Deposits with banks. Then fill the T-account.'})
    bl.append({'t': 'tacct', 'caption': [['T-accounts: which lines move, and by how much (minus sign for a decrease)', {'b': True}]], 'left': 'Assets', 'right': 'Liabilities and equity', 'rows': 4})
    bl.append({'t': 'table', 'widths': [1973, 1973, 1973, 1973, 1974], 'row_h': 480,
               'header': [f"{r['key'][1]} {r['en']}" for r in RD], 'rows': [['', '', '', '', '']]})
    bl.append({'t': 'p', 'runs': [['The AI’s sentences: on the statement, calculated, or inference?', {'b': True}], [' (copy three of them)', {}]]})
    bl.append({'t': 'table', 'widths': [5866, 1800, 2200], 'row_h': 560,
               'header': ['What the AI said', 'On the statement / calculated / inference', 'Basis (page or reason)'], 'rows': [['', '', ''], ['', '', ''], ['', '', '']]})

    bl.append({'t': 'h1', 'text': 'Table 3  Spot-check log (three cells against the original)'})
    bl.append({'t': 'table', 'widths': [2000, 1300, 2266, 1300, 3000], 'row_h': 560,
               'header': ['Cell (which number)', 'PDF page', 'Number in the original', 'Right or wrong', 'Why (units / year column / consolidated / page numbering / other)'],
               'rows': [['', '', '', '', ''], ['', '', '', '', ''], ['', '', '', '', '']]})
    bl.append({'t': 'h1', 'text': 'Table 4  Disclosure sentence (copy it and fill in the blanks)'})
    bl.append({'t': 'note', 'runs': [[DISCLOSE_EN, {'b': True}]]})
    bl.append({'t': 'table', 'widths': [9866], 'row_h': 560, 'header': None, 'rows': [['']]})
    return {'lang': 'en', 'title': 'Bank Check-up Worksheet: JPMorgan Chase & Co.', 'header': 'Money and Banking, AI session 2 | Student worksheet', 'blocks': bl}

# ================= 回家作業卡 =================
def homework_zh():
    bl = [{'t': 'title', 'text': '回家作業卡：第二次 AI 專題的第一張表'},
          {'t': 'subtitle', 'text': '貨幣銀行學 AI 第二輪｜格式、分組與截止日以王老師 e學苑 公告為準'},
          {'t': 'h2', 'text': '做什麼（四件事）'},
          {'t': 'numbered', 'items': [
              [['挑兩家銀行：一家台灣、一家外國。', {'b': True}], ['台灣的要銀行本身的財報（公開資訊觀測站或銀行官網），不要金控的合併報表；外國的找年報或 10-K（公司官網或 SEC EDGAR）。', {}]],
              [['第一張表：', {'b': True}], ['用 agent 開同一個課程資料夾做 任務.md 的任務三（把兩家的財報 PDF 放進 data/，或把官方網址給 agent），兩家各做五個比率，每格附 PDF 頁碼；再用體檢表範本自己算一次對照。沒有 agent 就用聊天版貼提示語 ③，自己算。', {}]],
              [['抽三格回原文查', {'b': True}], ['，寫下結果：對或錯、單位、年度、合併或個體。', {}]],
              [['深度研究初稿：', {'b': True}], ['用 AI 的深度研究功能（ChatGPT、Gemini、Claude 都有）寫兩家經營方式的比較初稿（提示語 ⑤）；挑三句回來源查，標「有出處／沒出處」。', {}]],
          ]},
          {'t': 'bullets', 'items': ['把提示語 ③ 裡的銀行名、報表日期、科目名換成那家財報上的字；淨放款與證券投資各算了哪幾列要寫明。', '深度研究功能不能用的話，改用一般對話，並附上你自己找到的來源。']},
          {'t': 'h2', 'text': '交什麼'},
          {'t': 'p', 'runs': '表格＋抽查紀錄＋初稿與三句查核＋揭露句。'},
          {'t': 'prompt', 'label': '提示語 ⑤（回家：深度研究）', 'lines': P[('zh', '⑤')], 'key': ('zh', '⑤')},
          {'t': 'h2', 'text': '揭露句（附在作業最後）'},
          {'t': 'note', 'runs': [[DISCLOSE_ZH, {'b': True}]]},
          {'t': 'p', 'runs': [['格式、分組與截止日以王老師 e學苑 公告為準。', {'b': True}]]}]
    return {'lang': 'zh', 'title': '回家作業卡', 'header': '貨幣銀行學 AI 第二輪｜回家作業卡', 'blocks': bl, 'base_size': 22}

def homework_en():
    bl = [{'t': 'title', 'text': 'Homework Card: the First Table of AI Project 2'},
          {'t': 'subtitle', 'text': 'Money and Banking, AI session 2 | Format, groups and due date: see Prof. Wang’s announcement on e-Learning'},
          {'t': 'h2', 'text': 'What to do (four things)'},
          {'t': 'numbered', 'items': [
              [['Pick two banks: one in Taiwan, one abroad.', {'b': True}], [' For the Taiwan bank, use the bank’s own financial report (Market Observation Post System, or the bank’s website), not the financial holding company’s consolidated report. For the foreign bank, use its annual report or 10-K (company website or SEC EDGAR).', {}]],
              [['First table:', {'b': True}], [' open the same course folder with your agent and do Task 3 in TASK.md (put both banks’ report PDFs into data/, or give the agent the official links). Compute the five ratios for both banks with the PDF page for every cell, then compute them once more yourselves with the check-up template. No agent? Use the chat version with Prompt ③ and compute the ratios yourselves.', {}]],
              [['Check three cells against the original', {'b': True}], [' and write down the result: right or wrong, units, year, consolidated or not.', {}]],
              [['Deep-research draft:', {'b': True}], [' use an AI’s deep-research mode (ChatGPT, Gemini and Claude all have one) to draft a comparison of how the two banks make money (Prompt ⑤). Pick three sentences, check them against the sources, and mark each “sourced” or “not sourced”.', {}]],
          ]},
          {'t': 'bullets', 'items': ['Replace the bank name, statement date and line names in Prompt ③ with the words printed in that bank’s report, and state which lines you counted as net loans and as securities.', 'If deep-research mode is not available, use a normal chat instead and attach the sources you found yourselves.']},
          {'t': 'h2', 'text': 'What to hand in'},
          {'t': 'p', 'runs': 'The table + the spot-check log + the draft with its three checked sentences + the disclosure sentence.'},
          {'t': 'prompt', 'label': 'Prompt ⑤ (Homework: deep research)', 'lines': P[('en', '⑤')], 'key': ('en', '⑤')},
          {'t': 'h2', 'text': 'Disclosure sentence (put it at the end)'},
          {'t': 'note', 'runs': [[DISCLOSE_EN, {'b': True}]]},
          {'t': 'p', 'runs': [['Format, groups and due date: as announced by Prof. Wang on e-Learning.', {'b': True}]]}]
    return {'lang': 'en', 'title': 'Homework Card', 'header': 'Money and Banking, AI session 2 | Homework card', 'blocks': bl, 'base_size': 22}

# ================= 壓力測試題與參考答案 =================
def stress_zh():
    A = CHB['stress']['A_deposit_run_10pct']; A2 = CHB['stress']['A2_deposit_run_10pct_fire_sale_10pct']; Bs = CHB['stress']['B_rate_shock_5pct']
    JA = JPM['stress']['A_deposit_run_10pct']; JB = JPM['stress']['B_rate_shock_5pct']
    r0 = CHB['ratios_pct']; jr0 = JPM['ratios_pct']
    rr = lambda d: '／'.join(pct(d[k]) for k in ['r1', 'r2', 'r3', 'r4', 'r5'])
    jleft = JA['liquid_assets_before'] - JA['liquid_used']
    bl = [{'t': 'title', 'text': '壓力測試題與參考答案：彰化銀行'},
          {'t': 'subtitle', 'text': '貨幣銀行學 AI 第二輪｜第一部分給學生（題目＋空白 T 字帳）；第二部分給老師（參考答案），兩部分之間分頁'},
          {'t': 'h1', 'text': '第一部分　題目（學生版）'},
          {'t': 'p', 'runs': f"資料：彰化銀行 114 年度財務報告的合併資產負債表（PDF 第 1 頁，頁面印的頁碼是 8），114 年 12 月 31 日那一欄，單位新臺幣千元。數字自己從財報找，每個都寫頁碼。"},
          {'t': 'h2', 'text': '情境 A：明天有一成的存款被提走'},
          {'t': 'p', 'runs': '銀行先用「現金及約當現金」與「存放央行及拆借銀行同業」付；不夠的賣證券（先假設照帳面賣，不虧）。'},
          {'t': 'numbered', 'items': ['一成存款是多少（存款及匯款 × 10%）？', '手上的錢（現金及約當現金＋存放央行及拆借銀行同業）有多少？夠不夠？不夠的話差多少、要從哪裡來？',
                                      '用 T 字帳列出哪幾行會動、各動多少；權益會不會變？', '五個比率之後各變成多少？跟之前比，哪一個變最多？',
                                      '這一題裡，哪些事是資產負債表上沒有、要靠推論的？寫兩件。']},
          {'t': 'table', 'widths': [3700, 3166, 3000], 'row_h': 460, 'header': ['數字', '金額（千元）', 'PDF 頁碼'],
           'rows': [['存款及匯款', '', ''], ['現金及約當現金', '', ''], ['存放央行及拆借銀行同業', '', ''], ['一成存款', '', '—'], ['手上的錢', '', '—'], ['差多少（或剩多少）', '', '—']]},
          {'t': 'tacct', 'caption': [['情境 A 的 T 字帳', {'b': True}]], 'left': '資產', 'right': '負債與權益', 'rows': 4},
          {'t': 'h2', 'text': '情境 B：利率上升，債券價格跌 5%'},
          {'t': 'p', 'runs': '彰化銀行的證券分成三行，名字就告訴你損失會跑去哪裡：「透過損益」的跌了算進當期損益；「透過其他綜合損益」的跌了直接進權益；「按攤銷後成本衡量」的照原價記，跌了在資產負債表上看不到。'},
          {'t': 'numbered', 'items': ['三行金融資產各跌多少（× 5%）？', '哪一行的損失進損益、哪一行進權益、哪一行在表上看不到？',
                                      '表上認列的損失合計多少？權益變成多少？權益 ÷ 總資產變成多少？', '如果看不到的那一行也認列，權益 ÷ 總資產又變成多少？',
                                      '想一想：矽谷銀行出事的那一格，是這三種裡的哪一種？']},
          {'t': 'table', 'widths': [3866, 2000, 2000, 2000], 'row_h': 520, 'header': ['科目', '帳面（千元）', '跌 5%（千元）', '進損益／進權益／看不到'],
           'rows': [[L(CHB, 'fvtpl'), '', '', ''], [L(CHB, 'fvoci'), '', '', ''], [L(CHB, 'ac_debt'), '', '', '']]},
          {'t': 'tacct', 'caption': [['情境 B 的 T 字帳（只寫表上認列的）', {'b': True}]], 'left': '資產', 'right': '負債與權益', 'rows': 4},
          {'t': 'pagebreak'},
          {'t': 'h1', 'text': '第二部分　參考答案（老師版）'},
          {'t': 'p', 'runs': f"數字由同一支計算程式產生、逐格對過財報原文；彰銀單位千元、JPMorgan Chase 單位百萬美元。之前的五個比率：彰銀 {rr(r0)}；JPMorgan Chase {rr(jr0)}（%，依序為放款÷資產／證券÷資產／放款÷存款／存款÷負債／權益÷資產）。"},
          {'t': 'note', 'runs': [['教學假設：', {'b': True}], ['兩列流動資產全部可動用、缺口照帳面賣證券、不借款、不算稅；情境 B 整類資產一律跌 5%。', {}]]},
          {'t': 'h2', 'text': '情境 A：一成存款被提走'},
          {'t': 'table', 'widths': [3000, 3600, 3266], 'right_cols': [], 'header': ['', '彰銀（千元）', 'JPMorgan Chase（百萬美元）'], 'first_col_bold': True,
           'rows': [['一成存款', f(A['deposit_outflow']), f(JA['deposit_outflow'])],
                    ['手上流動資產（現金＋存放央行／同業）', f(A['liquid_assets_before']), f(JA['liquid_assets_before'])],
                    ['夠不夠', [['不夠，差 ' + f(A['shortfall_after_liquid']), {'b': True}], [' → 要賣證券或向同業／央行借', {}]], [['夠', {'b': True}], ['，還剩 ' + f(jleft), {}]]],
                    ['T 字帳：資產減', f"現金＋存放央行 −{f(A['liquid_used'])}；證券 −{f(A['securities_sold_book'])}", f"Cash and due from banks＋Deposits with banks −{f(JA['liquid_used'])}"],
                    ['T 字帳：負債減', f"存款 −{f(A['deposit_outflow'])}", f"Deposits −{f(JA['deposit_outflow'])}"],
                    ['權益', '不變', '不變'],
                    ['五個比率之後（%）', rr(A['ratios_after']), rr(JA['ratios_after'])]]},
          {'t': 'p', 'runs': [['延伸（只給老師）：', {'b': True}], [f"若證券只能以帳面九折賣出，彰銀要賣帳面 {f(A2['securities_sold_book'])} 才拿得到 {f(A2['shortfall_after_liquid'])}，損失 {f(A2['loss_to_equity'])} 進權益，權益比 {pct(A2['ratios_after']['r5'])}%。JPMorgan Chase 手上的錢就夠付，不必賣證券，九折與否不影響。", {}]]},
          {'t': 'h2', 'text': '情境 B：債券價格跌 5%'},
          {'t': 'table', 'widths': [3000, 3600, 3266], 'header': ['', '彰銀（千元）', 'JPMorgan Chase（百萬美元）'], 'first_col_bold': True,
           'rows': [['進損益：透過損益按公允價值衡量', f(Bs['recognized_losses'][L(CHB, 'fvtpl')]), '（Trading assets 不在此題）'],
                    ['進權益（其他綜合損益）：透過其他綜合損益按公允價值衡量／AFS', f(Bs['recognized_losses'][L(CHB, 'fvoci')]), f(JB['recognized_losses'][L(JPM, 'afs')])],
                    ['認列合計 → 權益變成', [[f"{f(Bs['recognized_total'])} → ", {}], [f(Bs['equity_after_recognized']), {'b': True}], [f"（權益比 {pct(r0['r5'])}→{pct(Bs['r5_after_recognized'])}）", {}]],
                     [[f"{f(JB['recognized_total'])} → ", {}], [f(JB['equity_after_recognized']), {'b': True}], [f"（{pct(jr0['r5'])}→{pct(JB['r5_after_recognized'])}）", {}]]],
                    ['表上看不到：攤銷後成本／HTM', f"{f(Bs['hidden_total'])}（若也認列→權益比 {pct(Bs['r5_if_hidden_also_marked'])}）", f"{f(JB['hidden_total'])}（若也認列→{pct(JB['r5_if_hidden_also_marked'])}）"],
                    ['對照真實數字', '—', f"JPM 自己的 HTM 未實現損失 {f(JPM['firm_reported']['htm_gross_unrealized_losses'])}（10-K 紙本 p.229，PDF 第 261 頁）＝權益 {JPM['variants']['htm_unrealized_loss_pct_of_equity']}%"]]},
          {'t': 'p', 'runs': [['接回矽谷銀行：', {'b': True}], [f"HTM 帳面與公允價值差 {f(SVB['variants']['htm_fair_value_gap'])} vs 權益 {f(SVB['lines']['equity']['value'])}（{SVB['variants']['htm_gap_pct_of_equity']}%）→ 若全部認列，權益剩 {f(SVB['variants']['equity_if_htm_gap_recognized'])}、權益比 {SVB['variants']['r5_if_htm_gap_recognized']}%（百萬美元，2022-12-31）。矽谷銀行出事的就是「表上看不到」那一格。", {}]]},
          {'t': 'h2', 'text': '哪些句子是推論（表上沒有）'},
          {'t': 'bullets', 'items': [
              '情境 A：證券賣了會不會虧（我們先假設照帳面賣）；向同業或央行借不借得到；存戶為什麼要提款。',
              '情境 B：利率會不會真的漲、債券會跌多少（5% 是我們設的情境）；看不到的那一行損失會不會真的實現（持有到期就不必賣）。',
              '判準（三類）：指得出報表哪一頁、哪一列的，是「表上」；用表上的數字照算式算出來的，是「算的」；兩樣都不是的，不管寫得多肯定，都是「推論」。',
          ]}]
    return {'lang': 'zh', 'title': '壓力測試題與參考答案', 'header': '貨幣銀行學 AI 第二輪｜壓力測試題與參考答案', 'blocks': bl}

def stress_en():
    JA = JPM['stress']['A_deposit_run_10pct']; JA2 = JPM['stress']['A2_deposit_run_10pct_fire_sale_10pct']; JB = JPM['stress']['B_rate_shock_5pct']
    jr0 = JPM['ratios_pct']
    rr = lambda d: ' / '.join(pct(d[k]) for k in ['r1', 'r2', 'r3', 'r4', 'r5'])
    jleft = JA['liquid_assets_before'] - JA['liquid_used']
    bl = [{'t': 'title', 'text': 'Stress-Test Scenarios and Answer Key: JPMorgan Chase & Co.'},
          {'t': 'subtitle', 'text': 'Money and Banking, AI session 2 | Part 1 for students (questions + blank T-accounts); Part 2 for the teacher (answer key), on a new page'},
          {'t': 'h1', 'text': 'Part 1  Questions (student version)'},
          {'t': 'p', 'runs': 'Source: JPMorgan Chase & Co. 2025 Annual Report, Consolidated balance sheets (PDF page 199, printed as page 167 in the Form 10-K numbering), December 31, 2025 column, US$ million. Find every number yourself and write its page.'},
          {'t': 'h2', 'text': 'Scenario A: 10% of deposits are withdrawn tomorrow'},
          {'t': 'p', 'runs': 'The bank pays first out of “Cash and due from banks” and “Deposits with banks”; anything still missing comes from selling securities (assume for now they sell at carrying amount, no loss).'},
          {'t': 'numbered', 'items': ['How much is 10% of deposits (Deposits × 10%)?', 'How much cash is on hand (Cash and due from banks + Deposits with banks)? Is it enough? If not, how much is missing and where does it come from?',
                                      'Show in T-accounts which lines move and by how much. Does equity change?', 'What do the five ratios become? Which one moves the most?',
                                      'Which parts of this answer are not on the balance sheet and have to be inferred? Name two.']},
          {'t': 'table', 'widths': [3700, 3166, 3000], 'row_h': 460, 'header': ['Number', 'Amount (US$ million)', 'PDF page'],
           'rows': [['Deposits', '', ''], ['Cash and due from banks', '', ''], ['Deposits with banks', '', ''], ['10% of deposits', '', '—'], ['Cash on hand', '', '—'], ['Short by (or left over)', '', '—']]},
          {'t': 'tacct', 'caption': [['Scenario A T-accounts', {'b': True}]], 'left': 'Assets', 'right': 'Liabilities and equity', 'rows': 4},
          {'t': 'h2', 'text': 'Scenario B: interest rates rise and bond prices fall 5%'},
          {'t': 'p', 'runs': 'JPMorgan Chase reports its investment securities in two lines. “Available-for-sale securities” are carried at fair value, so a price fall shows up in equity (other comprehensive income). “Held-to-maturity securities” are carried at amortized cost, so a price fall does not show on the face of the balance sheet. Trading assets are left out of this question.'},
          {'t': 'numbered', 'items': ['How much does each line fall (× 5%)?', 'Which loss shows up in equity, and which one cannot be seen on the balance sheet?',
                                      'After the recognized loss, what is equity, and what is Equity ÷ Total assets?', 'If the hidden loss were recognized too, what would Equity ÷ Total assets be?',
                                      'Think: at Silicon Valley Bank, which of these two kinds of line was the problem?']},
          {'t': 'table', 'widths': [3866, 2000, 2000, 2000], 'row_h': 520, 'header': ['Line', 'Carrying amount (US$ million)', 'Fall of 5% (US$ million)', 'Equity / not on the face'],
           'rows': [[L(JPM, 'afs'), '', '', ''], [L(JPM, 'htm'), '', '', '']]},
          {'t': 'tacct', 'caption': [['Scenario B T-accounts (recognized loss only)', {'b': True}]], 'left': 'Assets', 'right': 'Liabilities and equity', 'rows': 4},
          {'t': 'pagebreak'},
          {'t': 'h1', 'text': 'Part 2  Answer key (teacher version)'},
          {'t': 'p', 'runs': f"Numbers come from the same calculation script and were checked cell by cell against the report; US$ million. Ratios before the shock: {rr(jr0)} (%, in order: Loans ÷ Total assets / Securities ÷ Total assets / Loans ÷ Deposits / Deposits ÷ Total liabilities / Equity ÷ Total assets)."},
          {'t': 'note', 'runs': [['Teaching assumptions: ', {'b': True}], ['both liquid lines can be used in full, any shortfall is covered by selling securities at carrying amount, no borrowing, no tax; in Scenario B every security in a class falls 5%.', {}]]},
          {'t': 'h2', 'text': 'Scenario A: 10% of deposits withdrawn'},
          {'t': 'table', 'widths': [3800, 6066], 'header': ['', 'JPMorgan Chase (US$ million)'], 'first_col_bold': True,
           'rows': [['10% of deposits', f(JA['deposit_outflow'])],
                    ['Cash on hand (Cash and due from banks + Deposits with banks)', f(JA['liquid_assets_before'])],
                    ['Enough?', [['Yes', {'b': True}], [f", {f(jleft)} left over", {}]]],
                    ['T-account: assets down', f"Cash and due from banks + Deposits with banks −{f(JA['liquid_used'])}"],
                    ['T-account: liabilities down', f"Deposits −{f(JA['deposit_outflow'])}"],
                    ['Equity', 'Unchanged'],
                    ['Five ratios after (%)', rr(JA['ratios_after'])]]},
          {'t': 'p', 'runs': [['Extension (teacher only): ', {'b': True}], [f"if securities could only be sold at a 10% discount, nothing changes for JPMorgan Chase — the cash on hand already covers the outflow, so no securities are sold (securities sold: {JA2['securities_sold_book']}; loss to equity: {JA2['loss_to_equity']}).", {}]]},
          {'t': 'h2', 'text': 'Scenario B: bond prices fall 5%'},
          {'t': 'table', 'widths': [3800, 6066], 'header': ['', 'JPMorgan Chase (US$ million)'], 'first_col_bold': True,
           'rows': [['Into equity (other comprehensive income): Available-for-sale securities', f(JB['recognized_losses'][L(JPM, 'afs')])],
                    ['Recognized total → equity becomes', [[f"{f(JB['recognized_total'])} → ", {}], [f(JB['equity_after_recognized']), {'b': True}], [f" (Equity ÷ Total assets {pct(jr0['r5'])} → {pct(JB['r5_after_recognized'])})", {}]]],
                    ['Not on the face: Held-to-maturity securities', f"{f(JB['hidden_total'])} (if also recognized → {pct(JB['r5_if_hidden_also_marked'])})"],
                    ['Trading assets', 'Not in this question'],
                    ['Compare with the real number', f"The Firm’s own HTM gross unrealized losses: {f(JPM['firm_reported']['htm_gross_unrealized_losses'])} (Note 10, PDF page 261 / printed page 229) = {JPM['variants']['htm_unrealized_loss_pct_of_equity']}% of equity"]]},
          {'t': 'p', 'runs': [['Back to Silicon Valley Bank: ', {'b': True}], [f"the gap between the HTM carrying amount and its fair value, {f(SVB['variants']['htm_fair_value_gap'])}, vs stockholders’ equity {f(SVB['lines']['equity']['value'])} ({SVB['variants']['htm_gap_pct_of_equity']}%) → if all recognized, equity would be {f(SVB['variants']['equity_if_htm_gap_recognized'])} and Equity ÷ Total assets {SVB['variants']['r5_if_htm_gap_recognized']}% (US$ million, December 31, 2022). SVB’s problem sat in the line you cannot see on the face.", {}]]},
          {'t': 'h2', 'text': 'Which sentences are inference (not on the statement)'},
          {'t': 'bullets', 'items': [
              'Scenario A: whether selling securities would cause a loss (we assumed carrying amount); whether the bank could borrow from other banks or the central bank; why depositors are withdrawing.',
              'Scenario B: whether rates actually rise and how far bond prices fall (5% is our assumption); whether the hidden held-to-maturity loss is ever realized (a bank that holds to maturity need not sell).',
              'Rule of thumb (three labels): if the sentence points to a page and a line of the statement, it is “on the statement”; if it is computed from those numbers with a stated formula, it is “calculated”; if neither, however confident it sounds, it is “inference”.',
          ]}]
    return {'lang': 'en', 'title': 'Stress-Test Scenarios and Answer Key', 'header': 'Money and Banking, AI session 2 | Stress-test scenarios and answer key', 'blocks': bl}

def split_stress(spec, lang):
    """洄瀾 11/15 微調：題目與答案拆兩檔（整夾上傳 e學苑 時不會把答案一起給學生）。"""
    bl = spec['blocks']; k = next(i for i, b in enumerate(bl) if b['t'] == 'pagebreak')
    stu, tea = bl[3:k], bl[k + 2:]   # 去掉原標題、副標、第一部分 h1；答案從 h1 之後
    if lang == 'zh':
        s = {'lang': 'zh', 'title': '壓力測試題', 'header': '貨幣銀行學 AI 第二輪｜壓力測試題',
             'blocks': [{'t': 'title', 'text': '壓力測試題：彰化銀行'}, {'t': 'subtitle', 'text': '貨幣銀行學 AI 第二輪｜2026-11-16｜先在紙上用 T 字帳算，再問 AI'}] + stu}
        t = {'lang': 'zh', 'title': '壓力測試參考答案（老師版）', 'header': '貨幣銀行學 AI 第二輪｜壓力測試參考答案（老師版，不給學生）',
             'blocks': [{'t': 'title', 'text': '壓力測試參考答案（老師版）：彰化銀行'}, {'t': 'subtitle', 'text': '貨幣銀行學 AI 第二輪｜對應「壓力測試題.docx」的情境 A、B｜不要放在學生看得到的地方'}] + tea}
        return {'壓力測試題': s, '壓力測試參考答案-老師版': t}
    s = {'lang': 'en', 'title': 'Stress-Test Scenarios', 'header': 'Money and Banking, AI session 2 | Stress-test scenarios',
         'blocks': [{'t': 'title', 'text': 'Stress-Test Scenarios: JPMorgan Chase & Co.'}, {'t': 'subtitle', 'text': 'Money and Banking, AI session 2 | 2026-11-18 | Work it out on paper with T-accounts first, then ask the AI'}] + stu}
    t = {'lang': 'en', 'title': 'Stress-Test Answer Key (teacher)', 'header': 'Money and Banking, AI session 2 | Stress-test answer key (teacher only)',
         'blocks': [{'t': 'title', 'text': 'Stress-Test Answer Key (teacher version): JPMorgan Chase & Co.'}, {'t': 'subtitle', 'text': 'Money and Banking, AI session 2 | Answers to Scenarios A and B in “Stress-Test-Scenarios.docx” | Do not post where students can see it'}] + tea}
    return {'Stress-Test-Scenarios': s, 'Stress-Test-Answer-Key-Teacher': t}

# ================= HTML（練習單） =================
CSS = """
:root{--bg:#FAF8F2;--surface:#FFFFFF;--surface-2:#F1F5F4;--ink:#132525;--ink-soft:#3E5656;--line:#D6E2E1;
--teal:#0E7C7B;--teal-tint:#E2F0EF;--gold:#D9A441;--gold-tint:#FBF0D9;--code-bg:#EEF3F2;color-scheme:light;
--zh:"Microsoft JhengHei","Noto Sans TC","PingFang TC",system-ui,sans-serif;--mono:Consolas,"Cascadia Mono",Menlo,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#0B1A1A;--surface:#112424;--surface-2:#173030;--ink:#E6F2F2;--ink-soft:#BBD0CF;--line:#26403F;--teal:#5CC8C6;--teal-tint:#123A39;--gold:#E8B85A;--gold-tint:#3A2F18;--code-bg:#0D1F1F;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0B1A1A;--surface:#112424;--surface-2:#173030;--ink:#E6F2F2;--ink-soft:#BBD0CF;--line:#26403F;--teal:#5CC8C6;--teal-tint:#123A39;--gold:#E8B85A;--gold-tint:#3A2F18;--code-bg:#0D1F1F;color-scheme:dark}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 var(--zh)}
main{max-width:980px;margin:0 auto;padding:24px 16px 64px}
h1.title{font-size:1.7rem;line-height:1.3;margin:.2em 0;color:var(--teal)}
.sub{color:var(--ink-soft);margin:0 0 1.2em}
h2{font-size:1.3rem;margin:1.8em 0 .5em;color:var(--teal);border-bottom:2px solid var(--line);padding-bottom:.2em}
h3{font-size:1.08rem;margin:1.2em 0 .4em}
.tw{overflow-x:auto;margin:.6em 0 1em}
table{border-collapse:collapse;width:100%;background:var(--surface)}
th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;text-align:left}
th{background:var(--teal-tint)}
td.blank{height:3em}
.note{background:var(--gold-tint);border-left:5px solid var(--gold);padding:10px 14px;margin:1em 0;border-radius:4px}
.prompt{position:relative;background:var(--code-bg);border-left:5px solid var(--teal);border-radius:4px;margin:.4em 0 1.2em}
.prompt pre{margin:0;padding:14px 16px;white-space:pre-wrap;word-break:break-word;font:15px/1.7 var(--zh)}
.prompt.en pre{font-family:var(--mono)}
.plabel{font-weight:700;color:var(--teal);margin-top:1em}
.copy{position:absolute;top:6px;right:6px;font:13px var(--zh);padding:4px 10px;border:1px solid var(--teal);background:var(--surface);color:var(--teal);border-radius:4px;cursor:pointer}
details.stuck{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:8px 14px;margin:1em 0}
details.stuck summary{cursor:pointer;font-weight:700}
.tacct{display:grid;grid-template-columns:1fr 1fr;border-top:3px solid var(--ink);max-width:640px;margin:.4em 0 1em}
.tacct div{min-height:9em;padding:6px 10px}.tacct div:first-child{border-right:3px solid var(--ink)}
.tacct b{display:block;text-align:center}
@media print{.copy{display:none}details.stuck{display:block}details.stuck>*{display:block}}
"""

def runs_html(r):
    if r is None: return ''
    if isinstance(r, str): return html.escape(r)
    out = []
    for x in r:
        if isinstance(x, str): out.append(html.escape(x)); continue
        t, o = x; s = html.escape(t)
        if o.get('b'): s = f'<b>{s}</b>'
        out.append(s)
    return ''.join(out)

def cell_html(c):
    if isinstance(c, dict): return runs_html(c.get('text', ''))
    return runs_html(c)

def to_html(spec, stuck_heading):
    zh = spec['lang'] == 'zh'
    out = [f'<!doctype html><html lang="{"zh-Hant-TW" if zh else "en"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(spec["title"])}</title><style>{CSS}</style></head><body><main>']
    blocks = spec['blocks']; i = 0; in_stuck = False
    copy_lbl = '複製' if zh else 'Copy'; copied = '已複製' if zh else 'Copied'
    for b in blocks:
        t = b['t']
        if t == 'h1' and in_stuck:
            out.append('</details>'); in_stuck = False
        if t == 'title': out.append(f'<h1 class="title">{runs_html(b["text"])}</h1>')
        elif t == 'subtitle': out.append(f'<p class="sub">{runs_html(b["text"])}</p>')
        elif t == 'h1':
            if b['text'] == stuck_heading:
                out.append(f'<h2>{html.escape(b["text"])}</h2><details class="stuck"><summary>{"點開看常見狀況" if zh else "Open for common problems"}</summary>'); in_stuck = True
            else: out.append(f'<h2>{html.escape(b["text"])}</h2>')
        elif t == 'h2': out.append(f'<h3>{html.escape(b["text"])}</h3>')
        elif t == 'p': out.append(f'<p>{runs_html(b["runs"])}</p>')
        elif t == 'note': out.append(f'<div class="note">{runs_html(b["runs"])}</div>')
        elif t in ('bullets', 'numbered'):
            tag = 'ul' if t == 'bullets' else 'ol'
            out.append(f'<{tag}>' + ''.join(f'<li>{runs_html(it)}</li>' for it in b['items']) + f'</{tag}>')
        elif t == 'prompt':
            out.append(f'<div class="plabel">{html.escape(b["label"])}</div><div class="prompt{"" if zh else " en"}"><button type="button" class="copy" data-done="{copied}">{copy_lbl}</button><pre>' + html.escape('\n'.join(b['lines'])) + '</pre></div>')
        elif t == 'table':
            h = ''
            if b.get('header'): h = '<tr>' + ''.join(f'<th>{runs_html(x)}</th>' for x in b['header']) + '</tr>'
            rows = ''
            for r in b['rows']:
                rows += '<tr>' + ''.join((f'<td class="blank"></td>' if (c == '' or c is None) else f'<td>{cell_html(c)}</td>') for c in r) + '</tr>'
            out.append(f'<div class="tw"><table>{h}{rows}</table></div>')
        elif t == 'tacct':
            if b.get('caption'): out.append(f'<p>{runs_html(b["caption"])}</p>')
            out.append(f'<div class="tacct"><div><b>{html.escape(b["left"])}</b></div><div><b>{html.escape(b["right"])}</b></div></div>')
        elif t == 'pagebreak': pass
    if in_stuck: out.append('</details>')
    out.append("""</main><script>
document.querySelectorAll('.copy').forEach(function(btn){btn.addEventListener('click',function(){
var txt=btn.parentNode.querySelector('pre').textContent;var lbl=btn.textContent;
function ok(){btn.textContent=btn.dataset.done;setTimeout(function(){btn.textContent=lbl},1500)}
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(txt).then(ok,function(){fallback()})}else{fallback()}
function fallback(){var ta=document.createElement('textarea');ta.value=txt;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');ok()}catch(e){}document.body.removeChild(ta)}
})});
</script></body></html>""")
    return '\n'.join(out)

# ================= Excel =================
def build_xlsx(lang, teacher, path):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    zh = lang == 'zh'
    FN = 'Microsoft JhengHei' if zh else 'Arial'
    bank = CHB if zh else JPM
    wb = Workbook(); ws = wb.active; ws.title = '體檢表' if zh else 'Check-up'
    thin = Side(style='thin', color='9AA9A8'); bd = Border(left=thin, right=thin, top=thin, bottom=thin)
    yellow = PatternFill('solid', fgColor='FFF2B3'); head = PatternFill('solid', fgColor='E2F0EF'); grey = PatternFill('solid', fgColor='F1F5F4')
    inp = Font(name=FN, color='0000FF', size=11); base = Font(name=FN, size=11); bold = Font(name=FN, bold=True, size=11)
    wrap = Alignment(wrap_text=True, vertical='top')
    ws['A1'] = '銀行體檢表' if zh else 'Bank Check-up Table'; ws['A1'].font = Font(name=FN, bold=True, size=15, color='0E5C5B')
    ws['A2'] = ('黃底格子是你要填的（藍字）；「比率」欄自動算＝分子金額 ÷ 分母金額。科目名照今天上課這家（彰化銀行）財報的原字；回家作業換銀行，就改成那家財報的原字。'
                if zh else 'Yellow cells are yours to fill in (blue text); the Ratio column computes itself = numerator amount ÷ denominator amount. Line names are as printed in today’s bank (JPMorgan Chase); for the homework, replace them with the names printed in your bank’s report.')
    ws['A2'].font = Font(name=FN, size=10, color='3E5656'); ws['A2'].alignment = wrap; ws.merge_cells('A2:I2'); ws.row_dimensions[2].height = 48
    ws['A3'] = '銀行名稱：' if zh else 'Bank:'; ws['A3'].font = bold
    ws['B3'] = CHB['name_zh'] if zh else JPM['name_en']; ws['B3'].font = inp; ws['B3'].fill = yellow; ws.merge_cells('B3:E3')
    hdr = (['比率', '分子科目', '分子金額', '分子頁碼', '分母科目', '分母金額', '分母頁碼', '比率', '我查過'] if zh else
           ['Ratio', 'Numerator line', 'Numerator amount', 'Numerator page', 'Denominator line', 'Denominator amount', 'Denominator page', 'Ratio', 'Checked'])
    for j, h in enumerate(hdr, 1):
        c = ws.cell(row=4, column=j, value=h); c.font = bold; c.fill = head; c.border = bd; c.alignment = wrap
    if zh:
        sec_label = '證券投資（下方三行相加）'
        lines = [(L(CHB, 'loans'), L(CHB, 'assets')), (sec_label, L(CHB, 'assets')), (L(CHB, 'loans'), L(CHB, 'deposits')),
                 (L(CHB, 'deposits'), L(CHB, 'liabilities')), (L(CHB, 'equity'), L(CHB, 'assets'))]
    else:
        lines = [(L(JPM, 'loans'), L(JPM, 'assets')), (L(JPM, 'investment_securities'), L(JPM, 'assets')), (L(JPM, 'loans'), L(JPM, 'deposits')),
                 (L(JPM, 'deposits'), L(JPM, 'liabilities')), (L(JPM, 'equity'), L(JPM, 'assets'))]
    for i, (r, (nl, dl)) in enumerate(zip(RD, lines)):
        row = 5 + i
        vals = [f"{r['key'][1]}　{r['zh']}" if zh else f"{r['key'][1]}  {r['en']}", nl, None, None, dl, None, None,
                f'=IF(OR(C{row}="",F{row}="",F{row}=0),"",C{row}/F{row})', None]
        for j, v in enumerate(vals, 1):
            c = ws.cell(row=row, column=j, value=v); c.border = bd; c.alignment = wrap; c.font = base
            if j in (3, 4, 6, 7, 9): c.fill = yellow; c.font = inp
            if j in (3, 6): c.number_format = '#,##0'
            if j == 8: c.number_format = '0.00%'; c.font = bold
        ws.row_dimensions[row].height = 36
    if zh:
        # 證券投資小計
        ws['A11'] = '證券投資＝下面三行相加（財報沒有「證券投資」這一列）'; ws['A11'].font = bold; ws.merge_cells('A11:I11')
        for j, h in enumerate(['', '科目', '金額', '頁碼'], 1):
            c = ws.cell(row=12, column=j, value=h or None);
            if h: c.font = bold; c.fill = head; c.border = bd
        for k, key in enumerate(['fvtpl', 'fvoci', 'ac_debt']):
            row = 13 + k
            ws.cell(row=row, column=2, value=L(CHB, key)).border = bd
            ws.cell(row=row, column=2).alignment = wrap; ws.cell(row=row, column=2).font = base
            for col in (3, 4):
                c = ws.cell(row=row, column=col); c.fill = yellow; c.font = inp; c.border = bd
            ws.cell(row=row, column=3).number_format = '#,##0'
            ws.row_dimensions[row].height = 36
        ws['B16'] = '小計（自動）'; ws['B16'].font = bold; ws['B16'].border = bd
        ws['C16'] = '=IF(COUNT(C13:C15)=0,"",SUM(C13:C15))'; ws['C16'].number_format = '#,##0'; ws['C16'].font = bold; ws['C16'].border = bd
        ws['C6'] = '=C16'; ws['C6'].fill = grey; ws['C6'].font = bold
        meta_row = 18
    else:
        ws['A11'] = 'Check: Available-for-sale + Held-to-maturity should equal “Investment securities, net” (row 6). Trading assets are not included.'; ws['A11'].font = bold; ws.merge_cells('A11:I11')
        for j, h in enumerate(['', 'Line', 'Amount', 'Page'], 1):
            if h:
                c = ws.cell(row=12, column=j, value=h); c.font = bold; c.fill = head; c.border = bd
        for k, key in enumerate(['afs', 'htm']):
            row = 13 + k
            ws.cell(row=row, column=2, value=L(JPM, key)).border = bd; ws.cell(row=row, column=2).font = base
            for col in (3, 4):
                c = ws.cell(row=row, column=col); c.fill = yellow; c.font = inp; c.border = bd
            ws.cell(row=row, column=3).number_format = '#,##0'
        ws['B15'] = 'Sum (automatic)'; ws['B15'].font = bold; ws['B15'].border = bd
        ws['C15'] = '=IF(COUNT(C13:C14)=0,"",SUM(C13:C14))'; ws['C15'].number_format = '#,##0'; ws['C15'].font = bold; ws['C15'].border = bd
        ws['B16'] = 'Difference from row 6 (should be 0)'; ws['B16'].font = bold; ws['B16'].border = bd
        ws['C16'] = '=IF(OR(C15="",C6=""),"",C15-C6)'; ws['C16'].number_format = '#,##0'; ws['C16'].font = bold; ws['C16'].border = bd
        meta_row = 18
    labels = ['單位', '年度欄', '合併／個體'] if zh else ['Units', 'Year column', 'Consolidated or not']
    for k, lab in enumerate(labels):
        row = meta_row + k
        ws.cell(row=row, column=1, value=lab).font = bold; ws.cell(row=row, column=1).fill = grey; ws.cell(row=row, column=1).border = bd
        c = ws.cell(row=row, column=2); c.fill = yellow; c.font = inp; c.border = bd; ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=5)
    ws.cell(row=meta_row + 4, column=1, value=('數字來源：彰化銀行 114 年度財務報告，合併資產負債表 PDF 第 1 頁（紙本頁碼 8），單位新臺幣千元。' if zh else
        'Source: JPMorgan Chase & Co. 2025 Annual Report, Consolidated balance sheets, PDF page 199 (printed page 167, Form 10-K numbering), US$ million.')).font = Font(name=FN, size=10, color='3E5656')
    widths = [26, 34, 16, 10, 22, 16, 10, 11, 9] if zh else [30, 40, 18, 12, 24, 18, 12, 11, 10]
    for j, w in enumerate(widths): ws.column_dimensions['ABCDEFGHI'[j]].width = w
    ws.freeze_panes = 'A5'

    if teacher:
        rs = wb.create_sheet('參考' if zh else 'Reference')
        rs['A1'] = '參考：三家的數字與五個比率（老師對答案用；逐格對過財報原文）' if zh else 'Reference: the three banks’ numbers and five ratios (for the teacher; checked against the reports)'
        rs['A1'].font = Font(name=FN, bold=True, size=13, color='0E5C5B')
        cols = [(CHB, '彰化銀行 2025-12-31（千元）' if zh else 'Chang Hwa Commercial Bank, 2025-12-31 (NT$ thousand)'),
                (JPM, 'JPMorgan Chase 2025-12-31（百萬美元）' if zh else 'JPMorgan Chase & Co., 2025-12-31 (US$ million)'),
                (SVB, '矽谷銀行 2022-12-31（百萬美元）' if zh else 'SVB Financial Group, 2022-12-31 (US$ million)')]
        rs.cell(row=3, column=1, value='項目' if zh else 'Item').font = bold
        for j, (_, h) in enumerate(cols, 2):
            c = rs.cell(row=3, column=j, value=h); c.font = bold; c.fill = head; c.alignment = wrap; c.border = bd
        rs.cell(row=3, column=1).fill = head; rs.cell(row=3, column=1).border = bd
        items = [('assets', '資產總計', 'Total assets'), ('loans', '放款（淨額）', 'Loans (net)'), ('securities', '證券投資', 'Securities'),
                 ('deposits', '存款', 'Deposits'), ('liabilities', '負債總計', 'Total liabilities'), ('equity', '權益總計', 'Equity')]
        for i, (k, z, e) in enumerate(items):
            row = 4 + i
            rs.cell(row=row, column=1, value=z if zh else e).border = bd
            for j, (bk, _) in enumerate(cols, 2):
                c = rs.cell(row=row, column=j, value=bk['base'][k]); c.number_format = '#,##0'; c.border = bd; c.font = Font(name=FN, color='0000FF')
        rs.cell(row=11, column=1, value='五個比率（公式算）' if zh else 'Five ratios (formula)').font = bold
        pairs = [(5, 4), (6, 4), (5, 7), (7, 8), (9, 4)]  # row numbers of numerator, denominator
        for i, (r, (nr, dr)) in enumerate(zip(RD, pairs)):
            row = 12 + i
            rs.cell(row=row, column=1, value=r['zh'] if zh else r['en']).border = bd
            for j in range(2, 5):
                col = 'ABCD'[j - 1]
                c = rs.cell(row=row, column=j, value=f'={col}{nr}/{col}{dr}'); c.number_format = '0.00%'; c.border = bd
        rs.cell(row=18, column=1, value='參考比率（對照用）' if zh else 'Reference ratios (to compare)').font = bold
        for i, r in enumerate(RD):
            row = 19 + i
            rs.cell(row=row, column=1, value=r['zh'] if zh else r['en']).border = bd
            for j, (bk, _) in enumerate(cols, 2):
                c = rs.cell(row=row, column=j, value=bk['ratios_pct'][r['key']]); c.number_format = '0.00'; c.border = bd; c.font = Font(name=FN, color='0000FF')
        notes = ([ '彰銀證券投資＝透過損益＋透過其他綜合損益按公允價值衡量之金融資產＋按攤銷後成本衡量之債務工具投資（三行相加）。',
                   'JPMorgan Chase 證券投資＝Investment securities, net（AFS＋HTM），不含 Trading assets；放款用 Loans, net of allowance for loan losses。',
                   '矽谷銀行證券投資＝AFS＋HTM；權益用 Total SVBFG stockholders’ equity。',
                   '頁碼：彰銀財報 PDF 第 1 頁（紙本 8）；JPM 年報 PDF 第 199 頁（10-K 紙本 167）；SVB 10-K 紙本 95。'] if zh else
                 [ 'Chang Hwa securities = the three financial-asset lines added together (fair value through profit or loss + fair value through other comprehensive income + debt instruments at amortized cost).',
                   'JPMorgan Chase securities = Investment securities, net (AFS + HTM), excluding Trading assets; loans = Loans, net of allowance for loan losses.',
                   'SVB securities = AFS + HTM; equity = Total SVBFG stockholders’ equity.',
                   'Pages: Chang Hwa financial report PDF page 1 (printed 8); JPM annual report PDF page 199 (10-K printed 167); SVB 10-K printed page 95.'])
        for i, t in enumerate(notes):
            c = rs.cell(row=25 + i, column=1, value=t); c.font = Font(name=FN, size=10, color='3E5656')
        for j, w in enumerate([34, 30, 30, 30]): rs.column_dimensions['ABCD'[j]].width = w
        rs.row_dimensions[3].height = 34
        for row in rs.iter_rows():
            for c in row:
                if c.font and c.font.name != FN:
                    c.font = Font(name=FN, bold=c.font.bold, size=c.font.size, color=c.font.color)
    wb.save(path)

# ================= e學苑 md =================
def elearn_md():
    return f"""# e學苑 標籤與作業說明（貨銀課 AI 第二輪）

> 給王老師直接貼。中文段＝11/16（一）中文場，英文段＝11/18（三）英文場。作業截止日留空，請老師填。檔名對應 `student/` 與上課包。

## 中文場（11/16）

### 標籤（放在上課那一週）

今天用 AI 幫一家銀行做體檢：把彰化銀行的財報交給 AI，要它每一句都指回頁碼，五個比率自己算，再回原文抽查。

- 課程網站（下載課程資料夾、財報、所有檔案）：https://cwstedctw.github.io/money-banking-ai-checkup/
- 投影片 PDF：`deck-zh.pdf`
- 學生練習單：`學生練習單-銀行體檢.docx`
- 體檢表範本：`體檢表範本.xlsx`
- 彰化銀行 114 年度財務報告（10 頁）：`CHB-2025-FY-consolidated-financial-report.pdf`
- 彰化銀行 2025 年年報（123 頁）：`CHB-2025-annual-report.pdf`
- 回家作業卡：`回家作業卡.docx`

請帶筆電、先裝好一個 AI agent（Antigravity、ChatGPT 桌面版或 Claude 桌面版）；沒有的話用手機或筆電登入 ChatGPT／Claude 網頁。

### 作業說明：第二次 AI 專題的第一張表

挑兩家銀行，一家台灣、一家外國（台灣的用銀行本身的財報，不用金控的合併報表；外國的用年報或 10-K）。用 agent 開課程資料夾做 任務.md 的任務三（沒有 agent 就用聊天版貼提示語 ③），兩家各做五個比率、每格附 PDF 頁碼，再用體檢表範本自己算一次；抽三格回原文查；再用 AI 的深度研究功能寫兩家經營方式的比較初稿（提示語 ⑤），挑三句回來源查。把提示語 ③ 裡的銀行名、報表日期、科目名換成那家財報上的字；淨放款與證券投資各算了哪幾列要寫明。深度研究功能不能用的話，改用一般對話，並附上你自己找到的來源。

交：表格＋抽查紀錄＋初稿與三句查核＋揭露句。截止日：＿＿＿＿。

## English session (11/18)

### Section label (in the week of the class)

Today we give a bank a check-up with AI: hand JPMorgan Chase’s annual report to an AI, make it cite a page for every sentence, compute the five ratios yourself, and spot-check against the original.

- Course website (course folder, reports, all files): https://cwstedctw.github.io/money-banking-ai-checkup/
- Slides (PDF): `deck-en.pdf`
- Student worksheet: `Student-Worksheet-Bank-Checkup.docx`
- Check-up template: `checkup-template.xlsx`
- JPMorgan Chase & Co. 2025 Annual Report (364 pages): `JPM-2025-annual-report.pdf`
- Homework card: `Homework-Card.docx`

Please bring a laptop with one AI agent installed (Antigravity, ChatGPT desktop or Claude desktop); if you have none, log in to ChatGPT or Claude on the web with a phone or laptop.

### Assignment: the first table of AI Project 2

Pick two banks, one in Taiwan and one abroad (for Taiwan, the bank’s own financial report, not the holding company’s consolidated report; abroad, the annual report or 10-K). With your agent, do Task 3 in TASK.md in the course folder (no agent: the chat version with Prompt ③): the five ratios for both banks with the PDF page for every cell, then compute them once more yourselves with the check-up template; check three cells against the original. Then use an AI’s deep-research mode to draft a comparison of how the two banks make money (Prompt ⑤) and check three of its sentences against the sources. Replace the bank name, statement date and line names in Prompt ③ with the words printed in that bank’s report, and state which lines you counted as net loans and as securities. If deep-research mode is not available, use a normal chat instead and attach the sources you found yourselves.

Hand in: the table + the spot-check log + the draft with its three checked sentences + the disclosure sentence. Due: ________.
"""

# ================= main =================
def main():
    env = dict(os.environ, NODE_PATH=str(NODE_MODULES))
    docs = {
        '學生練習單-銀行體檢': worksheet_zh(), 'Student-Worksheet-Bank-Checkup': worksheet_en(),
        '回家作業卡': homework_zh(), 'Homework-Card': homework_en(),
    }
    docs.update(split_stress(stress_zh(), 'zh')); docs.update(split_stress(stress_en(), 'en'))
    manifest = {}
    for name, spec in docs.items():
        sp = SPECDIR / f'{name}.json'
        sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
        outp = (TEA if name in TEACHER_DOCS else STU) / f'{name}.docx'
        r = subprocess.run(['node', str(QA / 'student-render_docx.js'), str(sp), str(outp)], env=env, capture_output=True, text=True, encoding='utf-8')
        if r.returncode != 0:
            print(r.stdout, r.stderr); sys.exit(1)
        manifest[name] = {'docx': str(outp), 'prompts': [list(b['key']) for b in spec['blocks'] if b['t'] == 'prompt']}
    (STU / '學生練習單-銀行體檢.html').write_text(to_html(docs['學生練習單-銀行體檢'], '3　卡住了'), encoding='utf-8')
    (STU / 'Student-Worksheet-Bank-Checkup.html').write_text(to_html(docs['Student-Worksheet-Bank-Checkup'], '3  If you get stuck'), encoding='utf-8')
    build_xlsx('zh', False, STU / '體檢表範本.xlsx'); build_xlsx('zh', True, TEA / '體檢表範本-老師版.xlsx')
    build_xlsx('en', False, STU / 'checkup-template.xlsx'); build_xlsx('en', True, TEA / 'checkup-template-teacher.xlsx')
    (EL / 'e學苑標籤與作業說明.md').write_text(elearn_md(), encoding='utf-8')
    (QA / 'student-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')
    print('ok')

if __name__ == '__main__':
    main()
