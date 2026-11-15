# 英文場 agent 示範（11/18 週三，投影片 p11 起跑、p14 回頭看）

> 給 Ted（說明用中文；給 agent 的 `AGENTS.md`、`TASK.md` 是英文，投影時學生看得懂）。原則照 9 月：**p11 按下去就切回投影片，p14 才回頭看；跑不完開彩排成品，不在台上乾等。**
> 這夾的 `data/` 與成品夾不進 git（PDF 從 `../../data/` 複製；要重做照 `../../data/README.md` 重抓、對 sha256）。

## 這夾有什麼

| 檔 | 是什麼 |
|---|---|
| `AGENTS.md` | 給 agent 的規則（英文）：只用 `data/`、每個數字附 PDF 頁＋紙本頁碼（**說明是哪一套頁碼**）＋原文科目、算式列出、做完用 SEC EDGAR XBRL companyfacts 核對、沒把握要標、成品寫到 `output/` |
| `TASK.md` | 第一行＝要貼的那一句；底下＝Prompt ③ 全文（跟投影片一字不差）＋三件加碼 |
| `data/` | JPMorgan Chase 2025 年報（364 頁，含 10-K）、矽谷銀行摘錄 |
| `output/` | 上課當下 agent 寫進來（空的） |
| `成品-彩排/` | 彩排那次的成品，台上的備援（**還是空的，要彩排才有**） |

## 彩排（11/17 晚上或 11/18 早上）

1. Claude 桌面版 → **Code** 分頁 → 選這一夾（`demo/agent-en`；建議複製到桌面）。
2. 打開 `TASK.md`，複製**第一行**，貼進去，送出。
3. 看它跑、**計時**：364 頁它會不會整本讀很久；找不找得到 PDF 第 199 頁（10-K 紙本 167）；有沒有分清兩套頁碼。
4. 跑完：`output/` 整夾複製到 `成品-彩排/`，再清空 `output/`。
5. 拿 `checkup-table.md` 對 `../../numbers.json` 的 `banks.JPM.lines`，找出它錯的那一格。

## 上課（p11，約第 17 分鐘）

1. 切到 Claude 桌面版（已開好這夾、新的對話）。
2. 貼 `TASK.md` 第一行 → 送出 → "It will open the report, copy the table, compute, draw a chart, write a memo, then check itself against SEC data. We won't wait." → **切回投影片**。
3. p14（約第 32 分鐘）切回來：做完 → 開 `output/checkup-table.md` 與 `ratios-chart.png`；還沒 → 開 `成品-彩排/`。

## 看它的五個點（p14）

- 頁碼：說 PDF 199 還是 167？有沒有講哪一套。
- 放款用淨額 1,467,664（存放比 57.35%）還是總額 1,493,429（58.35%，公司自己報 58%）。
- Trading assets 802,873 算不算證券：它的理由是什麼（算進去 35.71%，不算 17.57%）。
- 有沒有抄到 2024 欄（2024 資產 4,002,814）。
- 第二來源：真的連上 EDGAR 了嗎？

## 翻車

| 狀況 | 做法 |
|---|---|
| 桌面版登不進去／網路擋 | 開 `成品-彩排/` |
| 364 頁讀太久（超過 3 分鐘還沒出表） | 不等；p14 開彩排成品。這本身就是教學點：整本丟進去會慢 |
| EDGAR 擋自動程式 | 它寫「沒查到」＝誠實，可以講 |
| 它做得完美 | "Today it behaved. What about your chat AI?" → 對學生的表 |
