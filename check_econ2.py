#!/usr/bin/env python3
"""check_econ2.py — 貨銀課 AI 第二輪這一夾的機械檢查（只用標準函式庫）。

用法：python -X utf8 check_econ2.py        （在本夾或任何地方跑都可以）
印 PASS／WARN／FAIL 清單；有 FAIL → exit 1。

檢查：
  ① 數字：掃 deck/build/*/*.html、deck-*.html、student/*.html、teacher/*.md、demo/**/*.md（有就掃）裡所有 ≥4 位數的數字
     （含千分位寫法），每一個都要在 numbers.json 找得到（數值本身、或 numbers.json 字串裡出現過的數字），否則 FAIL。
     允許清單：年份 2021–2026；1280、720；場次日期 1116、1118（MMDD）；頁碼（PDF 1–364 與紙本頁碼都 ≤3 位，本來就不掃）；時間 11:35／12:25／11:00／11:50（≤2 位，不掃）。
     另外認一個「衍生數」：情境 A 付完還剩多少＝liquid_assets_before − liquid_used（numbers.json 沒存這格，make_slides.py 用同一條式子算；
     JPM＝87,406）。網址先拿掉再掃；deck 裡的網址必須是 numbers.json 裡的網址（否則 FAIL），其他檔的網址只列 WARN。
  ② 禁字：大陸用語（軟件、視頻、信息、數據庫、默認、優化、質量、屏幕、鼠標、點擊、網絡、用戶、登錄、鏈接、文檔）與簡體字抽樣，出現就 FAIL。
  ③ 提示語逐字：從 內容規格.md §三 讀出五段中文、五段英文，跟 deck/build/{zh,en}/04、06、10、16、20 頁與 deck-{zh,en}.html
     的提示語框（<pre class="ec-ptext">）比，差一個字 FAIL。
  ④ 零外部資源：deck 檔不得有 http(s) 或 // 開頭的 src／href／url(／@import（p22 的網址只能是純文字）。
  ⑤ 頁數 22×2、深底頁＝1 與 22（build 每頁檔、打包單檔都查）。
  ⑥ 每頁正文中文字數（不含提示語框；> 80 列 WARN，不擋）；英文版可見文字與 deck/內容稿.en.md 不得有中文或全形標點（FAIL）；中文版列出出現的英文詞（INFO，給人看是否 ≤8 個）。
  ⑦ 矽谷銀行只用一個口徑：deck 不得出現附註的未實現損失與它推出的認列後權益（15,160、844）。
⚠️ 本夾有 bank_numbers.py，會蓋掉 Python 標準函式庫的 numbers 模組（decimal、fractions、PIL 都會壞）；所以這支一開頭先把本夾從 sys.path 拿掉。
2026-11-15 建置者寫。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:] = [p for p in sys.path if p and Path(p).resolve() != HERE]

import html  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402

N = json.loads((HERE / "numbers.json").read_text(encoding="utf-8"))
SPEC = (HERE / "內容規格.md").read_text(encoding="utf-8")
PROMPT_PAGES = [4, 6, 10, 16, 20]
DARK = {1, 22}
PAGES = 22
NUM_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d{4,}(?:\.\d+)?)(?![\w])")
URL_RE = re.compile(r"https?://[^\s<>\"'`）)」]+")
CJK_RE = re.compile(r"[㐀-䶿一-鿿]")
ZH_ANY_RE = re.compile(r"[　-〿㐀-䶿一-鿿＀-￯]")   # 中文字＋全形標點（英文輸出都不該有）
MAINLAND = ["軟件", "視頻", "信息", "數據庫", "默認", "優化", "質量", "屏幕", "鼠標", "點擊", "網絡", "用戶", "登錄", "鏈接", "文檔"]
SIMPLIFIED = "们这说时银资产负债权证数发现应该进过还国东华习题页码设检验写读为么问统务汇贷币级报录网络单图"   # 只放「簡體專用」字（益、據這類繁簡同形的別放）
ALLOWED_YEARS = set(range(2021, 2027))
ALLOWED_MISC = {1280, 720}
ALLOWED_SESSION = {1116, 1118}   # 場次日期 MMDD（本夾名 -1116、交付夾 第二輪-1116-1118），不是金額

out = {"PASS": [], "WARN": [], "FAIL": [], "INFO": []}


def say(level, msg):
    out[level].append(msg)


# ---- numbers.json 裡所有數字 ----------------------------------------------------------------------
KNOWN, JSON_URLS = set(), set()


def walk(x):
    if isinstance(x, bool) or x is None:
        return
    if isinstance(x, (int, float)):
        KNOWN.add(round(abs(float(x)), 6))
    elif isinstance(x, str):
        for u in URL_RE.findall(x):
            JSON_URLS.add(u)
        for m in NUM_RE.findall(URL_RE.sub(" ", x)):
            KNOWN.add(round(float(m.replace(",", "")), 6))
    elif isinstance(x, dict):
        for k, v in x.items():
            walk(k)
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)


walk(N)
DERIVED = {}
for code, b in N["banks"].items():
    a = b["stress"]["A_deposit_run_10pct"]
    DERIVED[round(float(a["liquid_assets_before"] - a["liquid_used"]), 6)] = f"{code} 情境 A 付完剩下＝liquid_assets_before − liquid_used"


def num_ok(s):
    v = round(float(s.replace(",", "")), 6)
    if v in KNOWN or v in DERIVED:
        return True
    if "," not in s and "." not in s and int(v) in ALLOWED_YEARS | ALLOWED_MISC | ALLOWED_SESSION:
        return True
    return False


# ---- 讀檔 -----------------------------------------------------------------------------------------
def visible(src):
    s = re.sub(r"<(style|script)\b.*?</\1>", " ", src, flags=re.S | re.I)
    s = re.sub(r"data:[^\"')\s]+", " ", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return html.unescape(s)


def files():
    fs = []
    fs += sorted((HERE / "deck/build").glob("*/[0-9][0-9].html"))
    fs += sorted(HERE.glob("deck-*.html"))
    fs += sorted((HERE / "student").glob("*.html"))
    fs += sorted((HERE / "teacher").glob("*.md"))
    fs += sorted((HERE / "demo").rglob("*.md"))
    return [f for f in fs if f.is_file()]


def rel(p):
    return p.relative_to(HERE).as_posix()


def is_deck(p):
    return p.parent.parent.name == "build" or p.name.startswith("deck-")


# ---- ① 數字 ＋ ② 禁字 ------------------------------------------------------------------------------
n_numbers = 0
for f in files():
    raw = f.read_text(encoding="utf-8", errors="replace")
    text = visible(raw) if f.suffix == ".html" else raw
    for u in URL_RE.findall(text):
        if u not in JSON_URLS:
            say("FAIL" if is_deck(f) else "WARN", f"① {rel(f)}：網址不在 numbers.json：{u}")
    body = URL_RE.sub(" ", text)
    bad = sorted({m for m in NUM_RE.findall(body) if not num_ok(m)})
    n_numbers += len(NUM_RE.findall(body))
    if bad:
        say("FAIL", f"① {rel(f)}：numbers.json 找不到的數字 {bad}")
    hits = [w for w in MAINLAND if w in text]
    simp = sorted({c for c in text if c in SIMPLIFIED})
    if hits or simp:
        say("FAIL", f"② {rel(f)}：大陸用語 {hits} 簡體字 {simp}")
nf = len(files())
if not any(x.startswith("①") for x in out["FAIL"]):
    say("PASS", f"① {nf} 個檔、{n_numbers} 個 ≥4 位數的數字，全部在 numbers.json（或允許清單、衍生數）找得到")
if not any(x.startswith("②") for x in out["FAIL"]):
    say("PASS", f"② {nf} 個檔沒有大陸用語與簡體字抽樣")
for v, why in DERIVED.items():
    say("INFO", f"① 衍生數 {v:,.0f}：{why}（建議洄瀾把它加進 bank_numbers.py，就不必在這裡認）")

# ---- ③ 提示語逐字 ----------------------------------------------------------------------------------
sec = SPEC.split("## 三、", 1)[1].split("\n## 四、", 1)[0]
blocks = re.findall(r"```\n(.*?)\n```", sec, re.S)
if len(blocks) != 10:
    say("FAIL", f"③ 內容規格.md §三 應有 10 段提示語，讀到 {len(blocks)}")
else:
    want = {"zh": blocks[:5], "en": blocks[5:]}
    bad3 = 0
    for lang in ("zh", "en"):
        for i, pg in enumerate(PROMPT_PAGES):
            f = HERE / f"deck/build/{lang}/{pg:02d}.html"
            got = re.findall(r'<pre class="ec-ptext">(.*?)</pre>', f.read_text(encoding="utf-8"), re.S) if f.exists() else []
            if len(got) != 1 or html.unescape(got[0]) != want[lang][i]:
                bad3 += 1
                say("FAIL", f"③ {lang} p{pg}：提示語{'①②③④⑤'[i]}跟 §三 不一樣（或找不到框）")
        f = HERE / f"deck-{lang}.html"
        if f.exists():
            got = [html.unescape(x) for x in re.findall(r'<pre class="ec-ptext">(.*?)</pre>', f.read_text(encoding="utf-8"), re.S)]
            if got != want[lang]:
                bad3 += 1
                say("FAIL", f"③ deck-{lang}.html：五個提示語框跟 §三 不一致（找到 {len(got)} 個）")
        # 其他頁不該冒出提示語框
        for f in sorted((HERE / f"deck/build/{lang}").glob("[0-9][0-9].html")):
            if int(f.stem) not in PROMPT_PAGES and 'class="ec-ptext"' in f.read_text(encoding="utf-8"):
                bad3 += 1
                say("FAIL", f"③ {lang} p{int(f.stem)}：不該有提示語框")
    if not bad3:
        say("PASS", "③ 中英各五段提示語，build 每頁與打包單檔都跟 內容規格.md §三 逐字相同（含標點、換行）")

# ---- ④ 零外部資源 ----------------------------------------------------------------------------------
EXT = [re.compile(r"""\b(?:src|href)\s*=\s*["']?\s*(?:https?:)?//""", re.I),
       re.compile(r"""url\(\s*["']?\s*(?:https?:)?//""", re.I),
       re.compile(r"""@import\s+(?:url\(|["'])""", re.I)]
