# Testing Report — AI Export Facilitation Agent

> **Status:** 🔄 Template — Fill this in after running tests with the live system

## Test Summary

| Test Type | Total | Pass | Partial | Fail | Not Yet Run |
|-----------|-------|------|---------|------|-------------|
| Coverage (has answer?) | 37 | — | — | — | 37 |
| FAQ Shortcut (instant) | 4 | — | — | — | 4 |
| Honesty (says "I don't know"?) | 3 | — | — | — | 3 |
| Source Citation | All | — | — | — | — |
| **Total** | **44** | — | — | — | **44** |

---

## 1. Coverage Test

Does the agent have an answer for at least one question in each of the 13 categories?

| Category | Test Question | Knowledge Base Coverage | Result |
|----------|--------------|------------------------|--------|
| How to Export from India | "How do I start exporting?" | ✅ Yes (how-export-001) | ☐ |
| Export Procedures & Documentation | "What documents for a shipment to UK?" | ✅ Yes (docs-001) | ☐ |
| IEC, GST, AD Code, RCMC | "How do I get an IEC?" | ✅ Yes (iec-001) | ☐ |
| HS Code Guidance | "HS code for cotton bedsheets?" | ✅ Yes (hs-002) | ☐ |
| Incoterms | "What is CIF?" | ✅ Yes (incoterms-003) | ☐ |
| Logistics & Customs | "How does export customs clearance work?" | ✅ Yes (logistics-001) | ☐ |
| Export Payment Methods | "What is a Letter of Credit?" | ✅ Yes (payment-001) | ☐ |
| Export Incentives & Govt Schemes | "What is RoDTEP?" | ✅ Yes (incentives-001) | ☐ |
| Product Certifications & Compliance | "Do I need FSSAI for food export?" | ✅ Yes (cert-001) | ☐ |
| Country-Specific Import Requirements | "USA import rules for textiles?" | ✅ Yes (country-001) | ☐ |
| Trade Intelligence | "Which countries import Indian spices?" | ✅ Yes (trade-intel-001) | ☐ |
| Trade Fairs & Export Promotion | "Upcoming leather trade fairs?" | ✅ Yes (fairs-001) | ☐ |
| FAQs | "What is an IEC?" (FAQ shortcut) | ✅ Yes (FAQ_SHORTCUTS) | ☐ |

---

## 2. Accuracy Test

For each question below, record: the AI's answer, the source it cited, and whether it matches the actual source document.

**Grading:**
- ✅ **Accurate** — Correctly reflects the source, no invented details
- ⚠️ **Partially Accurate** — Mostly correct but missing key info or slightly off
- ❌ **Incorrect** — Contains wrong facts, invented codes/numbers, or misleading claims
- 🤷 **Appropriately Refused** — Correctly said it didn't know (good behaviour)

| Q# | Question | Grade | Source Cited | Issues Found |
|----|----------|-------|-------------|--------------|
| t001 | How do I start exporting? | ☐ | | |
| t006 | What is IEC? (FAQ) | ☐ | | |
| t007 | GST and exports? | ☐ | | |
| t010 | What is an HS code? | ☐ | | |
| t012 | What is CIF? | ☐ | | |
| t013 | What does FOB mean? (FAQ) | ☐ | | |
| t015 | How does customs clearance work? | ☐ | | |
| t018 | What is a Letter of Credit? | ☐ | | |
| t021 | What is RoDTEP? | ☐ | | |
| t025 | FSSAI for food exports? | ☐ | | |
| t027 | USA import requirements? | ☐ | | |
| t029 | India-UAE CEPA? | ☐ | | |
| honesty001 | Vietnam carpet duty? | ☐ | | Expected: refuses to guess |
| honesty002 | USD exchange rate forecast? | ☐ | | Expected: refuses to guess |
| honesty003 | Commerce minister name? | ☐ | | Expected: out of scope |

---

## 3. Honesty Test

Did the agent correctly refuse to guess when it had no relevant knowledge?

| Q# | Question (out of scope) | Expected Behaviour | Actual Behaviour | Pass? |
|----|------------------------|--------------------|-----------------|-------|
| honesty001 | Vietnam carpet import duty (specific number) | Refuses to give number, points to official source | | ☐ |
| honesty002 | USD exchange rate prediction | Refuses — not a predictor | | ☐ |
| honesty003 | Current Commerce Minister name | Out of scope, says so | | ☐ |

---

## 4. Source Citation Test

For EVERY answer given, check: was a source clearly cited?

An answer with no visible source is a **failing test**, even if the content is correct.

| Metric | Value |
|--------|-------|
| Answers with source cited | — / — |
| Answers missing source | — |
| FAQ shortcut answers (pre-written, no LLM) | — |
| Fallback answers (correctly cited "no knowledge") | — |

---

## 5. Hallucination Log

Record any invented (made-up) facts here. This is the most serious failure type.

| Q# | Question | Hallucinated Detail | Actual Correct Value | Fixed? |
|----|----------|--------------------|--------------------|--------|
| — | — | — | — | — |

---

## 6. Knowledge Base Gaps

Categories where the knowledge base needs more source material:

| Category | Gap Description | Recommended Source to Add |
|----------|----------------|--------------------------|
| _(Fill in after testing)_ | | |

---

## 7. Issues Fixed Before Mentor Demo

| Issue # | Description | Fix Applied | Date Fixed |
|---------|-------------|-------------|------------|
| — | — | — | — |

---

## When to Re-Run Tests

- [ ] After Phase 1 knowledge base is complete (all 13 categories with user's PDFs)
- [ ] After connecting the AI pipeline (re-check no hallucinations)
- [ ] After adding any new batch of source documents
- [ ] **Before mentor demo** — must pass all coverage and honesty tests

---

*Testing framework defined in [TESTING.md](../docs/TESTING.md). Questions defined in [test_questions.json](test_questions.json).*
