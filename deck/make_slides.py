#!/usr/bin/env python3
"""make_slides.py — 貨銀課 AI 第二輪「銀行體檢＋壓力測試」：一份頁面規格產兩種語言的 22 頁投影片。

用法：python -X utf8 make_slides.py
產出：build/zh/01.html…22.html（中文場 11/16，病人＝彰化銀行）、build/en/01.html…22.html（英文場 11/18，病人＝JPMorgan Chase）、
     內容稿.zh.md、內容稿.en.md（每頁文字；由本檔產生，別直接改）。
依據：`../內容規格.md`（2026-11-15 洄瀾寫，本案正本）§二 逐頁表、§三 提示語全文。
規則：
  - 數字一律 json.load `../numbers.json` 再格式化（千分位），本檔不手打任何金額或比率；頁碼也從 numbers.json 取。
  - 提示語在執行時從 `../內容規格.md` §三 的 ``` 區塊讀出（前五段中文、後五段英文），一字不漏印進提示語框。
  - 圖一律 HTML／CSS／SVG 真文字；零外部資源；深底 p1、p22。
只用 Python 標準函式庫。2026-11-15 建置者寫（從 aiot-course/weeks/w07/deck/make_slides.py 的產線改）。
"""
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
BUILD = HERE / "build"
N = json.loads((ROOT / "numbers.json").read_text(encoding="utf-8"))
CHB, JPM, SVB = N["banks"]["CHB"], N["banks"]["JPM"], N["banks"]["SVB"]
RD = N["ratio_definitions"]
RK = [r["key"] for r in RD]
CIRC = "①②③④⑤"


# ---- 從正本讀提示語（§三） ------------------------------------------------------------------------
def load_prompts():
    spec = (ROOT / "內容規格.md").read_text(encoding="utf-8")
    sec = spec.split("## 三、", 1)[1].split("\n## 四、", 1)[0]
    blocks = re.findall(r"```\n(.*?)\n```", sec, re.S)
    assert len(blocks) == 10, f"§三 應有 10 段提示語，讀到 {len(blocks)}"
    return {"zh": blocks[:5], "en": blocks[5:]}


PROMPTS = load_prompts()


# ---- 數字格式（只格式化，不計算；唯一例外見 left_after_run） --------------------------------------
def f(v):
    """千分位；負數照財報習慣加括號。"""
    return f"({abs(v):,})" if v < 0 else f"{v:,}"


def p2(v):
    return f"{v:.2f}"


def p1(v):
    return f"{v:.1f}"


def pg(s):
    """頁碼字串取開頭的數字（例："167 (Form 10-K numbering)" → "167"）。"""
    return re.match(r"\d+", str(s)).group(0)


def pages_in(title):
    return re.search(r"(\d+)\s*(?:頁|pages)", title).group(1)


def pct_in(scenario):
    return re.search(r"(\d+)%", scenario).group(1)


def left_after_run(bank):
    """情境 A 付完還剩多少＝流動資產 − 用掉的（numbers.json 沒有這一格，只做這一個減法；check_econ2.py 用同一條式子認它）。"""
    a = bank["stress"]["A_deposit_run_10pct"]
    return a["liquid_assets_before"] - a["liquid_used"]


RUN = pct_in(CHB["stress"]["A_deposit_run_10pct"]["scenario"])     # 10
SHOCK = pct_in(CHB["stress"]["B_rate_shock_5pct"]["scenario"])     # 5


def esc(s):
    return html.escape(s, quote=False)


def num(v):
    return f'<span class="ec-num">{f(v)}</span>'


def pgt(s):
    return f'<span class="ec-pg">{s}</span>'


# ---- 共用版面 --------------------------------------------------------------------------------------
ORG = {"zh": "國立東華大學　通識教育中心", "en": "National Dong Hwa University · General Education Center"}
SEAL_ALT = {"zh": "國立東華大學", "en": "National Dong Hwa University"}
ARCS = ('<div class="arc" style="width:520px;height:520px;right:-150px;top:-160px"></div>'
        '<div class="arc" style="width:340px;height:340px;right:-60px;top:-40px;border-color:rgba(230,242,242,.10)"></div>')
TAGS = {"zh": {"check": "檢查點", "hand": "✋ 互動"}, "en": {"check": "Checkpoint", "hand": "✋ Your turn"}}


def head(lang):
    hl = "zh-Hant" if lang == "zh" else "en"
    return (f'<!doctype html><html lang="{hl}"><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="../../deck.css"><link rel="stylesheet" href="../../econ.css"></head><body>')


def render(lang, p):
    dark = p["dark"]
    cls = "slide--dark" if dark else "slide--light"
    seal = "seal-white.webp" if dark else "seal-color.webp"
    big = " title--big" if p.get("big") else ""
    bot = ""
    if p.get("bot"):
        kind = p.get("kind", "check")
        bot = (f'<div class="ec-bot{" hand" if kind == "hand" else ""}"><b class="tag">{TAGS[lang][kind]}</b>'
               f'<span>{p["bot"]}</span></div>')
    return (f'{head(lang)}<div class="slide {cls}">{ARCS if dark else ""}<div class="kicker">{p["kicker"]}</div>'
            f'<div class="title{big}">{p["title"]}</div><hr class="rule">'
            f'<div class="ec-main{" top" if p.get("top") else ""}">{p["body"]}</div>{bot}'
            f'<div class="footer-org">{ORG[lang]}</div>'
            f'<img class="seal" src="../assets/{seal}" alt="{SEAL_ALT[lang]}"></div></body></html>')


def prompt_box(lang, i, size=""):
    """提示語框：左上標籤、右上複製鈕（打包後的單檔才有作用；列印隱藏）。內文＝§三原文，只做 HTML 跳脫。"""
    text = PROMPTS[lang][i - 1]
    if lang == "zh":
        lab = {1: "提示語 ① 照抄就好", 2: "提示語 ② 老師示範", 3: "提示語 ③ 照抄就好", 4: "提示語 ④ 照抄就好", 5: "提示語 ⑤ 回家用"}[i]
        btn = '<button class="ec-copy" type="button" data-done="已複製" data-sel="已選取，按 Ctrl+C">複製</button>'
    else:
        lab = {1: "PROMPT ① — COPY IT AS IS", 2: "PROMPT ② — TEACHER DEMO", 3: "PROMPT ③ — COPY IT AS IS",
               4: "PROMPT ④ — COPY IT AS IS", 5: "PROMPT ⑤ — FOR HOMEWORK"}[i]
        btn = '<button class="ec-copy" type="button" data-done="Copied" data-sel="Selected — press Ctrl+C">Copy</button>'
    return (f'<div class="ec-prompt {size}" data-prompt="{i}"><span class="ec-plab">{lab}</span>{btn}'
            f'<pre class="ec-ptext">{esc(text)}</pre></div>')


