Follow AGENTS.md in this folder and do the task in TASK.md (Prompt ③ plus the three extras); write the results to the output/ folder.

---

## Task (= slide Prompt ③, word for word)

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

## Three extras (for the agent only; the chat AIs do not get these)

1. **Draw one chart of the five ratios**: this time compute the ratios yourself (two decimals) and save a bar chart to `output/ratios-chart.png`, with the value on each bar.
2. **Write a one-page memo** (`output/memo.md`): using the report's business-segment pages, explain how this bank makes money and what the five ratios tell us. Put file name and PDF page after every factual sentence; mark your own reasoning "(inference)".
3. **Finally, list the cells where the second source disagrees** (`output/second-source-check.md`): check every cell against SEC EDGAR XBRL companyfacts for FY2025 and list "my number / EDGAR / same?" for each. If all agree, say so; if you could not check, say so.
