# Course folder (English session): give JPMorgan Chase a check-up with your AI agent

> Money and Banking, AI session 2. Website: https://cwstedctw.github.io/money-banking-ai-checkup/
> Open this folder with an AI agent (an AI that opens files, downloads and writes files by itself). Following `AGENTS.md`, it turns JPMorgan Chase's annual report into a check-up table with a page for every cell. **Checking is your job**: when it is done, you spot-check three cells and recompute the ratios yourself.

## 1. Download this folder

On the website press "Download the course folder (ZIP)", or open https://github.com/cwstedctw/money-banking-ai-checkup/archive/refs/heads/main.zip
Unzip it; the folder to open is `kit/en` inside (not the whole package).

## 2. Open `kit/en` with your agent

Use whichever you have:

| Agent | How to open this folder |
|---|---|
| Antigravity | File → Open Folder → choose `kit/en` |
| ChatGPT desktop (Codex) | New project → choose folder `kit/en` |
| Claude desktop | Code tab → Open folder → choose `kit/en` |

## 3. Paste this sentence

> Follow AGENTS.md in this folder and complete Task 1 in TASK.md.

If it asks "may I download / run a command?", check that it is the JPMorgan Chase URL in `data/README.md` before you allow it.

## 4. What you should see

1. It checks `data/` for the report; if missing, it downloads it from `data/README.md` and checks the sha256 (364 pages, so this takes a while).
2. It finds the Consolidated balance sheets on PDF page 199 (10-K printed page 167).
3. `output/checkup-table.md` appears: nine numbers, each with PDF page, printed page and the line name as printed, in US$ millions; the five ratios as formulas only.

If the download fails it will stop and tell you. Open the URL from `data/README.md` in a browser, save the PDF into `data/` under the name in the table, and tell it "continue".

## 5. Two things you do yourself afterwards

1. **Spot-check three cells**: open the PDF at the page it gave; check units, the year column (2025, not 2024), consolidated or not, and which page numbering it quoted.
2. **Recompute the ratios**: use a calculator or the check-up template from the website (`checkup-template.xlsx`), then ask it "what are your results?" and compare. Any mismatch is a clue.

Then paste "Now do Task 2 in TASK.md" for the stress test; Task 3 (two banks of your own) is homework.

## 6. No agent, or it will not open: the chat route

Use ChatGPT or Claude on the web: upload the JPMorgan Chase report (if 364 pages is too big, upload only PDF page 199) and paste the whole Task 1 box from `TASK.md`. Compute the ratios yourself.
