"""Build the one-page SVB 2022 balance-sheet excerpt PDF from numbers.json, then verify it.

Run (from anywhere):  python -X utf8 make_svb_excerpt.py
Output: SVB-2022-balance-sheet-excerpt.pdf (same folder) and ../../qa/svb-excerpt-check.txt
All labels, row order and numbers come from numbers.json banks.SVB.excerpt_rows — nothing typed by hand.
"""
import html
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
NUMBERS = ROOT / "numbers.json"
OUT_PDF = HERE / "SVB-2022-balance-sheet-excerpt.pdf"
OUT_HTML = ROOT / "qa" / "svb-excerpt.html"
CHECK = ROOT / "qa" / "svb-excerpt-check.txt"

TITLE = "SVB Financial Group and Subsidiaries — Consolidated Balance Sheets (excerpt)"
TOTAL_ROWS = {"Total investment securities", "Net loans", "Total assets", "Total deposits",
              "Total liabilities", "Total SVBFG stockholders’ equity", "Total equity",
              "Total liabilities and total equity"}


def fmt(v):
    if v is None:
        return ""
    s = f"{abs(v):,}"
    return f"({s})" if v < 0 else s


def build_html(svb):
    rows = []
    for label, y22, y21 in svb["excerpt_rows"]:
        if y22 is None and y21 is None:
            rows.append(f'<tr class="sec"><td colspan="3">{html.escape(label)}:</td></tr>')
            continue
        cls = ' class="tot"' if label in TOTAL_ROWS else ""
        rows.append(f'<tr{cls}><td class="lab">{html.escape(label)}</td>'
                    f'<td class="num">{fmt(y22)}</td><td class="num">{fmt(y21)}</td></tr>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>SVB excerpt</title>
<style>
@page {{ size: A4; margin: 14mm 14mm 14mm 14mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; color:#111; font-size: 8.6pt; margin:0; }}
h1 {{ font-size: 12pt; margin: 0 0 2px 0; }}
.sub {{ font-size: 8.6pt; margin: 0 0 6px 0; color:#333; }}
table {{ width:100%; border-collapse: collapse; }}
th {{ text-align:right; border-bottom: 1px solid #111; padding: 2px 4px; font-size: 8.6pt; }}
th.lab {{ text-align:left; }}
td {{ padding: 1.6px 4px; vertical-align: top; }}
td.num {{ text-align:right; white-space: nowrap; width: 15%; }}
td.lab {{ padding-left: 12px; }}
tr.sec td {{ font-weight:bold; padding-top: 6px; }}
tr.tot td {{ font-weight:bold; border-top: 0.6px solid #555; }}
.foot {{ margin-top: 10px; font-size: 7.6pt; color:#333; border-top: 0.6px solid #999; padding-top: 5px; }}
</style></head><body>
<h1>{html.escape(TITLE)}</h1>
<p class="sub">Dollars in millions; columns = December 31</p>
<table><thead><tr><th class="lab"></th><th>2022</th><th>2021</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table>
<p class="foot">{html.escape(svb["excerpt_footer"])}</p>
</body></html>"""


def verify(svb):
    doc = fitz.open(OUT_PDF)
    lines = []
    lines.append(f"pages: {doc.page_count}")
    text = "\n".join(p.get_text() for p in doc)
    # collapse whitespace so wrapped labels still match
    flat = re.sub(r"\s+", " ", text)
    ok = doc.page_count == 1
    if TITLE not in flat:
        ok = False
        lines.append("FAIL title not found")
    else:
        lines.append("OK   title")
    # walk through rows in order: each label then its two numbers must appear after the previous match
    pos = 0
    for label, y22, y21 in svb["excerpt_rows"]:
        want_label = label + (":" if y22 is None and y21 is None else "")
        i = flat.find(want_label, pos)
        if i < 0:
            ok = False
            lines.append(f"FAIL label not found in order: {label}")
            continue
        pos = i + len(want_label)
        if y22 is None and y21 is None:
            lines.append(f"OK   [section] {label}")
            continue
        m = re.match(r"\s*(\(?[\d,]+\)?)\s+(\(?[\d,]+\)?)", flat[pos:])
        if not m:
            ok = False
            lines.append(f"FAIL numbers missing after: {label}")
            continue
        got = []
        for tok in m.groups():
            neg = tok.startswith("(")
            n = int(tok.strip("()").replace(",", ""))
            got.append(-n if neg else n)
        pos += m.end()
        same = got == [y22, y21]
        ok &= same
        lines.append(f"{'OK  ' if same else 'FAIL'} {label[:70]:<70} json={y22},{y21} pdf={got[0]},{got[1]}")
    foot = re.sub(r"\s+", " ", svb["excerpt_footer"])
    if foot in flat:
        lines.append("OK   footer")
    else:
        ok = False
        lines.append("FAIL footer not found")
    lines.append("RESULT: " + ("PASS — every cell equals numbers.json" if ok else "FAIL"))
    return ok, "\n".join(lines)


def main():
    svb = json.loads(NUMBERS.read_text(encoding="utf-8"))["banks"]["SVB"]
    OUT_HTML.parent.mkdir(exist_ok=True)
    OUT_HTML.write_text(build_html(svb), encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(OUT_HTML.as_uri())
        pg.pdf(path=str(OUT_PDF), format="A4", print_background=True, prefer_css_page_size=True)
        b.close()
    ok, report = verify(svb)
    CHECK.write_text(report + "\n", encoding="utf-8")
    print(report)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
