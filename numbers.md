# numbers.md — 由 bank_numbers.py 產生，別手改

## 五個比率（%）
| # | 比率 | 彰銀 2025-12-31 | JPMorgan Chase 2025-12-31 | SVB 2022-12-31 |
|---|---|---:|---:|---:|
| 1 | 放款 ÷ 總資產 / Loans ÷ Total assets | 61.23 | 33.17 | 34.76 |
| 2 | 證券投資 ÷ 總資產 / Securities ÷ Total assets | 29.19 | 17.57 | 55.43 |
| 3 | 放款 ÷ 存款 / Loans ÷ Deposits | 76.29 | 57.35 | 42.52 |
| 4 | 存款 ÷ 總負債 / Deposits ÷ Total liabilities | 85.86 | 63.0 | 88.55 |
| 5 | 權益 ÷ 總資產 / Equity ÷ Total assets | 6.52 | 8.19 | 7.56 |

## CHB：彰化商業銀行（彰銀，2801）（2025-12-31（民國 114 年 12 月 31 日）；新臺幣千元（NT$ thousand））
來源：彰化銀行 114 年度財務報告（官網「財務報告」頁的摘要版，10 頁）；頁碼 PDF 1／紙本 8；交叉驗證：公開資訊觀測站 114Q4 合併資產負債表（twstock 工具，2026-11-15）全部相同

| 科目（原文） | 金額 |
|---|---:|
| 現金及約當現金 | 38,807,540 |
| 存放央行及拆借銀行同業 | 211,749,070 |
| 透過損益按公允價值衡量之金融資產 | 124,312,609 |
| 透過其他綜合損益按公允價值衡量之金融資產 | 319,082,057 |
| 按攤銷後成本衡量之債務工具投資 | 542,424,600 |
| 貼現及放款－淨額 | 2,067,768,378 |
| 資產總計 | 3,377,011,238 |
| 央行及銀行同業存款 | 333,816,006 |
| 存款及匯款 | 2,710,322,674 |
| 應付金融債券 | 41,785,176 |
| 負債總計 | 3,156,684,183 |
| 權益總計 | 220,327,055 |

變體與對照：{"securities_total": 985819266, "r1_vs_prior_year": 62.03}

**壓力測試 A_deposit_run_10pct**：{"scenario": "deposits -10%", "deposit_outflow": 271032267, "liquid_assets_before": 250556610, "liquid_used": 250556610, "shortfall_after_liquid": 20475657, "surplus_after_liquid": 0, "securities_sold_book": 20475657, "loss_to_equity": 0, "after": {"assets": 3105978971, "loans": 2067768378, "securities": 965343609, "deposits": 2439290407, "liabilities": 2885651916, "equity": 220327055}, "ratios_after": {"r1": 66.57, "r2": 31.08, "r3": 84.77, "r4": 84.53, "r5": 7.09}}

**壓力測試 A2_deposit_run_10pct_fire_sale_10pct**：{"scenario": "deposits -10%, securities sold at 10% discount", "deposit_outflow": 271032267, "liquid_assets_before": 250556610, "liquid_used": 250556610, "shortfall_after_liquid": 20475657, "surplus_after_liquid": 0, "securities_sold_book": 22750730, "loss_to_equity": 2275073, "after": {"assets": 3103703898, "loans": 2067768378, "securities": 963068536, "deposits": 2439290407, "liabilities": 2885651916, "equity": 218051982}, "ratios_after": {"r1": 66.62, "r2": 31.03, "r3": 84.77, "r4": 84.53, "r5": 7.03}}

**壓力測試 B_rate_shock_5pct**：{"scenario": "bond prices -5%", "recognized_losses": {"透過損益按公允價值衡量之金融資產": 6215630, "透過其他綜合損益按公允價值衡量之金融資產": 15954103}, "recognized_total": 22169733, "hidden_losses_not_on_balance_sheet": {"按攤銷後成本衡量之債務工具投資": 27121230}, "hidden_total": 27121230, "equity_after_recognized": 198157322, "r5_after_recognized": 5.91, "equity_if_hidden_also_marked": 171036092, "r5_if_hidden_also_marked": 5.14, "ratios_after_recognized": {"r1": 61.64, "r2": 28.72, "r3": 76.29, "r4": 85.86, "r5": 5.91}, "ratios_if_hidden_also_marked": {"r1": 62.14, "r2": 28.14, "r3": 76.29, "r4": 85.86, "r5": 5.14}}

