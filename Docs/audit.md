# RupeeRadar Comprehensive System Audit

This document compiles the frontend (UI/UX) and backend issues identified in the RupeeRadar application.

---

## 🎨 Frontend UI & UX Issues

### Issue 1: State Loss on Page Refresh
* **Category:** UX / Architecture
* **Impact / Priority:** P0 Critical
* **Description:** The dashboard state is passed solely via React Router state (`location.state.result`). Reloading the page or navigating back/forward wipes this state, causing the app to redirect back to the home page with a "No analysis yet" empty state message.
* **Why It Matters:** Users expect to refresh their browsers or bookmark the dashboard without losing their parsed transaction history.
* **Fix Recommendation:** Store the active `job_id` or the analysis results in `localStorage` / `sessionStorage`. On page load, retrieve and rehydrate from `localStorage` or fetch from the backend via the `GET /api/v1/analyze/{job_id}` endpoint.

### Issue 2: Tailwind Color Theme Variables Missing
* **Category:** UI / Bug
* **Impact / Priority:** P0 Critical
* **Description:** TSX components use Tailwind classes like `text-on-surface` and `text-on-surface-variant`. However, these keys are not defined under `@theme` in `index.css`. Only `--color-surface-foreground` and `--color-surface-foreground-variant` are defined.
* **Why It Matters:** Tailwind fails to map `text-on-surface` to any style, leaving important dashboard description text uncolored or defaulting to body text colors with poor contrast, causing a major accessibility regression.
* **Fix Recommendation:** Define the missing color mappings under `@theme` in `index.css`:
  ```css
  --color-on-surface: var(--color-surface-foreground);
  --color-on-surface-variant: var(--color-surface-foreground-variant);
  ```

### Issue 3: No Quick Demo/Sample Data Load Option
* **Category:** UX / QA
* **Impact / Priority:** P1 Important
* **Description:** There is no way to preview the dashboard without uploading a bank statement. In automated testing and local developer runs, users are blocked or face high friction.
* **Why It Matters:** Investors and users want to see the dashboard immediately without downloading sample CSV files and uploading them. In headless browser sandboxes, file uploads are restricted, making automated QA testing difficult.
* **Fix Recommendation:** Add a "Load Demo Data" button on the `UploadPage`. Import the `sample_analysis_output.json` content statically and load it directly into state to navigate to the dashboard.

### Issue 4: Navigation Hierarchy & Nesting Discord
* **Category:** UI / UX
* **Impact / Priority:** P1 Important
* **Description:** The left sidebar remains static and underutilized. Main features like the "Ledger", "Recurring", "Portfolio Audit", and "Report" are hidden behind secondary horizontal tabs inside the dashboard screen.
* **Why It Matters:** Double-nested layouts increase cognitive load and make navigation confusing. Primary sections should live in the global sidebar navigation.
* **Fix Recommendation:** Move "Ledger", "Recurring", "Portfolio Audit", and "Report" to the sidebar. Dynamically reveal or enable them only after data is loaded. Disable or lock them when no statement is analyzed.

### Issue 5: Recharts Flexible Container Width/Height Warning
* **Category:** UI / Bug
* **Impact / Priority:** P1 Important
* **Description:** The console logs `The width(-1) and height(-1) of chart should be greater than 0...` when rendering Recharts charts.
* **Why It Matters:** `ResponsiveContainer` fails to calculate container size when nested inside flex containers or tabs during mount, causing layout shift or empty charts.
* **Fix Recommendation:** Provide explicit `min-h-[350px]` wrappers around the Recharts charts, and ensure they only render when parent dimensions are set.

---

## ⚙️ Backend Architecture & Algorithmic Issues

### Issue 6: Silent Bug in MoM Category Spike Analysis
* **Category:** Bug / Logic
* **Impact / Priority:** P0 Critical
* **Description:** In `backend/app/pipeline/insights.py` under the `_category_spend_by_month` function (lines 224-235), the code iterates over transactions and resolves `cat`, but **fails to write the amount to the totals dictionary**. The line `totals[cat] += txn.amount` is completely missing.
* **Why It Matters:** The function always returns an empty dictionary `{}`. As a result, the Month-over-Month category spike detector never registers any category changes, and falls back to a generic spend insight. It is a silent bug that disables a key analytical feature.
* **Fix Recommendation:** Add the missing dictionary update in `_category_spend_by_month`:
  ```python
  cat = txn.category.value if txn.category else Category.OTHER.value
  totals[cat] += txn.amount
  ```

### Issue 7: High Risk of Recurring Payment False Positives
* **Category:** Bug / Algorithm
* **Impact / Priority:** P1 Important
* **Description:** In `backend/app/pipeline/recurrence.py` under `_group_key`, if a transaction has no merchant extracted, it is grouped **solely by its rounded amount** (e.g. `amount:500` for ₹450-₹550).
* **Why It Matters:** If a user makes unrelated debit card purchases of similar amounts (e.g. ₹510 at a cafe and ₹490 for groceries) on a roughly monthly interval, the algorithm will group them together and flag them as a single recurring payment.
* **Fix Recommendation:** When grouping transactions, incorporate description similarity (e.g. checking token overlaps or sharing similar clean description prefixes) rather than grouping solely by rounded amounts.

### Issue 8: Strict/Fragile Frequency Logic
* **Category:** Algorithm
* **Impact / Priority:** P2 Nice to Have
* **Description:** The range for monthly recurrence is strictly `(27, 35)` days.
* **Why It Matters:** Monthly transactions delayed by weekends, holidays, or month-length changes (such as in February) can easily fall to 26 days or rise to 36-37 days, causing them to be ignored by the recurrence engine.
* **Fix Recommendation:** Expand the monthly interval range to `(25, 37)` or `(25, 40)`.

### Issue 9: Configuration Crash on Database Import
* **Category:** Bug / Architecture
* **Impact / Priority:** P1 Important
* **Description:** `backend/app/database.py` tries to reference `settings.database_url`. However, `database_url` is not declared on the `Settings` class in `settings.py`, and is missing from `.env.example`.
* **Why It Matters:** Any attempt to import `database.py` or use the transaction routes in `transactions.py` immediately crashes with an `AttributeError`. It went unnoticed because `transactions.py` routes are currently commented out / not registered in `main.py`.
* **Fix Recommendation:** Add a `database_url` configuration field to the Pydantic `Settings` model in `settings.py` (defaulting to a local SQLite database string `sqlite:///./rupeeradar.db`) so that imports do not crash.
