# TESTING.md — How We Check the Agent is Actually Correct

## Why testing matters more here than in a normal app
A wrong feature bug is annoying. A wrong export rule can cost someone real money (a delayed shipment, a rejected customs form, a missed incentive deadline). So testing here isn't just "does the button work" — it's "is this piece of advice actually true."

## What gets tested

### 1. Coverage test
Does the agent have an answer (from the knowledge base) for at least one question in each of the 13 Phase 1 categories? Simple checklist:

| Category | Test question | Has knowledge base coverage? |
|---|---|---|
| How to export from India | "How do I start exporting?" | ☐ |
| Procedures & documentation | "What documents for a shipment to UK?" | ☐ |
| IEC/GST/AD Code/RCMC | "How do I get an IEC?" | ☐ |
| HS Code | "HS code for cotton shirts?" | ☐ |
| Incoterms | "What is CIF?" | ☐ |
| Logistics & Customs | "How does export customs clearance work?" | ☐ |
| Payment methods | "What is a Letter of Credit?" | ☐ |
| Incentives/schemes | "What is RoDTEP?" | ☐ |
| Certifications | "Do I need FSSAI for food export?" | ☐ |
| Country import requirements | "USA import rules for textiles?" | ☐ |
| Trade intelligence | "Which countries import Indian spices?" | ☐ |
| Trade fairs | "Upcoming leather trade fairs?" | ☐ |
| FAQs | "What is an IEC?" (FAQ shortcut) | ☐ |

### 2. Accuracy test
For a set of ~30–50 real questions (a mix across all categories):
1. Ask the agent the question
2. Compare its answer + cited source against the actual source document
3. Grade it: **Accurate / Partially Accurate / Incorrect / Appropriately Refused**
4. Log any hallucination (made-up fact) — this is the most serious failure type and should be fixed before moving forward

### 3. Honesty test (does it say "I don't know" when it should?)
Deliberately ask questions that are **not** in the knowledge base yet (e.g. a very obscure or made-up scenario), and confirm the agent refuses to guess and instead points to an official source. This is just as important as getting real questions right.

### 4. Source citation test
For every answer given, check: does it clearly state which document/source it used? An answer with no visible source should be treated as a failing test, even if the content happens to be correct.

## The Testing Report (deliverable)
A simple markdown or Excel file, filled in after running the above tests, containing:
- Total questions tested
- Pass/fail counts for accuracy, honesty, and citation
- A table of every failed/partial case, what went wrong, and what was fixed
- Any category with weak knowledge-base coverage, flagged for more source material

## When to test
- After the first version of the knowledge base is built (before connecting the AI) — check the raw facts are correctly extracted
- After the AI pipeline is connected — check the AI is using facts correctly and not adding its own guesses
- After any new batch of documents is added to the knowledge base
- Before showing the prototype to your mentor
