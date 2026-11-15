#!/usr/bin/env python3
"""make_site.py — 把貨銀課 AI 第二輪上課包做成 GitHub Pages 網站（docs/），並把產線鏡像進公開 repo。

用法（在含 numbers.json 的資料夾、或 repo 的 tools/ 執行皆可）：
  python -X utf8 make_site.py --out D:\\Ted_data\\active\\money-banking-ai-checkup [--mirror]
  --out     目標 repo 資料夾（網站寫到 <out>/docs/）
  --mirror  同時把規格、數字、產線程式、學生檔、示範夾鏡像到 <out>/（老師用的答案檔一律不複製）

規矩：提示語從 內容規格.md §三 讀（一字不漏）；數字只從 numbers.json；網頁零外部資源（字型用系統）。
QR 圖照 Hub 的作法「程式產生＋反向解碼驗證」，解不回網址就不留檔。
"""
import argparse
import hashlib
import html
import json
import pathlib
import re
import shutil
import sys
import urllib.parse


def find_root(start: pathlib.Path) -> pathlib.Path:
    for p in [start] + list(start.parents):
        if (p / "numbers.json").exists() and (p / "內容規格.md").exists():
            return p
    sys.exit("找不到 numbers.json＋內容規格.md 所在的資料夾")


HERE = pathlib.Path(__file__).resolve().parent
ROOT = find_root(HERE)
SITE_URL = "https://cwstedctw.github.io/money-banking-ai-checkup/"
REPO_URL = "https://github.com/cwstedctw/money-banking-ai-checkup"
ZIP_URL = REPO_URL + "/archive/refs/heads/main.zip"
N = json.loads((ROOT / "numbers.json").read_text(encoding="utf-8"))


def load_prompts():
    spec = (ROOT / "內容規格.md").read_text(encoding="utf-8")
    sec = spec.split("## 三、", 1)[1].split("\n## 四、", 1)[0]
    blocks = re.findall(r"```\n(.*?)\n```", sec, flags=re.S)
    assert len(blocks) == 10, f"§三 應有 10 段提示語，讀到 {len(blocks)}"
    return {"zh": blocks[:5], "en": blocks[5:]}


PROMPTS = load_prompts()
CSS = """
:root{--teal:#0E7C7B;--gold:#D9A441;--cream:#F4ECD8;--ink:#1A1A1A;--paper:#FFFDF8;--line:#E4D9C3}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--cream);color:var(--ink);font-family:"Noto Sans TC","Microsoft JhengHei","PingFang TC","Segoe UI",system-ui,sans-serif;line-height:1.6}
main{max-width:760px;margin:0 auto;padding:24px 16px 56px}
header.top{background:var(--teal);color:#fff;padding:28px 16px}
header.top .in{max-width:760px;margin:0 auto}
header.top h1{margin:0 0 6px;font-size:1.45rem;line-height:1.3;letter-spacing:.01em}
header.top p{margin:0;opacity:.92;font-size:.95rem}
h2{font-size:1.15rem;margin:28px 0 10px;color:var(--teal)}
.card{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 16px 10px;margin:12px 0;box-shadow:0 1px 0 rgba(0,0,0,.03)}
.card h3{margin:0 0 4px;font-size:1.08rem}
.card .meta{color:#555;font-size:.92rem;margin:0 0 10px}
.links{display:grid;grid-template-columns:1fr;gap:8px;margin:0;padding:0;list-style:none}
@media(min-width:560px){.links{grid-template-columns:1fr 1fr}}
.links a{display:block;padding:11px 12px;border-radius:10px;border:1px solid var(--line);background:#fff;color:var(--ink);text-decoration:none;font-weight:600;font-size:.98rem}
.links a:hover{border-color:var(--teal)}
.links a small{display:block;font-weight:400;color:#666;font-size:.84rem}
.links a.primary{background:var(--teal);color:#fff;border-color:var(--teal)}
.links a.primary small{color:#e6f2f2}
.note{font-size:.92rem;color:#444;margin:8px 0 0}
ol.steps{padding-left:1.2em}ol.steps li{margin:6px 0}
pre.prompt{white-space:pre-wrap;word-break:break-word;background:#fff;border:1px solid var(--line);border-left:4px solid var(--teal);border-radius:10px;padding:14px 14px;font:inherit;font-size:.98rem;margin:8px 0 0}
.pbar{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
.tag{display:inline-block;background:var(--teal);color:#fff;border-radius:999px;padding:2px 10px;font-size:.84rem;font-weight:700}
button.copy{background:var(--gold);color:#1A1A1A;border:0;border-radius:999px;padding:9px 16px;font-weight:700;font-size:.95rem;cursor:pointer;font-family:inherit}
button.copy:active{transform:translateY(1px)}
button.copy.done{background:var(--teal);color:#fff}
.use{color:#555;font-size:.9rem;margin:4px 0 0}
footer{max-width:760px;margin:0 auto;padding:0 16px 40px;color:#555;font-size:.86rem}
footer a{color:var(--teal)}
.lang{float:right;font-size:.9rem}.lang a{color:#fff;text-decoration:underline}
img.qr{width:160px;height:160px;display:block;margin:8px 0}
"""
JS_COPY = """
(function(){
  function fb(t){var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.top='-1000px';document.body.appendChild(ta);ta.select();var ok=false;try{ok=document.execCommand('copy')}catch(e){}document.body.removeChild(ta);return ok}
  document.querySelectorAll('button.copy').forEach(function(b){
    b.addEventListener('click',function(){
      var t=document.getElementById(b.getAttribute('data-for')).textContent;var done=function(){var o=b.textContent;b.textContent=b.getAttribute('data-done');b.classList.add('done');setTimeout(function(){b.textContent=o;b.classList.remove('done')},1600)};
      if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(done,function(){if(fb(t))done()})}else if(fb(t)){done()}
    });
  });
})();
"""