deck_files = [f for f in files() if is_deck(f)] + [HERE / "deck/deck.css", HERE / "deck/econ.css"]
bad4 = 0
for f in deck_files:
    if not f.exists():
        continue
    s = f.read_text(encoding="utf-8")
    for rx in EXT:
        m = rx.search(s)
        if m:
            bad4 += 1
            say("FAIL", f"④ {rel(f)}：外部資源 {s[max(0, m.start()-20):m.end()+40]!r}")
if not bad4:
    say("PASS", f"④ {len(deck_files)} 個 deck 檔（含兩份 CSS）沒有外部 src／href／url(／@import")

# ---- ⑤ 頁數與深底 ---------------------------------------------------------------------------------
bad5 = 0
for lang in ("zh", "en"):
    fs = sorted((HERE / f"deck/build/{lang}").glob("[0-9][0-9].html"))
    if [int(f.stem) for f in fs] != list(range(1, PAGES + 1)):
        bad5 += 1
        say("FAIL", f"⑤ build/{lang}：頁碼 {[int(f.stem) for f in fs]}，應 1..{PAGES}")
    dark = {int(f.stem) for f in fs if "slide--dark" in f.read_text(encoding="utf-8")}
    if dark != DARK:
        bad5 += 1
        say("FAIL", f"⑤ build/{lang}：深底頁 {sorted(dark)}，應 {sorted(DARK)}")
    f = HERE / f"deck-{lang}.html"
    if f.exists():
        secs = re.findall(r'<section class="sheet"[^>]*>(.*?)</section>', f.read_text(encoding="utf-8"), re.S)
        d2 = {i + 1 for i, s in enumerate(secs) if "slide--dark" in s}
        if len(secs) != PAGES or d2 != DARK:
            bad5 += 1
            say("FAIL", f"⑤ deck-{lang}.html：{len(secs)} 頁、深底 {sorted(d2)}")
    else:
        bad5 += 1
        say("FAIL", f"⑤ 沒有 deck-{lang}.html（先跑 build_web.py）")
