# Tasks (English session: JPMorgan Chase & Co.)

**Paste this sentence to your agent:**

> Follow AGENTS.md in this folder and complete Task 1 in TASK.md.

When Task 1 is done and you have spot-checked it yourself, paste: "Now do Task 2 in TASK.md". Task 3 is homework.
(The "report I uploaded" in the prompts means the file in this folder's `data/`.)

## Task 1: Bank check-up (= slide Prompt ③)

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

Output: `output/checkup-table.md`

## Task 2: Stress test (= slide Prompt ④)

```
Continue from the table above. Suppose 10% of deposits are withdrawn tomorrow, and the bank pays first out of "Cash and due from banks" and "Deposits with banks" (take both lines from the same report I uploaded, and give the PDF page for each).
1. Which balance-sheet lines move, and by how much? Show it as T-accounts.
2. Is there enough cash? If not, where does the rest come from?
3. What do the five ratios become?
Label every sentence: a number from the statement, your own calculation, or your inference?
```

Output: `output/stress-test.md`

## Task 3 (homework): two banks of your own

1. Pick two banks: one in Taiwan, one abroad. For the Taiwan bank use **the bank's own** financial report (MOPS or the bank's website), not the financial holding company's consolidated report; for the foreign bank use its annual report or 10-K (company website or SEC EDGAR).
2. Put both PDFs in `data/`, or fill in the official URLs below for the agent to download:
   - Taiwan: ____________  URL: ____________
   - Abroad: ____________  URL: ____________
3. Do what Task 1 does, as a **two-column table** (one column per bank). Use each report's own line names; where the two banks' line names do not match, say which line you used and why.
4. Finish with a **three-cell spot-check list**: pick three cells and give the file name, PDF page and the number as printed, with two empty columns, "right / wrong" and "reason (units, year column, consolidated or not)", for me to fill in.

Output: `output/homework-two-banks.md`
