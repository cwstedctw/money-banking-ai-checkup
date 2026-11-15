# Rules for this folder (for the agent)

You are the live demo in a Money and Banking class. The teacher hands you a bank check-up task while the whole class does the same task with a chat AI; afterwards the class will check your output against the original report, cell by cell. **Being accurate, citing pages, and saying when you are unsure** matter more than doing a lot.

## Data

- Use only the files in `data/`:
  - `JPM-2025-annual-report.pdf`: JPMorgan Chase & Co. 2025 Annual Report (364 pages; the Form 10-K is inside it).
  - `SVB-2022-balance-sheet-excerpt.pdf`: Silicon Valley Bank 2022 balance sheet excerpt (not needed for this task unless the task says so).
- Do not fill in numbers from memory. If a number is not in the files, write "not found".

## Every number must carry

- File name + **PDF page** (physical page, counting from 1) + **the page number printed on that page** + **the line name exactly as printed**.
- This report has **two printed page numberings** (the annual-report front section and the Form 10-K section). Say which one you are quoting.
- Units as printed (US$ millions), which column (December 31, 2025, not 2024), and whether the statement is consolidated.

## Formulas

- For each ratio, write numerator = which cell, denominator = which cell, then the result (%, two decimals).

## Second-source check (only after the table is done)

- Check every cell against **SEC EDGAR XBRL companyfacts** for JPMorgan Chase & Co. (CIK 0000019617): `https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json`, FY2025 10-K values.
- Read only. Do not upload, log in, or submit any form. SEC asks automated tools to send a User-Agent header; use a generic one (for example `classroom-demo admin@example.com`), never a real person's name or address.
- If you cannot reach it, write "second source not checked". Do not pretend.

## Say when you are unsure

- Mark any cell you are not sure about with "⚠️ unsure" and the reason (hard to read, two pages disagree, line name differs from the task).

## Files

- Write everything to `output/`: `checkup-table.md` (table + formulas + ratios), `ratios-chart.png`, `memo.md` (one page), `second-source-check.md`.
- Draw the chart with Python (matplotlib).
- Do not modify anything in `data/`; do not upload any file anywhere; do not install anything that needs administrator rights.
