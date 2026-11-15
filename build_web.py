"""把貨銀課 AI 第二輪的兩套 22 頁投影片各打包成離線單檔：deck-zh.html（11/16 中文場）、deck-en.html（11/18 英文場）。

用法：python -X utf8 build_web.py
先跑 deck/make_slides.py（build/zh、build/en 各 22 頁＋內容稿），再把 deck/deck.css＋deck/econ.css 內嵌、
校徽轉成 data URI、@import 整行拿掉——成品雙擊即播、左右鍵翻頁、零外部請求；提示語框的「複製」鈕在單檔裡可用。
校徽 deck/build/assets/ 不進 git（本夾 .gitignore），缺的話從 skills/course-intro/assets/ 複製。
（2026-11-15 從 aiot-course/weeks/w07/build_web.py 複製改：兩種語言各跑一次、頁數 22、拿掉 EDL 圖。）
只用 Python 標準函式庫。
"""
import base64, html, pathlib, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent
DECK = ROOT / 'deck'
BUILD = DECK / 'build'
SEAL_SRC = ROOT / 'deck' / 'assets'   # 校徽放 repo 自己的 deck/assets/
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml'}
PAGES = 22
TEXT = {
    'zh': {'LANG': 'zh-Hant', 'TITLE': '銀行體檢：把財報交給 AI｜貨幣銀行學 AI 第二輪（2026-11-16）',
           'BAR': '貨幣銀行學 AI 第二輪　銀行體檢＋壓力測試（2026-11-16）', 'TOOLS_LABEL': '投影片工具', 'TOC_LABEL': '選擇頁面',
           'FULL': '全螢幕', 'PRINT': '列印／PDF', 'NAV_LABEL': '翻頁', 'PREV': '上一頁', 'NEXT': '下一頁', 'FULL_FAIL': '請用瀏覽器全螢幕',
           'HINT': '左右方向鍵翻頁，Home／End 到第一頁／最後一頁。提示語框右上的「複製」可以把整段提示語複製走。投影片可離線開啟。'},
    'en': {'LANG': 'en', 'TITLE': 'Bank Check-up: Hand the Report to the AI | Money and Banking, AI session 2 (2026-11-18)',
           'BAR': 'Money and Banking, AI session 2 — Bank check-up and stress test (2026-11-18)', 'TOOLS_LABEL': 'Slide tools', 'TOC_LABEL': 'Go to slide',
           'FULL': 'Full screen', 'PRINT': 'Print / PDF', 'NAV_LABEL': 'Slide navigation', 'PREV': 'Previous', 'NEXT': 'Next', 'FULL_FAIL': 'Use the browser full screen',
           'HINT': 'Left and right arrow keys turn the page; Home / End jump to the first / last slide. The Copy button on each prompt box copies the whole prompt. Works offline.'},
}
SHEET = {'zh': '第{n}頁', 'en': 'Slide {n}'}


def ensure_seals():
    for name in ('seal-color.webp', 'seal-white.webp'):
        dst = BUILD / 'assets' / name
        if dst.exists():
            continue
        src = SEAL_SRC / name
        if not src.exists():
            sys.exit(f'找不到校徽 {name}：deck/build/assets/ 和 {SEAL_SRC} 都沒有')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f'copied {name} from {SEAL_SRC}')


def asset(m):
    path = BUILD / 'assets' / m.group(1)
    return f'data:{MIME[path.suffix.lower()]};base64,' + base64.b64encode(path.read_bytes()).decode()


def build(lang):
    t = TEXT[lang]
    styles = '\n'.join((DECK / n).read_text(encoding='utf8') for n in ['deck.css', 'econ.css'])
    styles = re.sub(r'(?m)^@import[^\n]*\n?', '', styles)
    slides, options = [], []
    files = sorted((BUILD / lang).glob('[0-9][0-9].html'))
    if len(files) != PAGES:
        sys.exit(f'build/{lang} 應有 {PAGES} 頁，實際 {len(files)} 頁')
    for p in files:
        text = p.read_text(encoding='utf8')
        body = re.search(r'<body>(.*)</body>', text, re.S).group(1)
        body = re.sub(r'\.\./assets/([\w.-]+)', asset, body)
        n = int(p.stem)
        slides.append(f'<section class="sheet" aria-label="{SHEET[lang].format(n=n)}">{body}</section>')
        title = re.search(r'<div class="title[^>]*>(.*?)</div>', text, re.S).group(1)
        title = re.sub(r'(?<=[A-Za-z0-9,])<br>', ' ', title).replace('<br>', '')
        title = re.sub('<[^>]+>', '', title)
        options.append(f'<option value="{n-1}">{n}. {html.escape(html.unescape(title))}</option>')
    shell = (ROOT / 'web-shell.html').read_text(encoding='utf8')
    for k, v in t.items():
        shell = shell.replace(f'<!--{k}-->', v if k == 'LANG' else html.escape(v, quote=False))
    shell = (shell.replace('<!--DECK_STYLES-->', styles)
                  .replace('<!--SLIDES-->', '\n'.join(slides))
                  .replace('<!--OPTIONS-->', ''.join(options)))
    left = re.findall(r'<!--[A-Z_]+-->', shell)
    if left:
        sys.exit(f'web-shell 還有沒換掉的佔位：{left}')
    shell = '\n'.join(line.rstrip() for line in shell.splitlines()) + '\n'
    out = ROOT / f'deck-{lang}.html'
    out.write_text(shell, encoding='utf8', newline='\n')
    print(f'Built self-contained {out.name} ({len(slides)} slides)')


if __name__ == '__main__':
    ensure_seals()
    subprocess.run([sys.executable, '-X', 'utf8', str(DECK / 'make_slides.py')], check=True)
    for lang in ('zh', 'en'):
        build(lang)