def page(title, body, lang="zh-Hant", head_html="", sub=""):
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{CSS}</style></head><body>'
            f'<header class="top"><div class="in">{head_html}<h1>{html.escape(title)}</h1><p>{sub}</p></div></header>'
            f'<main>{body}</main>'
            f'<footer><p>© 2026 陳文盛（國立東華大學通識教育中心）× AI 協作團隊・<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hant">CC BY-NC-SA 4.0</a>・'
            f'<a href="{REPO_URL}">原始碼與 AI 助理規則（GitHub）</a></p>'
            f'<p>財報的著作權屬各發行機構，本站只連結官方檔案；矽谷銀行摘錄頁照 SEC 公開申報文件逐格重排。Financial reports belong to their issuers; this site links to the official files.</p></footer>'
            f'<script>{JS_COPY}</script></body></html>')


def a(href, text, small="", cls=""):
    c = f' class="{cls}"' if cls else ""
    s = f"<small>{html.escape(small)}</small>" if small else ""
    return f'<li><a{c} href="{href}">{html.escape(text)}{s}</a></li>'


def official(bank):
    return bank["source"]["url"]


def enc(url):
    # 中文網址逐段百分號編碼，瀏覽器才不會把它切壞
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path), p.query, p.fragment))


def index_html():
    chb, jpm, svb = N["banks"]["CHB"], N["banks"]["JPM"], N["banks"]["SVB"]
    zh = f"""
<h2>中文場　11/16（一）11:35–12:25</h2>
<div class="card"><h3>病人：彰化銀行（2801）・2025-12-31 合併資產負債表</h3>
<p class="meta">單位新臺幣千元。財報 10 頁，合併資產負債表在 PDF 第 1 頁（紙本頁碼 8）。</p>
<ul class="links">
{a(ZIP_URL, "下載課程資料夾（ZIP）", "解開後用你的 AI agent 打開 kit/zh：規則、任務、財報網址都在裡面", "primary")}
{a("zh/deck.html", "投影片（網頁版）", "22 頁；提示語框有「複製」鈕，左右鍵翻頁", "primary")}
{a("zh/prompts.html", "提示語①–⑤（手機版）", "沒有 agent 的人：一鍵複製，貼進 ChatGPT／Claude 網頁", "")}
{a("zh/worksheet.html", "學生練習單（網頁版）", "每一步：做什麼、貼什麼、應該看到、多久")}
{a("zh/files/學生練習單-銀行體檢.docx", "學生練習單（Word）", "同內容，可下載填寫")}
{a("zh/files/體檢表範本.xlsx", "體檢表範本（Excel）", "填數字，五個比率自動算")}
{a("zh/files/回家作業卡.docx", "回家作業卡（Word）", "第二次 AI 專題的第一張表")}
{a("zh/files/壓力測試題.docx", "壓力測試題（Word）", "情境 A、B 與空白 T 字帳")}
{a("zh/files/deck-zh.pdf", "投影片 PDF", "備援；沒有複製鈕")}
</ul>
<h3 style="margin-top:14px;font-size:1rem">財報（官方檔案）</h3>
<ul class="links">
{a(enc(official(chb)), "彰化銀行 114 年度財務報告", "官網 PDF，10 頁；上課用這份", "")}
{a(enc(chb["source_business"]["url"]), "彰化銀行 2025 年年報", "官網 PDF，123 頁；回家做經營方式用")}
{a("files/SVB-2022-balance-sheet-excerpt.pdf", "矽谷銀行資產負債表摘錄（一頁）", "照 2022 年 10-K 第 95 頁重排；開場案例")}
</ul></div>
"""
    en = f"""
<h2>English session　Wed 11/18, 11:00–11:50</h2>
<div class="card"><h3>Patient: JPMorgan Chase &amp; Co. · Consolidated balance sheets, Dec 31, 2025</h3>
<p class="meta">US$ million. 2025 Annual Report, 364 pages; the balance sheet is on PDF page 199 (= page 167 in the 10-K's own numbering).</p>
<ul class="links">
{a(ZIP_URL, "Download the course folder (ZIP)", "Unzip, then open kit/en with your AI agent: rules, tasks and report links are inside", "primary")}
{a("en/deck.html", "Slides (web)", "22 pages; prompt boxes have a Copy button; arrow keys to navigate", "primary")}
{a("en/prompts.html", "Prompts ①–⑤ (phone)", "No agent? One-tap copy for ChatGPT / Claude on the web", "")}
{a("en/worksheet.html", "Student worksheet (web)", "Each step: what to do, what to paste, what you should see, how long")}
{a("en/files/Student-Worksheet-Bank-Checkup.docx", "Student worksheet (Word)", "Same content, downloadable")}
{a("en/files/checkup-template.xlsx", "Check-up template (Excel)", "Type the numbers; the five ratios compute themselves")}
{a("en/files/Homework-Card.docx", "Homework card (Word)", "The first table of AI Project 2")}
{a("en/files/Stress-Test-Scenarios.docx", "Stress-test scenarios (Word)", "Scenarios A and B with blank T-accounts")}
{a("en/files/deck-en.pdf", "Slides (PDF)", "Backup; no Copy buttons")}
</ul>
<h3 style="margin-top:14px;font-size:1rem">Reports (official files)</h3>
<ul class="links">
{a(official(jpm), "JPMorgan Chase 2025 Annual Report", "Official PDF, 364 pages; PDF pages 75–359 reprint Form 10-K pages 43–327")}
{a("files/SVB-2022-balance-sheet-excerpt.pdf", "SVB balance-sheet excerpt (one page)", "Re-typeset from the FY2022 Form 10-K, page 95; opening case")}
{a(svb["source"]["url"], "SVB Financial Group Form 10-K, FY2022", "SEC EDGAR, web version")}
</ul></div>
"""
    how = f"""
<h2>怎麼用 / How to use</h2>
<div class="card"><ol class="steps">
<li><b>主線：用你的 AI agent 開資料夾。</b>下載課程資料夾 ZIP、解開，用 Antigravity（File → Open Folder）、ChatGPT 桌面版的 Codex（新增專案 → 選資料夾）或 Claude 桌面版（Code 分頁 → 開啟資料夾）打開 <code>kit/zh</code>，貼一句「請照這個資料夾的 AGENTS.md 做完 任務.md 的任務一」。它會自己抓財報、做出每格有頁碼的表、列出比率算式。<br><span class="use"><b>Main route: open the folder with your AI agent.</b> Unzip the course folder and open <code>kit/en</code> in Antigravity (File → Open Folder), ChatGPT desktop's Codex (New project → choose folder) or Claude desktop (Code tab → Open folder); paste "Follow AGENTS.md in this folder and complete Task 1 in TASK.md".</span></li>
<li><b>沒有 agent？</b>下載上面的財報，上傳到 ChatGPT 或 Claude 網頁，貼提示語 ③。<br><span class="use"><b>No agent?</b> Download the report above, upload it to ChatGPT or Claude on the web, paste Prompt ③.</span></li>
<li>拿到表之後，<b>五個比率自己再算一次</b>（體檢表範本會算）——agent 算得快，核對是你的事。<br><span class="use">Then <b>recompute the five ratios yourself</b> (the template does it) — the agent is fast, checking is your job.</span></li>
<li>抽三格回原文查：單位、年度欄、合併或個體。<br><span class="use">Spot-check three cells against the original: units, year column, consolidated or not.</span></li>
<li>交作業附揭露句：「本作業使用＿＿（AI 工具）協助＿＿（做了什麼）；數字已由本組對照原文核對。」</li>
</ol></div>
<h2>給老師 / For instructors</h2>
<div class="card"><p class="note">把這一個網址放進 e學苑 就好，學生用手機也能開。老師用的檔案（壓力測試參考答案、體檢表老師版）不在這個網站上，請向陳文盛老師索取。<br>
Put this one link on your LMS. Teacher-only files (answer keys) are not on this site; ask the author.</p>
<p class="note">想在自己的課上換一家銀行？這個網站的原始碼 repo 內建 AI 助理規則：用 Claude 桌面版、Codex 或 Antigravity 打開 repo 資料夾，直接說「幫我加一家銀行」，它會照 <code>bank_numbers.py</code> 的格式要你提供數字與頁碼，再重算五個比率、重產投影片與練習單。說明在 <a href="{REPO_URL}#readme">README</a>。</p>
<img class="qr" src="qr.png" alt="QR code of this site"><p class="note">投影用 QR：掃了就是這一頁。</p></div>
"""
    body = zh + en + how
    return page("銀行體檢：把財報交給 AI，要它每一句指回頁碼", body, "zh-Hant",
                sub="Bank check-up with AI — Money and Banking, National Dong Hwa University · 陳文盛 Wen-Sheng (Ted) Chen")