if not bad5:
    say("PASS", f"⑤ 兩種語言各 {PAGES} 頁（build 與打包單檔一致）、深底頁＝1、22")

# ---- ⑥ 字數、語言純度 ------------------------------------------------------------------------------
def body_text(src):
    s = re.sub(r'<div class="(?:kicker|title[^"]*|footer-org)"[^>]*>.*?</div>', " ", src, flags=re.S)
    s = re.sub(r'<pre class="ec-ptext">.*?</pre>', " ", s, flags=re.S)
    s = re.sub(r'<(span|button) class="ec-(?:plab|copy)"[^>]*>.*?</\1>', " ", s, flags=re.S)
    s = re.sub(r'alt="[^"]*"', " ", s)
    return visible(s)


counts = {}
en_words = {}
bad6 = 0
for lang in ("zh", "en"):
    for f in sorted((HERE / f"deck/build/{lang}").glob("[0-9][0-9].html")):
        src = f.read_text(encoding="utf-8")
        n = len(CJK_RE.findall(body_text(src)))
        counts[f"{lang}{int(f.stem):02d}"] = n
        if lang == "zh" and n > 80:
            say("WARN", f"⑥ zh p{int(f.stem)}：正文（不含提示語框）中文 {n} 字 > 80")
        vis = visible(re.sub(r'alt="[^"]*"', " ", src))
        if lang == "en":
            cj = ZH_ANY_RE.findall(vis)
            if cj:
                bad6 += 1
                say("FAIL", f"⑥ en p{int(f.stem)}：英文版出現中文或全形標點 {''.join(cj)[:30]}")
        else:
            t = URL_RE.sub(" ", visible(re.sub(r'<pre class="ec-ptext">.*?</pre>', " ", src, flags=re.S)))
            for w in re.findall(r"[A-Za-z][A-Za-z\-]*(?: [A-Z][A-Za-z]+)*", t):
                en_words.setdefault(w, set()).add(int(f.stem))