## JPM：摩根大通（JPMorgan Chase & Co.）（December 31, 2025；US$ million）
來源：JPMorgan Chase & Co. 2025 Annual Report (364 pages; contains the 2025 Form 10-K)；頁碼 PDF 199／紙本 167 (Form 10-K numbering)；交叉驗證：SEC EDGAR XBRL companyfacts, CIK 19617, FY2025 10-K filed 2026-02-13 (accession 0001628280-26-008131): identical

其他定位（頁碼都查過原檔）：
- selected_balance_sheet_analysis：PDF 87／紙本 55：Consolidated balance sheets analysis (same line items with % change)
- business_segments：PDF 94／紙本 62：Business Segment & Corporate Results (how the firm makes money: CCB, CIB, AWM, Corporate)
- segment_overview_front：PDF 54-70／紙本 52-67 (annual-report front section numbering)：Segment overviews in the front part of the annual report
- liquidity_deposits：PDF 135／紙本 103：Firmwide estimated uninsured deposits $1,558.6 billion at Dec 31, 2025
- deposit_ratios：PDF 136／紙本 104：Deposits as a % of total liabilities 63%; loans-to-deposits ratio 58% (the Firm's own table, uses gross loans $1,493.4bn)
- ratios_summary：PDF 76／紙本 44：Loans-to-deposits ratio 58 (2025), 56 (2024), 55 (2023)
- htm_unrealized：PDF 261／紙本 229：Note 10: total HTM securities amortized cost 270,134 / gross unrealized losses 17,053 / fair value 253,344; total investment securities gross unrealized losses 20,395

| 科目（原文） | 金額 |
|---|---:|
| Cash and due from banks | 21,742 |
| Deposits with banks | 321,596 |
| Federal funds sold and securities purchased under resale agreements | 336,426 |
| Securities borrowed | 286,191 |
| Trading assets | 802,873 |
| Available-for-sale securities | 507,198 |
| Held-to-maturity securities | 270,134 |
| Investment securities, net of allowance for credit losses | 777,332 |
| Loans | 1,493,429 |
| Allowance for loan losses | -25,765 |
| Loans, net of allowance for loan losses | 1,467,664 |
| Total assets | 4,424,900 |
| Deposits | 2,559,320 |
| Federal funds purchased and securities loaned or sold under repurchase agreements | 442,396 |
| Short-term borrowings | 64,776 |
| Trading liabilities | 216,019 |
| Long-term debt | 435,206 |
| Total liabilities | 4,062,462 |
| Total stockholders’ equity | 362,438 |

變體與對照：{"r3_gross_loans": 58.35, "r1_gross_loans": 33.75, "r2_including_trading_assets": 35.71, "htm_unrealized_loss_pct_of_equity": 4.7, "uninsured_deposits_pct_of_deposits": 60.9}

**壓力測試 A_deposit_run_10pct**：{"scenario": "deposits -10%", "deposit_outflow": 255932, "liquid_assets_before": 343338, "liquid_used": 255932, "shortfall_after_liquid": 0, "surplus_after_liquid": 87406, "securities_sold_book": 0, "loss_to_equity": 0, "after": {"assets": 4168968, "loans": 1467664, "securities": 777332, "deposits": 2303388, "liabilities": 3806530, "equity": 362438}, "ratios_after": {"r1": 35.2, "r2": 18.65, "r3": 63.72, "r4": 60.51, "r5": 8.69}}

**壓力測試 A2_deposit_run_10pct_fire_sale_10pct**：{"scenario": "deposits -10%, securities sold at 10% discount", "deposit_outflow": 255932, "liquid_assets_before": 343338, "liquid_used": 255932, "shortfall_after_liquid": 0, "surplus_after_liquid": 87406, "securities_sold_book": 0, "loss_to_equity": 0, "after": {"assets": 4168968, "loans": 1467664, "securities": 777332, "deposits": 2303388, "liabilities": 3806530, "equity": 362438}, "ratios_after": {"r1": 35.2, "r2": 18.65, "r3": 63.72, "r4": 60.51, "r5": 8.69}}

**壓力測試 B_rate_shock_5pct**：{"scenario": "bond prices -5%", "recognized_losses": {"Available-for-sale securities": 25360}, "recognized_total": 25360, "hidden_losses_not_on_balance_sheet": {"Held-to-maturity securities": 13507}, "hidden_total": 13507, "equity_after_recognized": 337078, "r5_after_recognized": 7.66, "equity_if_hidden_also_marked": 323571, "r5_if_hidden_also_marked": 7.38, "ratios_after_recognized": {"r1": 33.36, "r2": 17.09, "r3": 57.35, "r4": 63.0, "r5": 7.66}, "ratios_if_hidden_also_marked": {"r1": 33.46, "r2": 16.84, "r3": 57.35, "r4": 63.0, "r5": 7.38}}

## SVB：矽谷銀行（SVB Financial Group）（December 31, 2022（倒閉前最後一份年報；銀行於 2023-03-10 被接管）；US$ million）
來源：SVB Financial Group Form 10-K for fiscal year 2022, filed 2023-02-24 (accession 0000719739-23-000021)；頁碼 PDF None／紙本 95；交叉驗證：SEC EDGAR XBRL companyfacts, CIK 719739, FY2022 10-K: identical (Assets, AFS, HTM, NotesReceivableNet 73,614, Deposits, Liabilities, StockholdersEquity 16,004)

其他定位（頁碼都查過原檔）：
- uninsured：PDF —／紙本 80：“the amount of estimated uninsured deposits in U.S. offices that exceed the FDIC insurance limit were $151.5 billion” (Dec 31, 2022)
- htm_note：PDF —／紙本 125：Total HTM securities: amortized cost 91,327 / gross unrealized losses (15,160) / fair value 76,169 / allowance 6 / net carrying 91,321

| 科目（原文） | 金額 |
|---|---:|
| Cash and cash equivalents | 13,803 |
| Available-for-sale securities, at fair value (cost of $28,602) | 26,069 |
| Held-to-maturity securities, at amortized cost (fair value of $76,169) | 91,321 |
| Non-marketable and other equity securities | 2,664 |
| Total investment securities | 120,054 |
| Loans, amortized cost | 74,250 |
| Allowance for credit losses: loans | -636 |
| Net loans | 73,614 |
| Total assets | 211,793 |
| Noninterest-bearing demand deposits | 80,753 |
| Interest-bearing deposits | 92,356 |
| Total deposits | 173,109 |
| Short-term borrowings | 13,565 |
| Long-term debt | 5,370 |
| Total liabilities | 195,498 |
| Total SVBFG stockholders’ equity | 16,004 |
| Total equity (incl. noncontrolling interests) | 16,295 |

變體與對照：{"r3_gross_loans": 42.89, "r2_total_investment_securities": 56.68, "r5_total_equity": 7.69, "htm_fair_value_gap": 15152, "htm_gap_pct_of_equity": 94.7, "equity_if_htm_gap_recognized": 852, "r5_if_htm_gap_recognized": 0.43, "note_htm_gross_unrealized_losses_p125": 15160, "htm_unrealized_loss_pct_of_equity": 94.7, "uninsured_deposits_pct_of_deposits": 87.5, "noninterest_bearing_pct_of_deposits": 46.6}

**壓力測試 A_deposit_run_10pct**：{"scenario": "deposits -10%", "deposit_outflow": 17311, "liquid_assets_before": 13803, "liquid_used": 13803, "shortfall_after_liquid": 3508, "surplus_after_liquid": 0, "securities_sold_book": 3508, "loss_to_equity": 0, "after": {"assets": 194482, "loans": 73614, "securities": 113882, "deposits": 155798, "liabilities": 178187, "equity": 16004}, "ratios_after": {"r1": 37.85, "r2": 58.56, "r3": 47.25, "r4": 87.44, "r5": 8.23}}

**壓力測試 A2_deposit_run_10pct_fire_sale_10pct**：{"scenario": "deposits -10%, securities sold at 10% discount", "deposit_outflow": 17311, "liquid_assets_before": 13803, "liquid_used": 13803, "shortfall_after_liquid": 3508, "surplus_after_liquid": 0, "securities_sold_book": 3898, "loss_to_equity": 390, "after": {"assets": 194092, "loans": 73614, "securities": 113492, "deposits": 155798, "liabilities": 178187, "equity": 15614}, "ratios_after": {"r1": 37.93, "r2": 58.47, "r3": 47.25, "r4": 87.44, "r5": 8.04}}

**壓力測試 B_rate_shock_5pct**：{"scenario": "bond prices -5%", "recognized_losses": {"Available-for-sale securities, at fair value (cost of $28,602)": 1303}, "recognized_total": 1303, "hidden_losses_not_on_balance_sheet": {"Held-to-maturity securities, at amortized cost (fair value of $76,169)": 4566}, "hidden_total": 4566, "equity_after_recognized": 14701, "r5_after_recognized": 6.98, "equity_if_hidden_also_marked": 10135, "r5_if_hidden_also_marked": 4.92, "ratios_after_recognized": {"r1": 34.97, "r2": 55.15, "r3": 42.52, "r4": 88.55, "r5": 6.98}, "ratios_if_hidden_also_marked": {"r1": 35.75, "r2": 54.16, "r3": 42.52, "r4": 88.55, "r5": 4.92}}
