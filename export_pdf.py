"""把兩套網頁投影片用 Chromium 印成 PDF：deck-zh.html → deck-zh.pdf、deck-en.html → deck-en.pdf（各 22 頁，1280×720）。

用法：python -X utf8 export_pdf.py（先跑 build_web.py）
需要 playwright（`pip install playwright` 後 `playwright install chromium`）。列印時「複製」鈕隱藏（@media print）。
PDF 不進 git（本夾 .gitignore）。印完用 PyMuPDF 回讀頁數、頁面尺寸、有沒有漏印出「複製／Copy」鈕，不對就 exit 1。
（2026-11-15 從 aiot-course/weeks/w07/export_pdf.py 複製改：兩種語言、加回讀。）
"""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    for source, output in [("deck-zh.html", "deck-zh.pdf"), ("deck-en.html", "deck-en.pdf")]:
        page.goto((ROOT / source).as_uri())
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(ROOT / output), prefer_css_page_size=True, print_background=True)
        print(output)
    browser.close()

try:
    import fitz
except ImportError:
    print("（沒有 PyMuPDF，跳過回讀）")
    sys.exit(0)
bad = 0
for name, btn in (("deck-zh.pdf", "複製"), ("deck-en.pdf", "Copy")):
    doc = fitz.open(ROOT / name)
    sizes = {(round(pg.rect.width), round(pg.rect.height)) for pg in doc}
    btn_pages = [i + 1 for i, pg in enumerate(doc) if btn in [w[4] for w in pg.get_text("words")]]
    print(f"{name}: {doc.page_count} 頁, 尺寸(pt) {sizes}, 印出「{btn}」鈕的頁 {btn_pages or '無'}")
    if doc.page_count != 22 or sizes != {(960, 540)} or btn_pages:
        bad += 1
        print(f"  ⚠️ {name} 不對（應 22 頁、1280×720 px＝960×540 pt、不印複製鈕）")
sys.exit(1 if bad else 0)
