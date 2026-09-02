# KNOWLEDGE_BASE.md — Turning Your PDFs/Excel into AI-Ready Facts

## Why this matters most
This is the actual "brain content" of the agent. The mentor asked for an "AI-ready knowledge base (Excel/JSON)" as a deliverable — this file explains exactly what that means and what shape it should be in.

## The one rule for every entry
Every single fact the agent can say must be traceable to a real source. No fact goes in without a source. If you're not sure where a fact came from, don't include it — flag it for follow-up instead.

## The format (one entry = one fact/topic chunk)

Each chunk in `knowledge_base.json` looks like this:

```json
{
  "id": "iec-001",
  "topic": "IEC Registration",
  "category": "IEC, GST, AD Code, RCMC",
  "question_it_answers": "What is an IEC and how do I get one?",
  "answer": "An Importer-Exporter Code (IEC) is a 10-digit number issued by DGFT, required for anyone exporting or importing from India. You can apply online via the DGFT website with PAN, business proof, and a bank certificate/cancelled cheque. There is no renewal needed, but the IEC must be confirmed annually online (a simple free step) or it gets deactivated.",
  "source_name": "DGFT Official Website — IEC Guidelines",
  "source_url": "https://www.dgft.gov.in/...",
  "source_type": "government website",
  "last_verified_date": "2026-08-30",
  "notes": "Confirm the annual update rule is still current before relying on it"
}
```

### Field-by-field, in plain words
| Field | What it means |
|---|---|
| `id` | A short unique code so we can reference this fact elsewhere (e.g. in testing) |
| `topic` | Short name of what this chunk covers |
| `category` | Which of the 13 Phase 1 topics this belongs to (see PRD.md table) |
| `question_it_answers` | A real question a user might type — helps the search find it and helps testing |
| `answer` | The actual explained fact, written clearly, no jargon left unexplained |
| `source_name` | Which document/website this came from |
| `source_url` | Link, if it's a webpage (leave blank if it's from your uploaded PDF) |
| `source_type` | e.g. "government website", "your uploaded PDF", "official circular" |
| `last_verified_date` | When this fact was last checked to be accurate — important because rules change |
| `notes` | Anything uncertain or that needs a human to double check |

## The Excel version (mirror of the JSON, for humans)
Same fields as columns in a spreadsheet — this is the version your mentor or a non-technical reviewer can open and read directly, without needing to understand JSON. It should always be kept in sync with the JSON (the `ingest.py` script should generate both from the same source data, not maintained as two separate manual files).

## How your existing PDFs/knowledge files get turned into this
1. Each PDF/document gets read and broken into logical chunks — usually one chunk per distinct fact, procedure, or rule (not the whole document as one giant blob — that makes search worse).
2. Every chunk gets tagged with which of the 13 categories it belongs to.
3. Every chunk gets a `source_name` pointing back to the exact original document (and page number if possible, in `notes`).
4. If a document mentions a number, deadline, fee, or rule that changes over time, mark it clearly so it's easy to find and refresh later.

## Source mapping document (a separate deliverable)
Alongside `knowledge_base.json`, keep a `source_mapping.xlsx` — a simple table:

| Category | Source Document/Website | Number of Facts Extracted | Reliability |
|---|---|---|---|
| IEC/GST/AD Code/RCMC | (your PDF name) | 12 | Official government doc |
| HS Code Guidance | ICEGATE / your PDF | 8 | Official |
| ... | ... | ... | ... |

This gives anyone reviewing the project (like your mentor) a one-page view of *where the AI's knowledge actually comes from*, which is the trust foundation of the whole tool.

## Next step for you
When you're ready, share your knowledge PDFs/Excel files and I'll help design the `ingest.py` logic (or process a sample file directly) so the extraction matches this exact format.
