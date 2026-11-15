# Rules for this folder (for the AI agent)

The person using you is a university student in a Money and Banking class, reading a bank's annual report with an agent for the first time. Afterwards they will pick three cells, check them against the PDF, and recompute the ratios with a calculator, so every number you give must be easy to trace back.

Talk to the user in English.

## Where the data comes from

- Use only the reports in `data/`. Reason: the class is practising "every number points back to the original"; numbers from memory or other websites cannot be checked by the student.
- If a PDF is not in `data/` yet, download it from the official URL in `data/README.md` into `data/` and compare its sha256 with the table. Downloading, computing the sha256 and saving into `data/` need no confirmation; just do them.
- If the sha256 does not match, the download fails, or the URL does not open: stop, tell the user which file and what error you saw, and ask them to download it with a browser from the same URL into `data/` and tell you to continue. Do not switch to a copy from another website; its pages and numbers may differ.
- Task 3 uses banks the student chooses, so there is no sha256 for them: use the files the user puts in `data/` or the official URLs they give, and record the URL and download date in the output.

## Every number must carry

- File name, **PDF page** (physical page counting from 1), the page number printed on that page, and **the line name exactly as printed**.
- The JPMorgan Chase report has **two printed page numberings** (the annual-report front section and the Form 10-K section): say which one you are quoting.
- Units as printed (US$ millions), which column (December 31, 2025, not 2024), and whether the statement is consolidated. Reason: wrong column, wrong units and wrong page numbering are the most common errors in this exercise.

## Label every sentence

After each sentence, add one label:

- **(statement)**: taken directly from the report, with a page you can cite.
- **(calculated)**: computed from statement numbers; show the formula.
- **(inference)**: not in the report; your own judgement or assumption (for example "the bank would sell securities first", "why depositors withdraw").

Reason: the class is learning to tell sourced sentences from AI inferences; your labels give the student something to check.

## Ratios

- For each ratio write numerator = which cell, denominator = which cell.
- When the task says "I will compute the ratios myself", give only the formulas, not the results; when the user comes back after computing, give your results (%, two decimals) for comparison. Reason: the student works it out first, and any mismatch is a clue.

## Say "not found" when it is not there

- If a number the task asks for is not in the files in `data/`, write "not found" in that cell and tell the user which pages you checked. Do not fill it from another source and do not guess.
- If the task is ambiguous (for example, which column to use), stop and ask one question, then continue.

## Output

- Task 1 goes to `output/checkup-table.md`, Task 2 to `output/stress-test.md`, Task 3 to `output/homework-two-banks.md`; the teacher-demo file names are in `TASK-teacher-demo.md`.
- You may install Python packages needed to read PDFs (for example pymupdf, pypdf) with `pip install --user` without asking; do not install anything that needs administrator rights, tell the user instead.
- Do not change files outside `data/` and `output/`, and do not upload any file anywhere. Reason: this is the student's own computer; anything outside this folder is not part of the exercise.
- The JPMorgan Chase report has 364 pages. Search it for the balance sheet instead of reading it all at once.

## Personal data

This folder holds only public bank reports. If the user pastes a classmate's name, student ID or grades, remind them to delete it and do not write it into any file.
