# data/: the reports for this folder

> The agent downloads from these URLs and checks the sha256; if it cannot, open the URL in a browser and save the PDF here. PDFs are not in git. Same sha256 = same file.

| File name (save as) | What it is | Official URL | Pages | sha256 | Pages to look at |
|---|---|---|---:|---|---|
| `JPM-2025-annual-report.pdf` | JPMorgan Chase & Co. 2025 Annual Report (PDF pages 75–359 reprint Form 10-K pages 43–327) | https://www.jpmorganchase.com/content/dam/jpmc/jpmorgan-chase-and-co/investor-relations/documents/annualreport-2025.pdf | 364 | `2a3ee9733eafd01e7667c5540fbd797c4cc688d14f00638a877f5623d1316d9d` | **Consolidated balance sheets = PDF page 199 (10-K printed page 167)**; US$ millions; Business Segment & Corporate Results = PDF 94 (printed 62); uninsured deposits = PDF 135 (printed 103); loans-to-deposits and deposits as % of liabilities = PDF 136 (printed 104); HTM unrealized losses = PDF 261 (printed 229) |
| `SVB-2022-balance-sheet-excerpt.pdf` | Silicon Valley Bank (SVB Financial Group) Consolidated Balance Sheets, December 31, 2022: a one-page excerpt re-typeset for class, numbers as in the original | Course website: https://cwstedctw.github.io/money-banking-ai-checkup/files/SVB-2022-balance-sheet-excerpt.pdf ; original 10-K (web page only, no official PDF): https://www.sec.gov/Archives/edgar/data/719739/000071973923000021/sivb-20221231.htm | 1 | — (the excerpt is regenerated, so it has no fixed sha256) | Original 10-K printed page 95; uninsured deposits are on printed page 80 and are **not** in the excerpt |
