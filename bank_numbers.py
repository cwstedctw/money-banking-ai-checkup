#!/usr/bin/env python3
"""bank_numbers.py — 貨銀課 AI 第二輪（2026-11-16 中文場、11-18 英文場）的「數字唯一來源」。

三家銀行的原始數字只在這裡打一次（每個數字旁註出處與頁碼），五個比率、壓力測試情境的
推算全部由程式算出來，寫成 numbers.json 與 numbers.md。投影片、學生練習單、教師手記、
示範資料夾一律讀 numbers.json，不准自己手算、不准自己抄數字。

用法：python -X utf8 bank_numbers.py   （只用標準函式庫；在本資料夾執行）

原始數字的驗證（2026-11-15 洄瀾）：
- 彰銀：官網「財務報告」頁 114 年度財報 PDF（摘要版 10 頁）第 1 頁（紙本頁碼 8）的合併資產負債表，
  逐格對公開資訊觀測站（經 twstock 工具抓的 114Q4 合併資產負債表）——全部相同。
- JPMorgan Chase：2025 Annual Report PDF 第 199 頁（Form 10-K 紙本頁碼 167）的 Consolidated balance sheets，
  逐格對 SEC EDGAR XBRL companyfacts（CIK 19617，FY2025 10-K）——Assets／Deposits／Liabilities／
  StockholdersEquity／AFS／HTM／Loans net 全部相同；Trading assets 另與 PDF 第 87 頁（紙本 55）對過。
- 矽谷銀行（SVB Financial Group）：Form 10-K FY2022（2023-02-24 申報）紙本頁碼 95 的 Consolidated Balance Sheets
  （在內建瀏覧器打開 EDGAR 原檔抄的），逐格對 SEC XBRL companyfacts（CIK 719739）——全部相同。
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 原始數字（唯一可以手打數字的地方）
# ---------------------------------------------------------------------------
CHB = {
    "name_zh": "彰化商業銀行（彰銀，2801）", "name_en": "Chang Hwa Commercial Bank (CHB, TWSE 2801)",
    "date": "2025-12-31（民國 114 年 12 月 31 日）", "unit": "新臺幣千元（NT$ thousand）",
    "statement": "合併資產負債表（Consolidated balance sheet）",
    "source": {
        "file": "data/CHB-2025-FY-consolidated-financial-report.pdf",
        "title": "彰化銀行 114 年度財務報告（官網「財務報告」頁的摘要版，10 頁）",
        "url": "https://www.bankchb.com/chb_2a_resource/leap_do/gallery/1775714798658/114年度財報.pdf",
        "sha256": "27e72e334f13b794fad5ec0c8aa96095195645bec6eaa36656c2d3541abd153f",
        "pdf_page": 1, "printed_page": "8",
        "cross_check": "公開資訊觀測站 114Q4 合併資產負債表（twstock 工具，2026-11-15）全部相同",
    },
    "source_business": {
        "file": "data/CHB-2025-annual-report.pdf",
        "title": "彰化銀行 2025 年年報（股東會年報，123 頁，刊印日期 2026 年 3 月）",
        "url": "https://www.bankchb.com/chb_2a_resource/leap_do/annual_report_picture/1779097600166/彰化銀行2025年年報.pdf",
        "sha256": "2d19eb17fb948515b6dfce44c3f9cc7e62a4251c9d97220b7d3f4dda3c2705bb",
        "business_pdf_page": 82, "business_printed_page": "80",
        "business_note": "肆、營運概況 一、業務內容（存款業務、放款業務…的比重與變化）；財務狀況摘要在 PDF 第 98 頁（紙本 96）：資產總額 3,377,011,238、負債總額 3,156,684,183、權益總額 220,327,055，跟財報相同",
    },
    # 科目名稱照財報原字；數字＝財報第 1 頁「114年12月31日」欄
    "lines": {
        "cash": ("現金及約當現金", 38_807_540),
        "due_from_cb": ("存放央行及拆借銀行同業", 211_749_070),
        "fvtpl": ("透過損益按公允價值衡量之金融資產", 124_312_609),
        "fvoci": ("透過其他綜合損益按公允價值衡量之金融資產", 319_082_057),
        "ac_debt": ("按攤銷後成本衡量之債務工具投資", 542_424_600),
        "loans": ("貼現及放款－淨額", 2_067_768_378),
        "assets": ("資產總計", 3_377_011_238),
        "due_to_banks": ("央行及銀行同業存款", 333_816_006),
        "deposits": ("存款及匯款", 2_710_322_674),
        "bank_debentures": ("應付金融債券", 41_785_176),
        "liabilities": ("負債總計", 3_156_684_183),
        "equity": ("權益總計", 220_327_055),
    },
    "securities_components": ["fvtpl", "fvoci", "ac_debt"],
    "securities_note": "證券投資＝三行金融資產相加（財報沒有「證券投資」這一列，是我們定義的）",
    "liquid_components": ["cash", "due_from_cb"],
    "prior_year": {"assets": 3_172_721_131, "liabilities": 2_971_323_743, "equity": 201_397_388, "deposits": 2_630_356_510, "loans": 1_967_920_024},
}

JPM = {
    "name_zh": "摩根大通（JPMorgan Chase & Co.）", "name_en": "JPMorgan Chase & Co.",
    "date": "December 31, 2025", "unit": "US$ million",
    "statement": "Consolidated balance sheets",
    "source": {
        "file": "data/JPM-2025-annual-report.pdf",
        "title": "JPMorgan Chase & Co. 2025 Annual Report (364 pages; PDF pages 75–359 reprint pages 43–327 of the 2025 Form 10-K)",
        "url": "https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/annualreport-2025.pdf",
        "sha256": "2a3ee9733eafd01e7667c5540fbd797c4cc688d14f00638a877f5623d1316d9d",
        "pdf_page": 199, "printed_page": "167 (Form 10-K numbering)",
        "cross_check": "SEC EDGAR XBRL companyfacts, CIK 19617, FY2025 10-K filed 2026-02-13 (accession 0001628280-26-008131): identical",
        "edgar_url": "https://www.sec.gov/Archives/edgar/data/19617/000162828026008131/jpm-20251231.htm",
        # 2026-11-15 逐頁掃頁尾查的。PDF 第 75 頁（10-K 第 43 頁）目錄原文：
        # "Note: The following pages from JPMorgan Chase & Co.'s 2025 Form 10-K are not included herein: 1-42, 328"
        "structure": {
            "front_section_pdf_pages": "1-74", "front_section_note": "letters to shareholders etc.; own page numbers (PDF page 74 is printed 72)",
            "form10k_pdf_pages": "75-359", "form10k_pages_included": "43-327", "form10k_pages_not_included": "1-42, 328",
            "form10k_pdf_offset": 32, "toc_note_pdf_page": 75, "back_matter_pdf_pages": "360-364",
            "form10k_what": "the annual report a U.S. listed company must file with the SEC; the pages reprinted here are the MD&A, the audited financial statements and the notes",
        },
    },
    "extra_pages": {
        "selected_balance_sheet_analysis": {"pdf_page": 87, "printed_page": "55", "what": "Consolidated balance sheets analysis (same line items with % change)"},
        "business_segments": {"pdf_page": 94, "printed_page": "62", "what": "Business Segment & Corporate Results (how the firm makes money: CCB, CIB, AWM, Corporate)"},
        "segment_overview_front": {"pdf_page": "54-70", "printed_page": "52-67 (annual-report front section numbering)", "what": "Segment overviews in the front part of the annual report"},
        "liquidity_deposits": {"pdf_page": 135, "printed_page": "103", "what": "Firmwide estimated uninsured deposits $1,558.6 billion at Dec 31, 2025"},
        "deposit_ratios": {"pdf_page": 136, "printed_page": "104", "what": "Deposits as a % of total liabilities 63%; loans-to-deposits ratio 58% (the Firm's own table, uses gross loans $1,493.4bn)"},
        "ratios_summary": {"pdf_page": 76, "printed_page": "44", "what": "Loans-to-deposits ratio 58 (2025), 56 (2024), 55 (2023)"},
        "htm_unrealized": {"pdf_page": 261, "printed_page": "229", "what": "Note 10: total HTM securities amortized cost 270,134 / gross unrealized losses 17,053 / fair value 253,344; total investment securities gross unrealized losses 20,395"},
    },
    "lines": {
        "cash": ("Cash and due from banks", 21_742),
        "due_from_banks": ("Deposits with banks", 321_596),
        "fed_funds_sold": ("Federal funds sold and securities purchased under resale agreements", 336_426),
        "securities_borrowed": ("Securities borrowed", 286_191),
        "trading_assets": ("Trading assets", 802_873),
        "afs": ("Available-for-sale securities", 507_198),
        "htm": ("Held-to-maturity securities", 270_134),
        "investment_securities": ("Investment securities, net of allowance for credit losses", 777_332),
        "loans_gross": ("Loans", 1_493_429),
        "allowance": ("Allowance for loan losses", -25_765),
        "loans": ("Loans, net of allowance for loan losses", 1_467_664),
        "assets": ("Total assets", 4_424_900),
        "deposits": ("Deposits", 2_559_320),
        "fed_funds_purchased": ("Federal funds purchased and securities loaned or sold under repurchase agreements", 442_396),
        "short_term_borrowings": ("Short-term borrowings", 64_776),
        "trading_liabilities": ("Trading liabilities", 216_019),
        "long_term_debt": ("Long-term debt", 435_206),
        "liabilities": ("Total liabilities", 4_062_462),
        "equity": ("Total stockholders’ equity", 362_438),
    },
    "securities_components": ["afs", "htm"],
    "securities_note": "Securities investment = Investment securities, net of allowance (AFS + HTM). Trading assets (802,873) are NOT included: they are market-making inventory, mostly at fair value — ask students whether they should count",
    "liquid_components": ["cash", "due_from_banks"],
    "firm_reported": {"loans_to_deposits_pct": 58, "deposits_pct_of_liabilities": 63, "uninsured_deposits_bn": 1558.6, "htm_gross_unrealized_losses": 17_053, "afs_gross_unrealized_losses": 3_342},
    "prior_year": {"assets": 4_002_814, "liabilities": 3_658_056, "equity": 344_758, "deposits": 2_406_032, "loans": 1_323_643},
}

SVB = {
    "name_zh": "矽谷銀行（SVB Financial Group）", "name_en": "SVB Financial Group (Silicon Valley Bank)",
    "date": "December 31, 2022（倒閉前最後一份年報；銀行於 2023-03-10 被接管）", "unit": "US$ million",
    "statement": "Consolidated Balance Sheets",
    "source": {
        "file": "demo/svb/SVB-2022-balance-sheet-excerpt.pdf（我們重排的一頁摘錄，數字照原文）",
        "title": "SVB Financial Group Form 10-K for fiscal year 2022, filed 2023-02-24 (accession 0000719739-23-000021)",
        "url": "https://www.sec.gov/Archives/edgar/data/719739/000071973923000021/sivb-20221231.htm",
        "sha256": None,
        "pdf_page": None, "printed_page": "95",
        "cross_check": "SEC EDGAR XBRL companyfacts, CIK 719739, FY2022 10-K: identical (Assets, AFS, HTM, NotesReceivableNet 73,614, Deposits, Liabilities, StockholdersEquity 16,004)",
    },
    "extra_pages": {
        "uninsured": {"printed_page": "80", "what": "“the amount of estimated uninsured deposits in U.S. offices that exceed the FDIC insurance limit were $151.5 billion” (Dec 31, 2022)"},
        "htm_note": {"printed_page": "125", "what": "Total HTM securities: amortized cost 91,327 / gross unrealized losses (15,160) / fair value 76,169 / allowance 6 / net carrying 91,321"},
    },
    "lines": {
        "cash": ("Cash and cash equivalents", 13_803),
        "afs": ("Available-for-sale securities, at fair value (cost of $28,602)", 26_069),
        "htm": ("Held-to-maturity securities, at amortized cost (fair value of $76,169)", 91_321),
        "non_marketable": ("Non-marketable and other equity securities", 2_664),
        "investment_securities_total": ("Total investment securities", 120_054),
        "loans_gross": ("Loans, amortized cost", 74_250),
        "allowance": ("Allowance for credit losses: loans", -636),
        "loans": ("Net loans", 73_614),
        "assets": ("Total assets", 211_793),
        "deposits_noninterest": ("Noninterest-bearing demand deposits", 80_753),
        "deposits_interest": ("Interest-bearing deposits", 92_356),
        "deposits": ("Total deposits", 173_109),
        "short_term_borrowings": ("Short-term borrowings", 13_565),
        "long_term_debt": ("Long-term debt", 5_370),
        "liabilities": ("Total liabilities", 195_498),
        "equity": ("Total SVBFG stockholders’ equity", 16_004),
        "equity_total": ("Total equity (incl. noncontrolling interests)", 16_295),
    },
    "securities_components": ["afs", "htm"],
    "securities_note": "Securities investment = AFS + HTM (debt securities). The statement's own “Total investment securities” 120,054 also includes 2,664 of non-marketable equity securities",
    "liquid_components": ["cash"],
    "htm_fair_value": 76_169,
    "htm_gross_unrealized_losses": 15_160,
    "uninsured_deposits_bn": 151.5,
    # 給 demo/svb 摘錄頁用：10-K p.95 整張表（2022 與 2021 兩欄），行序照原文；(標籤, 2022, 2021)
    "excerpt_rows": [
        ("Assets", None, None),
        ("Cash and cash equivalents", 13_803, 14_586),
        ("Available-for-sale securities, at fair value (cost of $28,602 and $27,370, respectively, including $530 and $61 pledged as collateral, respectively)", 26_069, 27_221),
        ("Held-to-maturity securities, at amortized cost and net of allowance for credit losses of $6 and $7 (fair value of $76,169 and $97,227, respectively)", 91_321, 98_195),
        ("Non-marketable and other equity securities", 2_664, 2_543),
        ("Total investment securities", 120_054, 127_959),
        ("Loans, amortized cost", 74_250, 66_276),
        ("Allowance for credit losses: loans", -636, -422),
        ("Net loans", 73_614, 65_854),
        ("Premises and equipment, net of accumulated depreciation and amortization", 394, 270),
        ("Goodwill", 375, 375),
        ("Other intangible assets, net", 136, 160),
        ("Lease right-of-use assets", 335, 313),
        ("Accrued interest receivable and other assets", 3_082, 1_791),
        ("Total assets", 211_793, 211_308),
        ("Liabilities and total equity", None, None),
        ("Noninterest-bearing demand deposits", 80_753, 125_851),
        ("Interest-bearing deposits", 92_356, 63_352),
        ("Total deposits", 173_109, 189_203),
        ("Short-term borrowings", 13_565, 71),
        ("Lease liabilities", 413, 388),
        ("Other liabilities", 3_041, 2_467),
        ("Long-term debt", 5_370, 2_570),
        ("Total liabilities", 195_498, 194_699),
        ("Preferred stock", 3_646, 3_646),
        ("Common stock", 0, 0),
        ("Additional paid-in capital", 5_318, 5_157),
        ("Retained earnings", 8_951, 7_442),
        ("Accumulated other comprehensive income (loss)", -1_911, -9),
        ("Total SVBFG stockholders’ equity", 16_004, 16_236),
        ("Noncontrolling interests", 291, 373),
        ("Total equity", 16_295, 16_609),
        ("Total liabilities and total equity", 211_793, 211_308),
    ],
    "excerpt_footer": "Transcribed for classroom use from SVB Financial Group, Form 10-K for the fiscal year ended December 31, 2022 (filed 2023-02-24; SEC EDGAR accession 0000719739-23-000021), Consolidated Balance Sheets, page 95. Dollars in millions. Column “2021” = December 31, 2021.",
}

BANKS = {"CHB": CHB, "JPM": JPM, "SVB": SVB}

RATIOS = [
    ("r1", "放款 ÷ 總資產", "Loans ÷ Total assets", "錢主要拿去放款嗎？", "Does the money mainly go into loans?"),
    ("r2", "證券投資 ÷ 總資產", "Securities ÷ Total assets", "買了多少債券？", "How much is parked in securities?"),
    ("r3", "放款 ÷ 存款", "Loans ÷ Deposits", "存放比：存款有多少貸出去？", "Loan-to-deposit ratio: how much of the deposits is lent out?"),
    ("r4", "存款 ÷ 總負債", "Deposits ÷ Total liabilities", "資金靠存款，還是靠借？", "Funded by deposits, or by borrowing?"),
    ("r5", "權益 ÷ 總資產", "Equity ÷ Total assets", "自有資本有多厚？（未按風險加權，不是資本適足率）", "How thick is the equity cushion? (not risk-weighted; not the capital adequacy ratio)"),
]


def val(bank, key):
    return bank["lines"][key][1]


def ratios(bank, assets=None, loans=None, securities=None, deposits=None, liabilities=None, equity=None):
    assets = assets if assets is not None else val(bank, "assets")
    loans = loans if loans is not None else val(bank, "loans")
    securities = securities if securities is not None else sum(val(bank, k) for k in bank["securities_components"])
    deposits = deposits if deposits is not None else val(bank, "deposits")
    liabilities = liabilities if liabilities is not None else val(bank, "liabilities")
    equity = equity if equity is not None else val(bank, "equity")
    r = {
        "r1": loans / assets, "r2": securities / assets, "r3": loans / deposits,
        "r4": deposits / liabilities, "r5": equity / assets,
    }
    return {k: round(v * 100, 2) for k, v in r.items()}, dict(assets=assets, loans=loans, securities=securities, deposits=deposits, liabilities=liabilities, equity=equity)


def stress_deposit_run(bank, pct=0.10, fire_sale_discount=None):
    """存款被提走 pct；先用流動資產（現金＋存放央行／同業）付，不夠的賣證券（帳面；或打折賣）。"""
    dep = val(bank, "deposits")
    outflow = round(dep * pct)
    liquid = sum(val(bank, k) for k in bank["liquid_components"])
    shortfall = max(outflow - liquid, 0)
    liquid_used = min(outflow, liquid)
    securities0 = sum(val(bank, k) for k in bank["securities_components"])
    loss = 0
    securities_sold_book = shortfall
    if shortfall and fire_sale_discount:
        securities_sold_book = round(shortfall / (1 - fire_sale_discount))
        loss = securities_sold_book - shortfall
    assets = val(bank, "assets") - outflow - loss
    deposits = dep - outflow
    liabilities = val(bank, "liabilities") - outflow
    equity = val(bank, "equity") - loss
    securities = securities0 - securities_sold_book
    r, base = ratios(bank, assets=assets, securities=securities, deposits=deposits, liabilities=liabilities, equity=equity)
    return {
        "scenario": f"deposits -{int(pct*100)}%" + (f", securities sold at {int(fire_sale_discount*100)}% discount" if fire_sale_discount else ""),
        "deposit_outflow": outflow, "liquid_assets_before": liquid, "liquid_used": liquid_used,
        "shortfall_after_liquid": shortfall, "surplus_after_liquid": max(liquid - outflow, 0),
        "securities_sold_book": securities_sold_book, "loss_to_equity": loss,
        "t_account": {
            "assets_down": {bank["lines"][k][0]: None for k in bank["liquid_components"]} | {"liquid total used": liquid_used, "securities sold (book)": securities_sold_book},
            "liabilities_down": {bank["lines"]["deposits"][0]: outflow},
            "equity_down": loss,
        },
        "after": base, "ratios_after": r,
    }


def stress_rate_shock(bank, drop=0.05):
    """利率上升、債券價格跌 drop。入帳的（FVTPL／FVOCI／AFS）打進權益；攤銷後成本（AC／HTM）表上看不到。"""
    if bank is CHB:
        recognized = {"fvtpl": round(val(bank, "fvtpl") * drop), "fvoci": round(val(bank, "fvoci") * drop)}
        hidden = {"ac_debt": round(val(bank, "ac_debt") * drop)}
    elif bank is JPM:
        recognized = {"afs": round(val(bank, "afs") * drop)}
        hidden = {"htm": round(val(bank, "htm") * drop)}
    else:
        recognized = {"afs": round(val(bank, "afs") * drop)}
        hidden = {"htm": round(val(bank, "htm") * drop)}
    rec = sum(recognized.values()); hid = sum(hidden.values())
    securities0 = sum(val(bank, k) for k in bank["securities_components"])
    r_rec, base_rec = ratios(bank, assets=val(bank, "assets") - rec, securities=securities0 - rec, equity=val(bank, "equity") - rec)
    r_all, base_all = ratios(bank, assets=val(bank, "assets") - rec - hid, securities=securities0 - rec - hid, equity=val(bank, "equity") - rec - hid)
    return {
        "scenario": f"bond prices -{int(drop*100)}%",
        "recognized_losses": {bank["lines"][k][0]: v for k, v in recognized.items()}, "recognized_total": rec,
        "hidden_losses_not_on_balance_sheet": {bank["lines"][k][0]: v for k, v in hidden.items()}, "hidden_total": hid,
        "equity_after_recognized": base_rec["equity"], "r5_after_recognized": r_rec["r5"],
        "equity_if_hidden_also_marked": base_all["equity"], "r5_if_hidden_also_marked": r_all["r5"],
        "ratios_after_recognized": r_rec, "ratios_if_hidden_also_marked": r_all,
    }


def build():
    out = {"generated_by": "bank_numbers.py (2026-11-15 洄瀾)", "ratio_definitions": [dict(zip(("key", "zh", "en", "ask_zh", "ask_en"), r)) for r in RATIOS], "banks": {}}
    for code, bank in BANKS.items():
        r, base = ratios(bank)
        entry = {k: v for k, v in bank.items() if k != "lines"}
        entry["lines"] = {k: {"label": v[0], "value": v[1]} for k, v in bank["lines"].items()}
        entry["base"] = base
        entry["ratios_pct"] = r
        entry["variants"] = {}
        if code == "JPM":
            entry["variants"]["r3_gross_loans"] = round(val(bank, "loans_gross") / val(bank, "deposits") * 100, 2)
            entry["variants"]["r1_gross_loans"] = round(val(bank, "loans_gross") / val(bank, "assets") * 100, 2)
            entry["variants"]["r2_including_trading_assets"] = round((base["securities"] + val(bank, "trading_assets")) / val(bank, "assets") * 100, 2)
            entry["variants"]["htm_unrealized_loss_pct_of_equity"] = round(bank["firm_reported"]["htm_gross_unrealized_losses"] / val(bank, "equity") * 100, 1)
            entry["variants"]["uninsured_deposits_pct_of_deposits"] = round(bank["firm_reported"]["uninsured_deposits_bn"] * 1000 / val(bank, "deposits") * 100, 1)
        if code == "SVB":
            entry["variants"]["r3_gross_loans"] = round(val(bank, "loans_gross") / val(bank, "deposits") * 100, 2)
            entry["variants"]["r2_total_investment_securities"] = round(val(bank, "investment_securities_total") / val(bank, "assets") * 100, 2)
            entry["variants"]["r5_total_equity"] = round(val(bank, "equity_total") / val(bank, "assets") * 100, 2)
            # 課堂一律用表上算得出的「帳面－公允價值」差額 15,152（2026-11-15 立霧複驗：別跟附註的 15,160 混用）
            gap = val(bank, "htm") - bank["htm_fair_value"]
            entry["variants"]["htm_fair_value_gap"] = gap
            entry["variants"]["htm_gap_pct_of_equity"] = round(gap / val(bank, "equity") * 100, 1)
            entry["variants"]["equity_if_htm_gap_recognized"] = val(bank, "equity") - gap
            entry["variants"]["r5_if_htm_gap_recognized"] = round((val(bank, "equity") - gap) / (val(bank, "assets") - gap) * 100, 2)
            entry["variants"]["note_htm_gross_unrealized_losses_p125"] = bank["htm_gross_unrealized_losses"]
            entry["variants"]["htm_unrealized_loss_pct_of_equity"] = round(bank["htm_gross_unrealized_losses"] / val(bank, "equity") * 100, 1)
            entry["variants"]["uninsured_deposits_pct_of_deposits"] = round(bank["uninsured_deposits_bn"] * 1000 / val(bank, "deposits") * 100, 1)
            entry["variants"]["noninterest_bearing_pct_of_deposits"] = round(val(bank, "deposits_noninterest") / val(bank, "deposits") * 100, 1)
        if code == "CHB":
            entry["variants"]["securities_total"] = base["securities"]
            entry["variants"]["r1_vs_prior_year"] = round(bank["prior_year"]["loans"] / bank["prior_year"]["assets"] * 100, 2)
        entry["stress"] = {
            "A_deposit_run_10pct": stress_deposit_run(bank, 0.10),
            "A2_deposit_run_10pct_fire_sale_10pct": stress_deposit_run(bank, 0.10, fire_sale_discount=0.10),
            "B_rate_shock_5pct": stress_rate_shock(bank, 0.05),
        }
        out["banks"][code] = entry
    return out


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else f"{n:.2f}"


def write_md(out):
    L = ["# numbers.md — 由 bank_numbers.py 產生，別手改", ""]
    L.append("## 五個比率（%）")
    L.append("| # | 比率 | 彰銀 2025-12-31 | JPMorgan Chase 2025-12-31 | SVB 2022-12-31 |")
    L.append("|---|---|---:|---:|---:|")
    for i, rd in enumerate(out["ratio_definitions"], 1):
        k = rd["key"]
        L.append(f"| {i} | {rd['zh']} / {rd['en']} | {out['banks']['CHB']['ratios_pct'][k]} | {out['banks']['JPM']['ratios_pct'][k]} | {out['banks']['SVB']['ratios_pct'][k]} |")
    for code, b in out["banks"].items():
        L += ["", f"## {code}：{b['name_zh']}（{b['date']}；{b['unit']}）", f"來源：{b['source']['title']}；頁碼 PDF {b['source']['pdf_page']}／紙本 {b['source']['printed_page']}；交叉驗證：{b['source'].get('cross_check')}", ""]
        if b.get("extra_pages"):
            L.append("其他定位（頁碼都查過原檔）：")
            for k, v in b["extra_pages"].items():
                L.append(f"- {k}：PDF {v.get('pdf_page', '—')}／紙本 {v.get('printed_page', '—')}：{v.get('what')}")
            L.append("")
        L += ["| 科目（原文） | 金額 |", "|---|---:|"]
        for k, v in b["lines"].items():
            L.append(f"| {v['label']} | {fmt(v['value'])} |")
        L.append("")
        L.append("變體與對照：" + json.dumps(b["variants"], ensure_ascii=False))
        for sk, s in b["stress"].items():
            L.append("")
            L.append(f"**壓力測試 {sk}**：{json.dumps({k: v for k, v in s.items() if k != 't_account'}, ensure_ascii=False)}")
    (HERE / "numbers.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    out = build()
    (HERE / "numbers.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    write_md(out)
    for code, b in out["banks"].items():
        print(code, b["ratios_pct"], "| variants:", b["variants"])
        for sk, s in b["stress"].items():
            if sk.startswith("A"):
                print("   ", sk, "outflow", fmt(s["deposit_outflow"]), "liquid", fmt(s["liquid_assets_before"]), "shortfall", fmt(s["shortfall_after_liquid"]), "loss", fmt(s["loss_to_equity"]), "ratios", s["ratios_after"])
            else:
                print("   ", sk, "recognized", fmt(s["recognized_total"]), "hidden", fmt(s["hidden_total"]), "r5", s["r5_after_recognized"], "->", s["r5_if_hidden_also_marked"])
    print("wrote numbers.json / numbers.md")