def prompts_html(lang):
    zh = lang == "zh"
    labels = ({1: ("提示語 ①", "課文整理：把課本第 9 章（你自己的電子檔）交給 AI 後貼"), 2: ("提示語 ②", "矽谷銀行三題（老師示範用；自己想試就上傳摘錄頁再貼）"),
               3: ("提示語 ③", "銀行體檢：上傳財報後貼，拿到有頁碼的表"), 4: ("提示語 ④", "壓力測試：接在提示語 ③ 的同一個對話裡貼"),
               5: ("提示語 ⑤", "回家：深度研究兩家銀行的經營方式")}
              if zh else
              {1: ("Prompt ①", "Study guide: paste after giving the AI your own copy of textbook Chapter 9"), 2: ("Prompt ②", "Silicon Valley Bank, three questions (teacher demo; try it with the excerpt page)"),
               3: ("Prompt ③", "Bank check-up: paste after uploading the report; you get a table with pages"), 4: ("Prompt ④", "Stress test: paste in the same conversation as Prompt ③"),
               5: ("Prompt ⑤", "Homework: deep research on how two banks make money")})
    cards = []
    for i in range(1, 6):
        tag, use = labels[i]
        text = PROMPTS[lang][i - 1]
        cards.append(f'<div class="card"><div class="pbar"><span class="tag">{html.escape(tag)}</span>'
                     f'<button class="copy" data-for="p{i}" data-done="{"已複製 ✓" if zh else "Copied ✓"}">{"複製" if zh else "Copy"}</button></div>'
                     f'<p class="use">{html.escape(use)}</p><pre class="prompt" id="p{i}">{html.escape(text)}</pre></div>')
    intro = ('<p class="note">有 AI agent 的人不用這一頁：下載課程資料夾、用 agent 打開 <code>kit/zh</code>，任務檔裡就是這些提示語。這一頁給用 ChatGPT／Claude 網頁的人：先上傳財報，再整段貼上。找不到的數字它會說「找不到」，那是對的——自己翻 PDF。</p>'
             if zh else
             '<p class="note">If you have an AI agent you do not need this page: download the course folder and open <code>kit/en</code>; the task file holds these prompts. This page is for ChatGPT / Claude on the web: upload the report first, then paste the whole prompt. If it says "not found", that is the right answer — open the PDF yourself.</p>')
    back = f'<p class="note"><a href="../index.html">{"← 回首頁" if zh else "← Home"}</a>・<a href="deck.html">{"投影片" if zh else "Slides"}</a>・<a href="worksheet.html">{"練習單" if zh else "Worksheet"}</a></p>'
    title = "提示語①–⑤（中文場・彰化銀行）" if zh else "Prompts ①–⑤ (English session · JPMorgan Chase)"
    return page(title, back + intro + "".join(cards) + back, "zh-Hant" if zh else "en",
                sub=("貨幣銀行學 AI 第二輪・2026-11-16" if zh else "Money and Banking · AI session 2 · 2026-11-18"))