def card(h, body, cls=""):
    return f'<div class="ec-card {cls}">' + (f"<h4>{h}</h4>" if h else "") + f"{body}</div>"


# ---- 圖：矽谷銀行資產負債表（比例長條，SVG 真文字） ----------------------------------------------
def svb_bars(lang):
    L = SVB["lines"]
    A, loans, htm = L["assets"]["value"], L["loans"]["value"], L["htm"]["value"]
    dep, eq = L["deposits"]["value"], L["equity"]["value"]
    H, top, x1, x2, w = 318, 30, 4, 326, 300
    sc = H / A
    zh = lang == "zh"
    t = {
        "assets": "資產" if zh else "Assets",
        "liab": "負債與權益" if zh else "Liabilities and equity",
        "loans": "放款淨額" if zh else "Net loans",
        "htm": "持有至到期證券" if zh else "Held-to-maturity securities",
        "fv": (f"公允價值只有 {f(SVB['htm_fair_value'])}" if zh else f"fair value only {f(SVB['htm_fair_value'])}"),
        "other": "其他資產" if zh else "Other assets",
        "dep": "存款" if zh else "Total deposits",
        "oth_l": "其他負債" if zh else "Other liabilities",
        "eq": "股東權益" if zh else "Stockholders’ equity",
        "tot": (f"總資產 {f(A)}" if zh else f"Total assets {f(A)}"),
    }
    hl, hh = loans * sc, htm * sc
    ho = H - hl - hh
    hd, he = dep * sc, eq * sc
    hol = H - hd - he
    y_l, y_h, y_o = top, top + hl, top + hl + hh
    y_d, y_ol, y_e = top, top + hd, top + hd + hol
    s = [f'<svg class="ec-svg" viewBox="0 0 640 400" width="640" height="400" role="img" aria-label="{t["tot"]}">',
         f'<text x="{x1 + w/2}" y="20" text-anchor="middle" class="lbl">{t["assets"]}</text>',
         f'<text x="{x2 + w/2}" y="20" text-anchor="middle" class="lbl">{t["liab"]}</text>',
         f'<rect x="{x1}" y="{y_l}" width="{w}" height="{hl}" fill="#D6EBEA" stroke="#1A1A1A" stroke-width="1.5"/>',
         f'<text x="{x1 + 14}" y="{y_l + hl/2 + 6}" class="lbl">{t["loans"]}</text>',
         f'<text x="{x1 + w - 14}" y="{y_l + hl/2 + 6}" text-anchor="end" class="val">{f(loans)}</text>',
         f'<rect x="{x1}" y="{y_h}" width="{w}" height="{hh}" fill="#F6DFAE" stroke="#1A1A1A" stroke-width="1.5"/>',
         f'<text x="{x1 + 14}" y="{y_h + hh/2 - 4}" class="lbl">{t["htm"]}</text>',
         f'<text x="{x1 + w - 14}" y="{y_h + hh/2 - 4}" text-anchor="end" class="val">{f(htm)}</text>',
         f'<text x="{x1 + 14}" y="{y_h + hh/2 + 20}" class="sml" style="fill:#8A5A10;font-weight:700">{"（" + t["fv"] + "）" if zh else "(" + t["fv"] + ")"}</text>',
         f'<rect x="{x1}" y="{y_o}" width="{w}" height="{ho}" fill="#F1F1EC" stroke="#1A1A1A" stroke-width="1.5"/>',
         f'<text x="{x1 + 14}" y="{y_o + ho/2 + 6}" class="lbl" style="fill:#5F6B6B">{t["other"]}</text>',
         f'<rect x="{x2}" y="{y_d}" width="{w}" height="{hd}" fill="#D6EBEA" stroke="#1A1A1A" stroke-width="1.5"/>',
         f'<text x="{x2 + 14}" y="{y_d + hd/2 + 6}" class="lbl">{t["dep"]}</text>',
         f'<text x="{x2 + w - 14}" y="{y_d + hd/2 + 6}" text-anchor="end" class="val">{f(dep)}</text>',
         f'<rect x="{x2}" y="{y_ol}" width="{w}" height="{hol}" fill="#F1F1EC" stroke="#1A1A1A" stroke-width="1.5"/>',
         f'<text x="{x2 + 14}" y="{y_ol + hol/2 + 5}" class="sml" style="font-weight:700">{t["oth_l"]}</text>',
         f'<rect x="{x2}" y="{y_e}" width="{w}" height="{he}" fill="#E9A23B" stroke="#1A1A1A" stroke-width="1.5"/>',
         f'<text x="{x2 + w}" y="{y_e + he + 26}" text-anchor="end" class="lbl" style="fill:#8A5A10">▲ {t["eq"]} {f(eq)}</text>',
         f'<text x="{x1}" y="{top + H + 26}" class="lbl">{t["tot"]}</text>',
         "</svg>"]
    return "".join(s)


# ---- 圖：資產負債表簡圖（不帶數字，標比率號） ----------------------------------------------------
def bs_schema(lang):
    zh = lang == "zh"
    A = [("c1", "現金及存放央行" if zh else "Cash and deposits with banks", "", 54),
         ("c2", "證券投資" if zh else "Securities", "②", 70),
         ("c3", "放款" if zh else "Loans", "① ③", 120),
         ("c4", "其他" if zh else "Other", "", 46)]
    R = [("c3", "存款" if zh else "Deposits", "③ ④", 170),
         ("c4", "借入款與其他負債" if zh else "Borrowing and other liabilities", "④", 80),
         ("c5", "權益" if zh else "Equity", "⑤", 40)]

    def side(h, rows):
        return (f'<div class="side"><div class="hd">{h}</div>'
                + "".join(f'<div class="blk {c}" style="height:{ht}px"><span class="k">{k}</span><span class="tag">{t}</span></div>'
                          for c, k, t, ht in rows) + "</div>")
    return ('<div class="ec-bs" style="width:440px;flex:0 0 440px">'
            + side("資產" if zh else "Assets", A) + side("負債與權益" if zh else "Liabilities and equity", R) + "</div>")


def ratio_table(lang):
    zh = lang == "zh"
    rows = "".join(f'<tr><td class="c"><b>{CIRC[i]}</b></td><td style="white-space:nowrap"><b>{r[lang]}</b></td><td>{r["ask_" + lang]}</td></tr>'
                   for i, r in enumerate(RD))
    h = ("<th class=\"c\">#</th><th>比率</th><th>問的是</th>" if zh else "<th class=\"c\">#</th><th>Ratio</th><th>The question</th>")
    return f'<table class="ec-tb sm"><tr>{h}</tr>{rows}</table>'


