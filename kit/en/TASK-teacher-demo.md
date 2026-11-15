# Task (teacher's on-stage demo: Task 1 plus three extras)

**The teacher pastes:**

> Follow AGENTS.md in this folder and complete the task in TASK-teacher-demo.md; write the results to output/

## Task 1 (= slide Prompt ③, word for word)

```
Answer using only the JPMorgan Chase 2025 Annual Report I uploaded. Use nothing else.
Make a table of these items from the Consolidated balance sheets at December 31, 2025 (units as printed; say that they are US$ millions):
Total assets; Loans, net of allowance for loan losses; Available-for-sale securities; Held-to-maturity securities; Investment securities, net of allowance for credit losses; Trading assets; Deposits; Total liabilities; Total stockholders' equity.
After each number write: the PDF page it is on, the page number printed on that page, and the line name exactly as printed.
Then write out the formula for each of these five ratios (which cell over which cell); I will compute the ratios myself:
1. Loans ÷ Total assets
2. Securities ÷ Total assets (use "Investment securities, net"; tell me in one sentence whether trading assets should be included and why)
3. Loans ÷ Deposits
4. Deposits ÷ Total liabilities
5. Equity ÷ Total assets
Finish with one sentence: which column (year) you used and whether this is the consolidated statement.
If you cannot find a number, write "not found". Do not fill it in from any other source.
```

## Three extras (the students' Task 1 does not have these)

1. **Draw one chart of the five ratios**: this time compute the ratios yourself (two decimals) and save a bar chart to `output/ratios-chart.png`, with the value on each bar.
2. **Write a one-page memo** (`output/memo.md`): using the report's business-segment pages, explain where the bank's assets go, how it is funded, and what the five ratios tell us. Put file name and PDF page after every factual sentence; mark your own reasoning "(inference)".
3. **Finally, check yourself against a second source** (`output/second-source-check.md`): compare every cell with SEC EDGAR XBRL companyfacts for JPMorgan Chase & Co. (CIK 0000019617, `https://data.sec.gov/api/xbrl/companyfacts/CIK0000019617.json`, FY2025 10-K values) and list "my number / EDGAR / same?" for each; if all agree, say so. Read only, no login, no forms. SEC asks automated tools for a User-Agent header: use a generic one such as `classroom-demo admin@example.com`, never a real person's name or address. If you cannot reach it, write "second source not checked".

The table goes to `output/checkup-table.md`.