def copy_file(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return hashlib.sha256(dst.read_bytes()).hexdigest()[:12]


def make_qr(site, out):
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H
    from PIL import Image
    from pyzbar.pyzbar import decode
    q = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=3)
    q.add_data(site); q.make(fit=True)
    img = q.make_image(fill_color=(14, 124, 123), back_color="white").convert("RGB")
    img.save(out)
    got = [d.data.decode() for d in decode(Image.open(out))]
    if got != [site]:
        out.unlink(missing_ok=True)
        sys.exit(f"QR 解不回原網址：{got}")
    return got[0]


def build_site(out: pathlib.Path):
    site = out / "docs"
    manifest = {}
    # 1. 投影片、練習單、檔案
    for lang in ("zh", "en"):
        manifest[f"{lang}/deck.html"] = copy_file(ROOT / f"deck-{lang}.html", site / lang / "deck.html")
        manifest[f"{lang}/files/deck-{lang}.pdf"] = copy_file(ROOT / f"deck-{lang}.pdf", site / lang / "files" / f"deck-{lang}.pdf")
    manifest["zh/worksheet.html"] = copy_file(ROOT / "student" / "學生練習單-銀行體檢.html", site / "zh" / "worksheet.html")
    manifest["en/worksheet.html"] = copy_file(ROOT / "student" / "Student-Worksheet-Bank-Checkup.html", site / "en" / "worksheet.html")
    for f in ["學生練習單-銀行體檢.docx", "體檢表範本.xlsx", "回家作業卡.docx", "壓力測試題.docx"]:
        manifest[f"zh/files/{f}"] = copy_file(ROOT / "student" / f, site / "zh" / "files" / f)
    for f in ["Student-Worksheet-Bank-Checkup.docx", "checkup-template.xlsx", "Homework-Card.docx", "Stress-Test-Scenarios.docx"]:
        manifest[f"en/files/{f}"] = copy_file(ROOT / "student" / f, site / "en" / "files" / f)
    manifest["files/SVB-2022-balance-sheet-excerpt.pdf"] = copy_file(ROOT / "demo" / "svb" / "SVB-2022-balance-sheet-excerpt.pdf", site / "files" / "SVB-2022-balance-sheet-excerpt.pdf")
    # 2. 頁面
    (site / "index.html").write_text(index_html(), encoding="utf-8")
    (site / "zh" / "prompts.html").write_text(prompts_html("zh"), encoding="utf-8")
    (site / "en" / "prompts.html").write_text(prompts_html("en"), encoding="utf-8")
    (site / ".nojekyll").write_text("", encoding="utf-8")
    # 3. QR
    manifest["qr.png"] = make_qr(SITE_URL, site / "qr.png")
    # 4. 老師用的檔不准出現在 docs/
    leak = [p for p in site.rglob("*") if re.search(r"老師版|Teacher|參考答案|Answer-Key|給王老師", p.name)]
    assert not leak, f"docs/ 裡出現老師用檔：{leak}"
    return manifest