def tacct(title, left, right, lang, blank=False):
    zh = lang == "zh"
    hA, hL = ("資產（減少）", "負債與權益（減少）") if zh else ("Assets (down)", "Liabilities and equity (down)")
    if blank:
        hA, hL = ("資產", "負債與權益") if zh else ("Assets", "Liabilities and equity")

    def col(h, rows):
        if blank:
            inner = '<div class="blankline"></div>' * 3
        else:
            inner = "".join(f'<div class="row"><span>{k}</span><span class="v{" z" if z else ""}">{v}</span></div>'
                            for k, v, z in rows)
        return f'<div><span class="hh">{h}</span>{inner}</div>'
    return f'<div class="ec-t"><div class="tt">{title}</div><div class="tb">{col(hA, left)}{col(hL, right)}</div></div>'


# ---- 22 頁規格 -------------------------------------------------------------------------------------
def pages(lang):
    zh = lang == "zh"
    P = CHB if zh else JPM            # 今天的病人
    PL = P["lines"]
    SA = P["stress"]["A_deposit_run_10pct"]
    SB = P["stress"]["B_rate_shock_5pct"]
    date = "2026-11-16" if zh else "2026-11-18"
    when = "11:35–12:25" if zh else "11:00–11:50"
    J = lambda a, b: a if zh else b
    out = []

    def add(n, kicker, title, body, bot="", kind="check", dark=False, big=False, top=False):
        out.append(dict(n=n, kicker=kicker, title=title, body=body, bot=bot, kind=kind, dark=dark, big=big, top=top))

    # p1 深
    add(1, J("貨幣銀行學 · AI 第二輪", "MONEY AND BANKING · AI SESSION 2"),
        J("銀行體檢：把財報交給 AI，<br>要它每一句指回頁碼", "Bank Check-up: Hand the Report to the AI<br>and Make It Cite the Page"),
        f'<div class="ec-sub">' + J(f"貨幣銀行學 AI 第二輪｜{date}｜{when}<br>陳文盛（東華大學通識教育中心）",
                                     f"Money and Banking, AI session 2 | {date} | {when}<br>Wen-Sheng (Ted) Chen · NDHU General Education Center")
        + "</div>"
        + '<div class="ec-chips">'
        + J(f"<span>今天的病人：彰化銀行</span><span>開場：矽谷銀行</span><span>對照：JPMorgan Chase</span>",
            f"<span>Today's patient: {esc(JPM['name_en'])}</span><span>Opening case: Silicon Valley Bank</span><span>For comparison: a Taiwan bank</span>")
        + "</div>", dark=True, big=True)

    # p2
    sep_l = J("<h4>9 月：先問 AI，再回官方來源查</h4><ol><li>問完要回官方查</li><li>AI 會補數字</li><li>交作業附揭露句</li></ol>",
              "<h4>September: ask an AI first, then check the official source</h4><ol><li>Check the official source after you ask</li><li>AI fills in numbers it does not have</li><li>Hand in work with a disclosure sentence</li></ol>")
    flow = J('<div class="st"><b>1</b>先把來源交給 AI</div><span class="ar">→</span><div class="st"><b>2</b>每一句要頁碼</div><span class="ar">→</span><div class="st"><b>3</b>自己回原文抽查</div>',
             '<div class="st"><b>1</b>Hand the source to the AI</div><span class="ar">→</span><div class="st"><b>2</b>A page for every sentence</div><span class="ar">→</span><div class="st"><b>3</b>Spot-check the original yourself</div>')
    add(2, J("回顧 · 今天多一步", "RECAP · ONE MORE STEP"), J("9 月學的，加一步", "What we did in September, plus one step"),
        '<div class="ec-cols">' + card("", sep_l) + '<div class="ec-card gold" style="flex:1.5 1 0"><h4>' + J("今天", "Today") + '</h4>'
        + f'<div class="ec-flow" style="margin-top:8px">{flow}</div></div></div>'
        + '<div class="ec-card"><h4>' + J("工具三選一，提示語都一樣", "Pick one tool; the prompts are the same") + "</h4>"
        + J("AI 筆記本（Gemini Notebook，原名 NotebookLM）／ChatGPT／Claude",
            "AI notebook (Gemini Notebook, formerly NotebookLM) / ChatGPT / Claude") + "</div>",
        J("手機或筆電先登入其中一個", "Log in to one of them on your phone or laptop now"), "hand")

    # p3
    three = J([("來源交給 AI，每句要頁碼", ""), ("五個比率看一家銀行怎麼做生意", ""), ("分辨「哪句有頁碼、哪句是 AI 推的」", "")],
              [("Give the AI the source; demand a page for every sentence", ""), ("Five ratios show how a bank uses its assets and how it is funded", ""),
               ("Tell apart “has a page number” from “the AI inferred it”", "")])
    add(3, J("今天的目標", "TODAY'S GOALS"), J("今天帶走三件事", "Three things to take home today"),
        '<div class="ec-three">' + "".join(f'<div class="c"><div class="n">{CIRC[i]}</div><div class="h">{h}</div></div>'
                                           for i, (h, _) in enumerate(three)) + "</div>",
        J("第 44 分鐘會回來對", "We come back to these at minute 44"))

    # p4 提示語 ①
    add(4, J("課文整理 · 提示語 ①", "STUDY GUIDE · PROMPT ①"), J("提示語 ①：把一章講義交給 AI", "Prompt ①: hand one chapter of notes to the AI"),
        '<div class="ec-side">' + J("用王老師給的那一章講義（PDF）上傳。AI 筆記本的答案旁有出處小標，點了會跳回原文那一頁。",
                                    "Upload the chapter of lecture notes (PDF) from Prof. Wang. In the AI notebook every answer carries small citation marks; click one and it jumps back to that page.")
        + "</div>" + prompt_box(lang, 1),
        J("照頁碼翻回去對一題：對的舉手", "Turn to the page it cites and check one question: hands up if it matches"), "hand")

    # p5 矽谷銀行
    Ls = SVB["lines"]
    add(5, J("開場案例 · 矽谷銀行", "OPENING CASE · SILICON VALLEY BANK"), J("開場：矽谷銀行，2023 年 3 月", "Opening: Silicon Valley Bank, March 2023"),
        '<div class="ec-cols" style="align-items:center">' + f'<div style="flex:0 0 640px">{svb_bars(lang)}</div>'
        + '<div style="display:flex;flex-direction:column;gap:14px">'
        + card(J("這是哪一張表", "What this is"),
               J(f"倒閉前最後一份年報的資產負債表<br>2022-12-31｜單位百萬美元<br>美國年報 10-K 第 {SVB['source']['printed_page']} 頁",
                 f"The balance sheet in its last annual report before it failed<br>December 31, 2022 | US$ million<br>Form 10-K, page {SVB['source']['printed_page']}"))
        + card(J("一句史實", "One fact"), J("2023-03-10 被監理機關接管。", "Taken over by its regulator on 2023-03-10."), "gold")
        + "</div></div>",
        J("先猜：問它表上沒有的數字，它會老實說嗎？", "Guess first: ask it for a number that is not on the sheet. Will it say so honestly?"), "hand")

    # p6 提示語 ②
    add(6, J("老師示範 · 提示語 ②", "TEACHER DEMO · PROMPT ②"), J("提示語 ②：三題，第三題問表上沒有的", "Prompt ②: three questions; the third asks for something not on the sheet"),
        prompt_box(lang, 2, "m" if zh else "s"),
        J("老師台上跑；看出處小標", "I run it up front; watch the citation marks"))

    # p7 揭曉
    V = SVB["variants"]
    left = J(f"持有至到期證券：帳面 {num(Ls['htm']['value'])}<br>括號裡的公允價值只有 {num(SVB['htm_fair_value'])}<br>"
             f"→ 差 <span class=\"num\">{f(V['htm_fair_value_gap'])}</span>，是權益 {num(Ls['equity']['value'])} 的 <span class=\"num\">{p1(V['htm_gap_pct_of_equity'])}%</span>"
             f"<div class=\"ec-note\" style=\"margin-top:6px\">兩個數字都印在資產負債表那一列 {pgt('第 ' + SVB['source']['printed_page'] + ' 頁')}</div>",
             f"Held-to-maturity securities: carrying amount {num(Ls['htm']['value'])}; fair value in parentheses {num(SVB['htm_fair_value'])}<br>"
             f"→ a gap of <span class=\"num\">{f(V['htm_fair_value_gap'])}</span> = <span class=\"num\">{p1(V['htm_gap_pct_of_equity'])}%</span> of equity {num(Ls['equity']['value'])}"
             f"<div class=\"ec-note\" style=\"margin-top:6px\">Both numbers are printed on that one balance-sheet line {pgt('p.' + SVB['source']['printed_page'])}</div>")
    right = J(f"未受保障存款 <span class=\"num\">${SVB['uninsured_deposits_bn']} billion</span><br>＝存款的 <span class=\"num\">{p1(V['uninsured_deposits_pct_of_deposits'])}%</span>"
              f"<div class=\"ec-note\" style=\"margin-top:6px\">在年報 {pgt('第 ' + SVB['extra_pages']['uninsured']['printed_page'] + ' 頁')}，不在資產負債表上</div>",
              f"Uninsured deposits <span class=\"num\">${SVB['uninsured_deposits_bn']} billion</span><br>= <span class=\"num\">{p1(V['uninsured_deposits_pct_of_deposits'])}%</span> of deposits"
              f"<div class=\"ec-note\" style=\"margin-top:6px\">On {pgt('p.' + SVB['extra_pages']['uninsured']['printed_page'])} of the 10-K, not on the balance sheet</div>")
    add(7, J("揭曉", "THE REVEAL"), J("揭曉：表上有的，和表上沒有的", "The reveal: what is on the sheet, and what is not"),
        '<div class="ec-cols">' + card(J("表上有揭露，只看帳面比率容易漏掉", "Disclosed on the sheet, but easy to miss when you only look at headline ratios"), left, "gold")
        + card(J("表上沒有", "Not on the sheet"), right) + "</div>"
        + '<div class="ec-cols">' + card("", J("AI 老實說「這份文件裡沒有」＝有根據的 AI", "The AI says “not in this document” = an AI that stays grounded"))
        + card("", J("硬答一個數字＝連讀了資料的 AI 也會補", "It makes up a number = even an AI that read the file fills gaps"), "red") + "</div>",
        J("出處要能點回去", "Every citation must click back to its page"))

    # p8 體檢是什麼
    add(8, J("方法 · 一張表、五個比率", "METHOD · ONE SHEET, FIVE RATIOS"), J("銀行體檢是什麼：一張表、五個比率", "What a bank check-up is: one sheet, five ratios"),
        '<div class="ec-cols" style="align-items:center">' + bs_schema(lang) + f"<div>{ratio_table(lang)}</div></div>",
        J("五個都只用資產負債表就算得出來", "All five come from the balance sheet alone"))

    # p9 今天的病人
    if zh:
        s1, s2 = CHB["source"], CHB["source_business"]
        body9 = ('<div class="ec-lead">為什麼挑它：銀行本身上市、不是金控，財報就是銀行自己的。</div>'
                 '<div class="ec-cols">'
                 + card("檔案一：114 年度財務報告", f"共 {pages_in(s1['title'])} 頁<br>合併資產負債表在 PDF 第 {s1['pdf_page']} 頁"
                        f"<div class=\"ec-note\">頁面下方印的頁碼是 {s1['printed_page']}</div>", "gold")
                 + card("檔案二：2025 年年報", f"共 {pages_in(s2['title'])} 頁<br>業務內容從 PDF 第 {s2['business_pdf_page']} 頁起"
                        f"<div class=\"ec-note\">看它的存款、放款各占多少</div>")
                 + card("單位與檔案在哪", "單位：新臺幣千元<br>e學苑或老師的共用筆記本"
                        "<div class=\"ec-note\">上課先傳 10 頁的財報就好；年報回家做經營方式時再傳</div>")
                 + "</div>")
    else:
        s1 = JPM["source"]
        body9 = ('<div class="ec-lead">Why this one: a U.S. bank whose annual report carries the full Form 10-K, so the balance sheet is in the same file.</div>'
                 '<div class="ec-cols">'
                 + card("The file: 2025 Annual Report", f"{pages_in(s1['title'])} pages<br>Consolidated balance sheets on PDF page {s1['pdf_page']}"
                        f"<div class=\"ec-note\">= page {pg(s1['printed_page'])} in the 10-K’s own numbering</div>", "gold")
                 + card("Two page numberings", "The front part and the 10-K each number their own pages. <b>Always say which one.</b>", "red")
                 + card("Units and where", "US$ million<br>On the course e-learning site or in the shared notebook"
                        f"<div class=\"ec-note\">Upload fails? Give it PDF page {s1['pdf_page']} only, or use the AI notebook</div>")
                 + "</div>")
    add(9, J("今天的病人", "TODAY'S PATIENT"), J("今天的病人：彰化銀行", f"Today's patient: {esc(JPM['name_en'])}"), body9,
        J("把財報 PDF 上傳到你的 AI（或開共用筆記本）", "Upload the report PDF to your AI (or open the shared notebook)"), "hand")

    # p10 提示語 ③
    add(10, J("銀行體檢 · 提示語 ③", "BANK CHECK-UP · PROMPT ③"), J("提示語 ③：銀行體檢", "Prompt ③: the bank check-up"),
        prompt_box(lang, 3, "m" if zh else "s"), J("貼上去，等它做表", "Paste it in and wait for the table"), top=True)

    # p11 agent
    src2 = J("公開資訊觀測站", "SEC EDGAR")
    steps = J(["自己開檔", "抄表、附頁碼", "算五個比率", "畫圖、寫一頁備忘", f"用第二個來源查自己（{src2}）"],
              ["Opens the files itself", "Copies the table with pages", "Computes the five ratios", "Draws a chart, writes a one-page memo", f"Checks itself against a second source ({src2})"])
    flow11 = '<span class="ar">→</span>'.join(f'<div class="st"><b>{i+1}</b>{s}</div>' for i, s in enumerate(steps))
    add(11, J("老師台上同時做", "MEANWHILE, UP FRONT"), J("老師台上同時做：把同一個任務交給桌面 AI agent", "Meanwhile I give the same task to a desktop AI agent"),
        '<div class="ec-cols">'
        + card(J("給它什麼", "What it gets"), J("Claude 桌面版（Code 分頁）<br>一個資料夾：兩份 PDF＋一份規則", "Claude desktop app (the Code tab)<br>One folder: two PDFs + one rules file"))
        + card(J("我只做一件事", "All I do"), J("按下去，先不等它，回來繼續上課。", "Press go, do not wait, and carry on with the class."), "gold")
        + "</div>" + f'<div class="ec-flow">{flow11}</div>',
        J("預測：它跟你的表會差在哪一格？", "Predict: which cell will differ between its table and yours?"), "hand")

    # p12 體檢表（空白）
    hd = J(["比率", "分子／分母（數字）", "算式", "比率", "PDF 頁碼", "我查過 ✓"],
           ["Ratio", "Numerator / denominator", "Formula", "Ratio", "PDF page", "Checked ✓"])
    rows12 = "".join(f'<tr><td><b>{CIRC[i]}</b> {r[lang]}</td>' + '<td class="blank"></td>' * 5 + "</tr>" for i, r in enumerate(RD))
    add(12, J("自己算", "DO THE MATH YOURSELF"), J("比率自己算：體檢表", "Compute the ratios yourself: the check-up sheet"),
        '<div class="ec-lead">' + J("AI 只負責找數字＋頁碼；比率用計算機或試算表範本自己算。",
                                    "The AI only finds the numbers and their pages; you compute the ratios with a calculator or the spreadsheet template.") + "</div>"
        + '<table class="ec-tb"><tr>' + "".join(f"<th>{h}</th>" for h in hd) + f"</tr>{rows12}</table>"
        + '<div class="ec-note">' + J(f"單位：＿＿　年度欄：＿＿　合併或個體：＿＿", "Units: ____ &nbsp; Year column: ____ &nbsp; Consolidated? ____") + "</div>",
        J("五格都有頁碼", "All five rows have a page number"))

    # p13 抽查
    if zh:
        py = CHB["prior_year"]
        three13 = ('<div class="ec-three">'
                   '<div class="c"><div class="n">1</div><div class="h">單位</div><div class="e">千元，不是元</div></div>'
                   '<div class="c"><div class="n">2</div><div class="h">年度欄</div><div class="e">114 年那一欄，不是 113 年</div></div>'
                   '<div class="c"><div class="n">3</div><div class="h">合併或個體</div><div class="e">標題寫「合併資產負債表」</div></div></div>')
        errs = (f"<li>三行金融資產只加一行（三行相加＝{num(CHB['base']['securities'])}）</li>"
                f"<li>抄到 113 年欄（放款 114 年 {num(CHB['lines']['loans']['value'])}，113 年 {num(py['loans'])}）</li>"
                "<li>把千元當元</li><li>拿到金控的報表</li>")
    else:
        three13 = ('<div class="ec-three">'
                   '<div class="c"><div class="n">1</div><div class="h">Units</div><div class="e">US$ million</div></div>'
                   '<div class="c"><div class="n">2</div><div class="h">Year column</div><div class="e">2025, not 2024</div></div>'
                   '<div class="c"><div class="n">3</div><div class="h">Consolidated?</div><div class="e">“Consolidated balance sheets”</div></div></div>')
        Vj = JPM["variants"]
        errs = (f"<li>PDF page {JPM['source']['pdf_page']} vs printed page {pg(JPM['source']['printed_page'])}</li>"
                f"<li>Gross loans {num(JPM['lines']['loans_gross']['value'])} vs net {num(JPM['lines']['loans']['value'])} "
                f"(loans ÷ deposits {p2(Vj['r3_gross_loans'])}% vs {p2(JPM['ratios_pct']['r3'])}%; the Firm reports {JPM['firm_reported']['loans_to_deposits_pct']}%)</li>"
                f"<li>Trading assets in or out (securities ÷ assets {p2(Vj['r2_including_trading_assets'])}% vs {p2(JPM['ratios_pct']['r2'])}%)</li>"
                f"<li>The 2024 column (net loans {num(JPM['prior_year']['loans'])})</li>")
    add(13, J("抽查", "SPOT-CHECK"), J("抽三格回原文查", "Check three cells against the original"),
        three13 + card(J("常見的錯", "Common errors"), f"<ul>{errs}</ul>", "red"),
        J("兩人一組各查三格，找到錯的舉手", "In pairs, check three cells each; hands up when you find an error"), "hand")

    # p14 agent 成品
    items = J(["跟你的表對一格、跟原文對一格", "它有沒有說哪一格沒把握", "它多做了什麼：圖、備忘、第二來源核對", "它錯在哪裡"],
              ["Compare one cell with your table and one with the original", "Did it say which cell it was unsure of?",
               "What extra did it do: chart, memo, second-source check", "Where did it go wrong?"])
    add(14, J("回頭看 agent", "BACK TO THE AGENT"), J("回頭看 agent 的成品", "Back to the agent’s output"),
        '<div class="ec-three" style="flex-wrap:wrap">' + "".join(
            f'<div class="c" style="flex:1 1 40%"><div class="n">{i+1}</div><div class="h">{s}</div></div>' for i, s in enumerate(items)) + "</div>",
        J("agent 也要抽查", "The agent gets spot-checked too"))

    # p15 壓力測試一
    liq = P["liquid_components"]
    unit = J("單位：新臺幣千元", "US$ million")
    three15 = "".join(f'<tr><td>{esc(PL[k]["label"])}</td><td class="r">{f(PL[k]["value"])}</td></tr>' for k in ["deposits"] + liq)
    add(15, J("壓力測試 · 情境一", "STRESS TEST · SCENARIO A"), J(f"壓力測試（一）：一成存款被提走", f"Stress test A: {RUN}% of deposits walk out"),
        '<div class="ec-lead">' + J(f"假設明天有一成的存款被提走。銀行先用手上的現金和存放央行、同業的錢付；不夠的呢？",
                                    f"Suppose {RUN}% of deposits are withdrawn tomorrow. The bank pays first from cash and deposits at other banks. What if that is not enough?") + "</div>"
        + '<div class="ec-cols" style="align-items:center">'
        + f'<div><table class="ec-tb"><tr><th>{J("要用的三個數字", "The three numbers you need")}</th><th class="r">{unit}</th></tr>{three15}</table></div>'
        + f'<div>{tacct(J("T 字帳：自己填", "T-account: fill it in"), [], [], lang, blank=True)}</div></div>'
        + '<div class="ec-note">' + J("假設：這兩列全部可動用；不夠就照帳面賣證券",
                                     "Assume both lines are fully usable; any shortfall is met by selling securities at book value") + "</div>",
        J("紙上先算 3 分鐘：夠不夠？", "Three minutes on paper first: is it enough?"), "hand")

    # p16 提示語 ④
    add(16, J("壓力測試 · 提示語 ④", "STRESS TEST · PROMPT ④"), J("提示語 ④：問 AI 哪幾行先動", "Prompt ④: ask the AI which lines move first"),
        prompt_box(lang, 4, "narrow" if zh else "m"), J("貼上去，拿自己算的對", "Paste it in and compare with what you worked out"))

    # p17 對照
    ra = SA["ratios_after"]
    rb = P["ratios_pct"]
    rt = "".join(f'<tr><td><b>{CIRC[i]}</b> {r[lang]}</td><td class="r">{p2(rb[k])}%</td><td class="r">→</td><td class="r"><b>{p2(ra[k])}%</b></td></tr>'
                 for i, (r, k) in enumerate(zip(RD, RK)))
    if zh:
        verdict = (f"一成存款 {num(SA['deposit_outflow'])}<br>手上流動資產 {num(SA['liquid_assets_before'])}<br>"
                   f"<b style=\"color:var(--red)\">不夠，差 {f(SA['shortfall_after_liquid'])}</b> → 要賣證券或向同業、央行借")
        L17 = [("流動資產", "−" + f(SA["liquid_used"]), False), ("證券", "−" + f(SA["securities_sold_book"]), False)]
        R17 = [(esc(PL["deposits"]["label"]), "−" + f(SA["deposit_outflow"]), False), ("權益", "不變", True)]
    else:
        verdict = (f"{RUN}% of deposits {num(SA['deposit_outflow'])}<br>Cash and deposits with banks {num(SA['liquid_assets_before'])}<br>"
                   f"<b style=\"color:var(--green)\">Enough: {f(left_after_run(JPM))} left over</b>")
        L17 = [("Cash and deposits with banks", "−" + f(SA["liquid_used"]), False)]
        R17 = [("Deposits", "−" + f(SA["deposit_outflow"]), False), ("Equity", "unchanged", True)]
    infer = J("<span class=\"ec-tagl inf\">推論</span>賣證券會不會虧？同業借得到嗎？存戶為什麼提？",
              "<span class=\"ec-tagl inf\">inference</span>Would selling securities lose money? Could it borrow from other banks? Why are depositors leaving?")
    add(17, J("壓力測試 · 對答案", "STRESS TEST · ANSWER"), J("對照：哪句有頁碼、哪句是推的", "Compare: which sentences have a page, which are inferred"),
        '<div class="ec-cols">'
        + '<div style="display:flex;flex-direction:column;gap:10px">' + card(J("夠不夠", "Enough?"), verdict, "gold")
        + tacct(J("T 字帳（參考答案：假設照帳面賣證券、不借款）", "T-account (answer key: securities sold at book, no borrowing)"), L17, R17, lang) + "</div>"
        + '<div style="display:flex;flex-direction:column;gap:10px">'
        + f'<table class="ec-tb sm"><tr><th>{J("五個比率", "Five ratios")}</th><th class="r">{J("之前", "Before")}</th><th></th><th class="r">{J("之後", "After")}</th></tr>{rt}</table>'
        + card(J("表上沒有、是推論的句子", "Not on the statement: these are inferences"), infer) + "</div>"
        + "</div>",
        J("AI 的每一句，你標得出「表上／算的／推論」嗎", "Can you label every AI sentence “on the statement / calculated / inference”?"))

    # p18 壓力測試二
    if zh:
        rec = SB["recognized_losses"]
        k_tp, k_oci = PL["fvtpl"]["label"], PL["fvoci"]["label"]
        hid_k = PL["ac_debt"]["label"]
        seen = (f"<div class=\"ec-kv\"><span class=\"k\">進損益：{esc(k_tp)}</span><span class=\"v\">−{f(rec[k_tp])}</span></div>"
                f"<div class=\"ec-kv\"><span class=\"k\">進權益：{esc(k_oci)}</span><span class=\"v\">−{f(rec[k_oci])}</span></div>"
                f"<div style=\"margin-top:6px\">權益 {num(PL['equity']['value'])} → <b>{f(SB['equity_after_recognized'])}</b>　｜　"
                f"權益 ÷ 總資產 {p2(P['ratios_pct']['r5'])}% → <b>{p2(SB['r5_after_recognized'])}%</b></div>")
        hidden = (f"<div class=\"ec-kv\"><span class=\"k\">{esc(hid_k)}</span><span class=\"v\">−{f(SB['hidden_total'])}</span></div>"
                  f"<div style=\"margin-top:6px\">若也認列：權益 ÷ 總資產 → <b>{p2(SB['r5_if_hidden_also_marked'])}%</b></div>")
        svb = (f"持有至到期證券帳面與公允價值差 {num(SVB['variants']['htm_fair_value_gap'])}，權益只有 {num(SVB['lines']['equity']['value'])}"
               f"（{p1(SVB['variants']['htm_gap_pct_of_equity'])}%）<br>→ 認列後權益只剩 <b>{f(SVB['variants']['equity_if_htm_gap_recognized'])}</b>、"
               f"權益比 <b>{p2(SVB['variants']['r5_if_htm_gap_recognized'])}%</b>")
    else:
        afs_k = JPM["lines"]["afs"]["label"]; htm_k = JPM["lines"]["htm"]["label"]
        seen = (f"<div class=\"ec-kv\"><span class=\"k\">{esc(afs_k)} (into equity)</span><span class=\"v\">−{f(SB['recognized_total'])}</span></div>"
                f"<div style=\"margin-top:6px\">Equity {num(PL['equity']['value'])} → <b>{f(SB['equity_after_recognized'])}</b><br>"
                f"Equity ÷ assets {p2(P['ratios_pct']['r5'])}% → <b>{p2(SB['r5_after_recognized'])}%</b></div>")
        hidden = (f"<div class=\"ec-kv\"><span class=\"k\">{esc(htm_k)}</span><span class=\"v\">−{f(SB['hidden_total'])}</span></div>"
                  f"<div style=\"margin-top:6px\">If marked too: equity ÷ assets → <b>{p2(SB['r5_if_hidden_also_marked'])}%</b></div>"
                  f"<div class=\"ec-note\" style=\"margin-top:4px\">The Firm’s actual HTM unrealized loss: {f(JPM['firm_reported']['htm_gross_unrealized_losses'])} "
                  f"= {p1(JPM['variants']['htm_unrealized_loss_pct_of_equity'])}% of equity {pgt('p.' + JPM['extra_pages']['htm_unrealized']['printed_page'])}</div>")
        svb = (f"Silicon Valley Bank: HTM carrying amount minus fair value {num(SVB['variants']['htm_fair_value_gap'])} against equity of {num(SVB['lines']['equity']['value'])} "
               f"({p1(SVB['variants']['htm_gap_pct_of_equity'])}%) → recognized, equity falls to <b>{f(SVB['variants']['equity_if_htm_gap_recognized'])}</b>, "
               f"equity ÷ assets <b>{p2(SVB['variants']['r5_if_htm_gap_recognized'])}%</b>")
    add(18, J("壓力測試 · 情境二（老師講，學生不算）", "STRESS TEST · SCENARIO B (TEACHER TALKS IT THROUGH)"), J(f"壓力測試（二）：利率上升、債券跌 {SHOCK}%", f"Stress test B: rates rise, bond prices fall {SHOCK}%"),
        (card("表上看得到（單位：新臺幣千元）", seen)
         + '<div class="ec-cols">' + card("表上看不到（新臺幣千元）", hidden, "red")
         + card("接回矽谷銀行（百萬美元）", svb, "gold") + "</div>"
         if zh else
         '<div class="ec-cols">' + card("Shows up in the statements", seen, "wide")
         + card("Does not show on the face", hidden, "red") + "</div>"
         + card("Back to Silicon Valley Bank", svb, "gold") + '<div class="ec-note">US$ million</div>'),
        J("這就是矽谷銀行那一格", "This is exactly Silicon Valley Bank’s cell"))

    # p19 三家並排
    cols = [(CHB, J("彰化銀行", "CHB (Taiwan commercial bank)"), "2025-12-31"), (JPM, "JPMorgan Chase", "2025-12-31"),
            (SVB, J("矽谷銀行", "Silicon Valley Bank"), "2022-12-31")]
    th = "".join(f'<th class="r">{nm}<br><span class="q">{d}</span></th>' for _, nm, d in cols)
    tr = "".join(f'<tr><td><b>{CIRC[i]}</b> {r[lang]}</td>' + "".join(f'<td class="r">{p2(b["ratios_pct"][k])}%</td>' for b, _, _ in cols) + "</tr>"
                 for i, (r, k) in enumerate(zip(RD, RK)))
    one = J([f"<b>彰化銀行</b>：放款為主、存款為本",
             f"<b>JPMorgan Chase</b>：綜合銀行，放款只占三分之一；另有 {num(JPM['lines']['trading_assets']['value'])} 交易資產；{p1(JPM['variants']['uninsured_deposits_pct_of_deposits'])}% 存款未受保障",
             f"<b>矽谷銀行</b>：證券占 {p2(SVB['ratios_pct']['r2'])}%、存放比 {p2(SVB['ratios_pct']['r3'])}%、未受保障存款 {p1(SVB['variants']['uninsured_deposits_pct_of_deposits'])}%"],
            [f"<b>CHB</b>: mostly loans, funded by deposits",
             f"<b>JPMorgan Chase</b>: a universal bank; loans are only a third; plus {num(JPM['lines']['trading_assets']['value'])} of trading assets; {p1(JPM['variants']['uninsured_deposits_pct_of_deposits'])}% of deposits uninsured",
             f"<b>SVB</b>: securities {p2(SVB['ratios_pct']['r2'])}%, loans ÷ deposits {p2(SVB['ratios_pct']['r3'])}%, uninsured deposits {p1(SVB['variants']['uninsured_deposits_pct_of_deposits'])}%"])
    add(19, J("三家並排", "SIDE BY SIDE"), J("三家並排：從數字到經營方式", "Three banks side by side: how each uses its assets and is funded"),
        f'<table class="ec-tb sm"><tr><th>{J("比率", "Ratio")}</th>{th}</tr>{tr}</table>'
        + '<div class="ec-card" style="font-size:19px;line-height:1.5"><ul style="margin-left:20px">' + "".join(f"<li>{x}</li>" for x in one) + "</ul></div>",
        J("每一句都指得回哪一格", "Every sentence points back to a cell"))

    # p20 回家作業卡
    hw = J(["挑兩家銀行：一家台灣（<b>銀行本身</b>的財報，不要金控）、一家外國（年報或 10-K）",
            "第一張表：照提示語 ③，兩家各五個比率，<b>每格附 PDF 頁碼</b>；比率自己算",
            "抽三格回原文查，寫下結果（對或錯、單位、年度、合併或個體）",
            "深度研究初稿（提示語 ⑤）：挑三句回來源查，標出有沒有出處"],
           ["Pick two banks: one in Taiwan (the <b>bank’s own</b> report, not the holding company) and one abroad (annual report or 10-K)",
            "Table one: follow prompt ③; five ratios for each bank, <b>a PDF page in every cell</b>; compute the ratios yourself",
            "Check three cells against the original and write down the result (right or wrong, units, year, consolidated or not)",
            "A deep-research draft (prompt ⑤); check three sentences against their sources and mark “sourced / not sourced”"])
    add(20, J("回家作業卡", "HOMEWORK CARD"), J("回家作業卡：接第二次 AI 專題", "Homework card: the start of your second AI project"),
        '<div class="ec-cols">' + '<div class="ec-card" style="font-size:19px;line-height:1.45;flex:1.3 1 0"><ol>' + "".join(f"<li>{x}</li>" for x in hw) + "</ol>"
        + '<div class="ec-note" style="margin-top:6px">' + J("交什麼：表格＋抽查紀錄＋初稿與三句查核＋揭露句（最後一頁）。格式、分組、截止日以王老師 e學苑 公告為準。",
                                                            "Hand in: the table + spot-check log + draft with three checked sentences + the disclosure sentence (last slide). Format, groups and deadline: see Prof. Wang’s announcement.")
        + "</div></div>"
        + f'<div>{prompt_box(lang, 5, "m" if zh else "s")}</div></div>',
        J("拍下來", "Take a photo of this slide"), "hand")

    # p21 帶走三件事
    ev = J([f"提示語 ① 每題附頁碼，你翻回去對了一題；矽谷銀行那題，表上沒有的它該說「沒有」",
            f"彰化銀行放款 ÷ 總資產 {p2(CHB['ratios_pct']['r1'])}%，矽谷銀行證券 ÷ 總資產 {p2(SVB['ratios_pct']['r2'])}%：同樣是銀行，錢放在哪裡、從哪裡來完全不同",
            "壓力測試裡「賣證券會不會虧」「同業借得到嗎」表上都沒有，是推論"],
           [f"Prompt ① cited a page for every question and you checked one; on Silicon Valley Bank it should have said “not in this document”",
            f"JPMorgan Chase loans ÷ assets {p2(JPM['ratios_pct']['r1'])}%, Silicon Valley Bank securities ÷ assets {p2(SVB['ratios_pct']['r2'])}%: both banks, very different balance sheets",
            "In the stress test, “would selling securities lose money?” is not on the statement; it is an inference"])
    add(21, J("收尾", "WRAP-UP"), J("帶走三件事", "Three things to take home"),
        '<div class="ec-three">' + "".join(f'<div class="c"><div class="n">{CIRC[i]}</div><div class="h">{three[i][0]}</div>'
                                           f'<div class="e"><b>{J("今天的證據", "Today’s evidence")}</b>：{ev[i]}</div></div>' if zh else
                                           f'<div class="c"><div class="n">{CIRC[i]}</div><div class="h">{three[i][0]}</div>'
                                           f'<div class="e"><b>Today’s evidence</b>: {ev[i]}</div></div>' for i in range(3)) + "</div>")

    # p22 深
    if zh:
        links = [("彰化銀行 114 年度財務報告", CHB["source"]["url"]), ("彰化銀行 2025 年年報", CHB["source_business"]["url"]),
                 ("JPMorgan Chase 2025 年報", JPM["source"]["url"])]
        disc = "「本作業使用＿＿（AI 工具）協助＿＿（做了什麼）；數字已由本組對照原文核對。」"
        backup = "備援：AI 筆記本開不了 → ChatGPT／Claude 上傳 PDF；都不行 → 看老師示範、手算。"
    else:
        links = [("JPMorgan Chase 2025 Annual Report", JPM["source"]["url"]), ("JPMorgan Chase 2025 Form 10-K on SEC EDGAR", JPM["source"]["edgar_url"]),
                 ("SVB Financial Group 2022 Form 10-K on SEC EDGAR", SVB["source"]["url"])]
        disc = "“This assignment used ____ (AI tool) to help with ____ (what it did); our group checked every number against the original source.”"
        backup = "Backup: AI notebook will not open → upload the PDF to ChatGPT or Claude; nothing works → watch my demo and work it by hand."
    add(22, J("揭露句與連結", "DISCLOSURE AND LINKS"), J("揭露句與連結", "Disclosure sentence and links"),
        f'<div class="ec-disc">{disc}</div>'
        + '<div class="ec-card"><div class="ec-links">' + "".join(f'<div class="lk"><b>{esc(t)}</b><span class="ec-url">{esc(u)}</span></div>' for t, u in links)
        + "</div></div>" + f'<div class="ec-note" style="font-size:18px">{backup}</div>', dark=True)
    return out