say("INFO", "⑥ 每頁正文中文字數（不含提示語框）：" + "、".join(f"p{k[2:]}={v}" for k, v in counts.items() if k.startswith("zh")))
say("INFO", "⑥ 中文版出現的英文詞（頁）：" + "；".join(f"{w}({','.join(map(str, sorted(p)))})" for w, p in sorted(en_words.items())))
en_md = HERE / "deck/內容稿.en.md"
if en_md.exists():
    cj = ZH_ANY_RE.findall(en_md.read_text(encoding="utf-8"))
    if cj:
        bad6 += 1
        say("FAIL", f"⑥ deck/內容稿.en.md：出現中文或全形標點 {''.join(cj)[:30]}")
if not bad6:
    say("PASS", "⑥ 英文版 22 頁可見文字與 deck/內容稿.en.md 沒有中文、沒有全形標點")

# ---- ⑦ 矽谷銀行只用一個口徑（2026-11-15 洄瀾定：投影片只用表上算得出的差額；附註的 15,160 與它推出的 844 不上投影片） ----
V_SVB = N["banks"]["SVB"]["variants"]
BANNED_SVB = [f"{N['banks']['SVB']['htm_gross_unrealized_losses']:,}",
              f"{N['banks']['SVB']['lines']['equity']['value'] - N['banks']['SVB']['htm_gross_unrealized_losses']:,}"]
bad7 = 0
for f in [x for x in files() if is_deck(x)]:
    t = visible(f.read_text(encoding="utf-8"))
    hit = [b for b in BANNED_SVB if re.search(r"(?<![\d,])" + re.escape(b) + r"(?![\d,])", t)]
    if hit:
        bad7 += 1
        say("FAIL", f"⑦ {rel(f)}：矽谷銀行附註口徑的數字不該上投影片 {hit}")
if not bad7:
    say("PASS", f"⑦ 投影片沒有矽谷銀行附註口徑的 {'、'.join(BANNED_SVB)}（只用表上差額 {V_SVB['htm_fair_value_gap']:,}、{V_SVB['equity_if_htm_gap_recognized']:,}）")

for lv in ("PASS", "INFO", "WARN", "FAIL"):
    for m in out[lv]:
        print(lv, m)
print(f"== PASS {len(out['PASS'])}，WARN {len(out['WARN'])}，FAIL {len(out['FAIL'])}")
sys.exit(1 if out["FAIL"] else 0)
