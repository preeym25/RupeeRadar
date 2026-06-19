# RupeeRadar — Project Context

## Overview

**RupeeRadar** is an AI-powered personal finance assistant built for the AI Challenge. It helps working professionals understand where their money goes by analyzing bank statement data and turning messy, inconsistent transaction records into clear spending insights.

Working professionals often make hundreds of monthly transactions across UPI, cards, bank transfers, subscriptions, EMIs, rent, shopping, food delivery, travel, and investments. Bank statements contain all of this information, but transaction descriptions are messy, inconsistent, and hard to categorize manually. RupeeRadar automates that work end-to-end.

## Objective

Convert raw financial transaction data into meaningful personal finance insights through a working, end-to-end prototype.

The application should help users answer:

- What are my biggest spending categories?
- How much did I spend this month?
- Which transactions are recurring subscriptions or EMIs?
- What was my biggest transaction?
- What are the top insights from my spending behavior?

## Core Workflow

```
Upload bank statement → Extract & clean transactions → Categorize expenses
→ Detect recurring payments → Compute metrics → Generate insights → Dashboard / report
```

## Functional Requirements

### 1. Input

- Accept bank statement data as input (format TBD; prioritize a working prototype over universal bank support).

### 2. Transaction extraction & cleaning

- Parse raw statement data into a structured transaction format.
- Normalize messy, inconsistent transaction descriptions.
- Handle real-world, noisy descriptions robustly.

### 3. Categorization

Assign each transaction to a meaningful category. Target categories include:

| Category       | Examples                                      |
|----------------|-----------------------------------------------|
| Food           | Swiggy, Zomato, restaurants                   |
| Travel         | Flights, cabs, fuel, hotels                   |
| Shopping       | Amazon, Flipkart, retail                      |
| Bills          | Utilities, mobile, internet                   |
| EMI            | Loan repayments                               |
| Subscriptions  | Netflix, Spotify, SaaS                        |
| Salary         | Income credits                                |
| Rent           | Monthly rent payments                         |
| Investments    | SIPs, mutual funds, stocks                    |
| Other          | Uncategorized or ambiguous transactions       |

### 4. Recurring payment detection

Identify patterns for:

- Subscriptions
- EMIs
- Rent
- SIPs
- Insurance payments

### 5. Financial metrics

Calculate at minimum:

- Total income
- Total spend
- Savings (income − spend)
- Top spending categories
- Biggest transactions

### 6. AI-generated insights

- Produce at least **three personalized, human-readable insights** grounded in actual transaction amounts.
- Insights should be clear, actionable, and specific to the user's data.

### 7. Output & presentation

Deliver results via:

- A simple dashboard or UI
- A downloadable or shareable report / visual summary

## Expected Deliverables (Prototype Demo)

The working prototype must demonstrate:

- [ ] Cleaned transaction data
- [ ] Categorized expenses
- [ ] Recurring payment detection
- [ ] Spend summary dashboard
- [ ] At least three personalized financial insights
- [ ] A final report or visual summary that can be shared

**Final deliverable:** A deployed or locally runnable application that takes raw bank statement data and produces a clear personal finance summary.

## Evaluation Criteria

Submissions are judged on:

1. **Accuracy** — Transaction cleaning and categorization quality
2. **Insight quality** — Usefulness and clarity of generated financial insights
3. **Robustness** — Handling real-world messy transaction descriptions
4. **UX** — Simplicity and usefulness of the user experience
5. **Completeness** — End-to-end workflow from upload to report
6. **Privacy** — Conscious handling of sensitive financial data

## Constraints & Priorities

- **Working end-to-end prototype** takes priority over perfect support for every bank format.
- Technology stack and implementation approach are **open choice**.
- Privacy-conscious design is expected when handling bank statements and transaction data.

## Non-Functional Considerations

### Privacy & security

- Bank statements contain highly sensitive PII and financial data.
- Minimize data retention; avoid sending raw statements to third parties unless explicitly disclosed.
- Prefer local or ephemeral processing where feasible.
- Do not log or persist full statement contents unnecessarily.

### Data model (suggested)

Each cleaned transaction should ideally include:

```text
id, date, description (raw), description (cleaned), amount, type (debit/credit),
category, is_recurring, merchant (optional), account (optional)
```

### Suggested system components

| Component              | Responsibility                                      |
|------------------------|-----------------------------------------------------|
| Ingestion / parser     | Read uploaded statements (CSV, PDF, Excel, etc.)    |
| Cleaner                | Normalize descriptions, dedupe, fix amounts/dates   |
| Categorizer            | Rule-based, ML, or LLM-assisted category assignment |
| Recurrence detector    | Find repeating amounts, merchants, or intervals   |
| Analytics engine       | Aggregate metrics, top categories, trends           |
| Insight generator      | LLM or template-based narrative insights            |
| UI / dashboard         | Upload, review, visualize, export report            |

## Out of Scope (for initial prototype)

- Full multi-bank format support
- Real-time transaction sync with banks
- Tax filing or investment advice
- Multi-user accounts or authentication (unless needed for demo)

## Success Definition

RupeeRadar succeeds when a user can upload a bank statement, review categorized and cleaned transactions, see recurring payments flagged, read at least three personalized spending insights, and share or download a clear summary of where their money went — all without manually parsing messy transaction descriptions.