# ---- 輸出 ------------------------------------------------------------------------------------------
FORBID = ("軟件", "視頻", "信息", "數據庫", "默認", "優化", "質量", "屏幕", "鼠標", "點擊", "網絡", "用戶", "登錄", "鏈接", "文檔", "搞", "幹")


def plain(s, lang="zh"):
    s = re.sub(r"<pre[^>]*>(.*?)</pre>", lambda m: "\n```\n" + html.unescape(m.group(1)) + "\n```\n", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " ", s)
    s = re.sub(r"<(svg).*?</\1>", "［自繪圖］" if lang == "zh" else "[figure]", s, flags=re.S)
    s = re.sub(r"</(div|li|tr|h4)>", " ", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[ \t]+", " ", html.unescape(s)).strip()


def main():
    for lang in ("zh", "en"):
        ps = pages(lang)
        assert [p["n"] for p in ps] == list(range(1, 23)), "頁碼要 1..22"
        assert [p["n"] for p in ps if p["dark"]] == [1, 22], "深底頁要是 1、22"
        d = BUILD / lang
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.html"):
            old.unlink()
        zh = lang == "zh"
        md = ([f"# 貨銀課 AI 第二輪投影片內容稿（中文場 11/16，彰化銀行）", "",
               "> **本檔由 `deck/make_slides.py` 產生**：改內容改那支程式（或上游 `內容規格.md`、`numbers.json`），別直接改這裡。", ""]
              if zh else
              ["# Money and Banking, AI session 2: slide text (English session, 2026-11-18, JPMorgan Chase)", "",
               "> **Generated by `deck/make_slides.py`**: change that script (or the upstream spec and `numbers.json`), not this file.", ""])
        for p in ps:
            text = html.unescape(p["body"] + p["title"] + p["kicker"] + p["bot"])
            bad = [w for w in FORBID if w in text]
            assert not bad, f'{lang} p{p["n"]} 出現禁字 {bad}'
            (d / f'{p["n"]:02d}.html').write_text(render(lang, p), encoding="utf-8", newline="\n")
            dk = ("（深底）" if zh else " (dark)") if p["dark"] else ""
            md += [f'## {p["n"]}{dk}{"　" if zh else " "}{plain(p["title"], lang)}', "",
                   f'- kicker{"：" if zh else ": "}{plain(p["kicker"], lang)}',
                   f'- {"內容：" if zh else "Content: "}{plain(p["body"], lang)}']
            if p["bot"]:
                md.append(f'- {"底部（" + TAGS[lang][p["kind"]] + "）：" if zh else "Bottom line (" + TAGS[lang][p["kind"]] + "): "}{plain(p["bot"], lang)}')
            md.append("")
        (HERE / f"內容稿.{lang}.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
        print(f"wrote {len(ps)} slides → build/{lang}/ + 內容稿.{lang}.md")


if __name__ == "__main__":
    main()