def mirror_repo(out: pathlib.Path):
    """把產線鏡像進 repo：規格、數字、程式、學生檔、示範夾；不複製 teacher/、data/*.pdf、qa/。"""
    # 公開版規格：拿掉引用私人信件的句子、內部交付段與複驗紀錄；§三 提示語一字不動（產線從這裡讀）
    spec = (ROOT / "內容規格.md").read_text(encoding="utf-8")
    head, rest = spec.split("\n## 〇、", 1)
    head = ("# 內容規格 v1 — 貨銀課 AI 第二輪「銀行體檢＋壓力測試」（中文場 11/16、英文場 11/18）\n\n"
            "> 2026-11-15 洄瀾寫；公開版（內部交付與信件往來已略去）。**本課唯一正本**：內容變了先改這裡，投影片、學生練習單、網站跟著改。\n"
            "> 依據：授課老師 2026-11-12 的新方案（50 分鐘流程與五個比率照抄在 §一、§〇 E）與補充（英文場用國外銀行、工具加 ChatGPT 與 Claude）。\n"
            "> **數字只有一個來源：`bank_numbers.py` → `numbers.json`。** 本檔引用的數字都是從那裡抄的；改教材的人一律讀 `numbers.json`，不准手算、不准另抄 PDF。\n")
    rest = "\n## 〇、" + rest
    rest = rest.split("\n## 八、", 1)[0] + "\n## 九、" + rest.split("\n## 九、", 1)[1]
    rest = rest.split("\n## 複驗紀錄", 1)[0].rstrip() + "\n"
    rest = re.sub(r"王友利老師|王老師", "授課老師", rest)
    rest = re.sub(r"（她 11/12 17:11 定；Ted 行事曆 11/13 已照改）", "", rest)
    rest = re.sub(r"Ted 2026-11-15 早上的指示[^。]*。", "", rest)
    rest = rest.replace("Ted", "陳老師")
    spec_pub = head + rest
    assert "```" in spec_pub and spec_pub.count("```") == 20, "公開版規格的提示語區塊數不對"
    (out / "內容規格.md").parent.mkdir(parents=True, exist_ok=True)
    (out / "內容規格.md").write_text(spec_pub, encoding="utf-8")
    copies = ["numbers.json", "numbers.md", "bank_numbers.py", "check_econ2.py", "web-shell.html", "export_pdf.py",
              "deck/make_slides.py", "deck/econ.css", "deck/deck.css",
              "demo/svb/make_svb_excerpt.py", "demo/示範小抄.md",
              "elearn/e學苑標籤與作業說明.md", "data/README.md"]
    for rel in copies:
        copy_file(ROOT / rel, out / rel)
    # 學生用的課程資料夾 kit/zh、kit/en：規則、任務、README、data/README.md；PDF 與成品不進 repo
    for p in (ROOT / "kit").rglob("*"):
        if p.is_file() and p.suffix != ".pdf" and "成品" not in p.parts and "output" not in p.parts:
            copy_file(p, out / p.relative_to(ROOT))
    stale = [q for q in (out / "demo").glob("agent-*") if q.is_dir()]
    for q in stale:
        shutil.rmtree(q)
    for p in (ROOT / "student").iterdir():
        if p.suffix in (".docx", ".xlsx", ".html"):
            copy_file(p, out / "student" / p.name)
    copy_file(ROOT / "qa" / "student-build.py", out / "tools" / "build_student_docs.py")
    copy_file(HERE / "make_site.py" if (HERE / "make_site.py").exists() else ROOT / "make_site.py", out / "tools" / "make_site.py")
    # build_web.py 原本從洄瀾 repo 拿校徽，鏡像版改從 deck/assets/ 拿
    bw = (ROOT / "build_web.py").read_text(encoding="utf-8")
    bw = bw.replace("SEAL_SRC = ROOT.parents[3] / 'skills/course-intro/assets'   # 本夾往上 4 層＝repo 根（material、teaching、workspace、根）",
                    "SEAL_SRC = ROOT / 'deck' / 'assets'   # 校徽放 repo 自己的 deck/assets/")
    (out / "build_web.py").write_text(bw, encoding="utf-8")
    seal_src = ROOT.parents[3] / "skills" / "course-intro" / "assets"
    for s in ("seal-color.webp", "seal-white.webp"):
        if (seal_src / s).exists():
            copy_file(seal_src / s, out / "deck" / "assets" / s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=r"D:\Ted_data\active\money-banking-ai-checkup")
    ap.add_argument("--mirror", action="store_true")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    manifest = build_site(out)
    if args.mirror:
        mirror_repo(out)
    for k, v in manifest.items():
        print(f"  {k}  {v}")
    print(f"site → {out / 'docs'}  ({len(manifest)} files copied + index/prompts×2/qr)")


if __name__ == "__main__":
    main()
