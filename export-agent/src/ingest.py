"""
ingest.py — Pipeline A: Document Ingestion
============================================
Reads PDF and Excel files from data/raw/, breaks them into knowledge-base chunks,
and saves the result as:
  - data/processed/knowledge_base.json  (machine-readable, used by build_index.py)
  - data/processed/knowledge_base.xlsx  (human-readable, for mentor review)
  - data/processed/source_mapping.xlsx  (one-page summary of all sources used)

Usage:
  python src/ingest.py

To just regenerate the Excel versions from the existing JSON (no new PDFs):
  python src/ingest.py --from-json
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import date
import pandas as pd

# ── Try to import PDF reading libraries ──────────────────────────────────────
try:
    import pdfplumber
    PDF_READER = "pdfplumber"
except ImportError:
    try:
        from pypdf import PdfReader
        PDF_READER = "pypdf"
    except ImportError:
        PDF_READER = None
        print("WARNING: Neither pdfplumber nor pypdf is installed. PDF reading disabled.")
        print("         Run: pip install pdfplumber")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
KB_JSON = PROCESSED_DIR / "knowledge_base.json"
KB_XLSX = PROCESSED_DIR / "knowledge_base.xlsx"
SOURCE_MAP_XLSX = PROCESSED_DIR / "source_mapping.xlsx"

# ── The 13 categories (from PRD.md) ──────────────────────────────────────────
CATEGORIES = [
    "How to Export from India",
    "Export Procedures & Documentation",
    "IEC, GST, AD Code, RCMC",
    "HS Code Guidance",
    "Incoterms",
    "Logistics & Customs",
    "Export Payment Methods",
    "Export Incentives & Govt Schemes",
    "Product Certifications & Compliance",
    "Country-Specific Import Requirements",
    "Trade Intelligence",
    "Trade Fairs & Export Promotion",
    "FAQs",
]

# ── Knowledge base JSON schema fields (from KNOWLEDGE_BASE.md) ───────────────
REQUIRED_FIELDS = [
    "id", "topic", "category", "question_it_answers",
    "answer", "source_name", "source_url", "source_type",
    "last_verified_date", "notes"
]


# ─────────────────────────────────────────────────────────────────────────────
# PDF READING
# ─────────────────────────────────────────────────────────────────────────────

def read_pdf_pdfplumber(pdf_path: Path) -> str:
    """Read all text from a PDF using pdfplumber."""
    import pdfplumber
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text.append(f"[Page {i+1}]\n{page_text}")
    return "\n\n".join(text)


def read_pdf_pypdf(pdf_path: Path) -> str:
    """Read all text from a PDF using pypdf (fallback)."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    text = []
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text.append(f"[Page {i+1}]\n{page_text}")
    return "\n\n".join(text)


def read_pdf(pdf_path: Path) -> str:
    """Read PDF content, trying pdfplumber first then pypdf."""
    if PDF_READER == "pdfplumber":
        return read_pdf_pdfplumber(pdf_path)
    elif PDF_READER == "pypdf":
        return read_pdf_pypdf(pdf_path)
    else:
        raise RuntimeError("No PDF reader available. Install pdfplumber: pip install pdfplumber")


# ─────────────────────────────────────────────────────────────────────────────
# EXCEL READING
# ─────────────────────────────────────────────────────────────────────────────

def read_excel(excel_path: Path) -> list[dict]:
    """
    Read an Excel file from data/raw/.
    If the Excel file already has the knowledge_base columns, import it directly.
    Otherwise, read each sheet as raw text for manual chunking.
    
    Returns a list of chunk dicts (may be partial — needs review).
    """
    xl = pd.ExcelFile(excel_path)
    chunks = []
    
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        
        # Check if this sheet already looks like a knowledge_base format
        if all(field in df.columns for field in ["topic", "answer", "source_name"]):
            print(f"  Sheet '{sheet_name}': detected knowledge_base format — importing directly.")
            for i, row in df.iterrows():
                chunk = {
                    "id": str(row.get("id", f"imported-{i:04d}")),
                    "topic": str(row.get("topic", "")),
                    "category": str(row.get("category", "FAQs")),
                    "question_it_answers": str(row.get("question_it_answers", "")),
                    "answer": str(row.get("answer", "")),
                    "source_name": str(row.get("source_name", excel_path.name)),
                    "source_url": str(row.get("source_url", "")),
                    "source_type": str(row.get("source_type", "your uploaded document")),
                    "last_verified_date": str(row.get("last_verified_date", date.today().isoformat())),
                    "notes": str(row.get("notes", "Imported from Excel"))
                }
                chunks.append(chunk)
        else:
            # Raw Excel data — convert to text representation for review
            print(f"  Sheet '{sheet_name}': raw format — creating placeholder chunk for review.")
            text_content = df.to_string(index=False)
            chunk = {
                "id": f"raw-excel-{excel_path.stem}-{sheet_name}".lower().replace(" ", "-"),
                "topic": f"Data from {excel_path.name} — {sheet_name}",
                "category": "FAQs",  # placeholder
                "question_it_answers": f"[REVIEW NEEDED] What information is in {excel_path.name} sheet '{sheet_name}'?",
                "answer": f"[REVIEW NEEDED — raw data below]\n\n{text_content[:2000]}",
                "source_name": f"{excel_path.name} — Sheet: {sheet_name}",
                "source_url": "",
                "source_type": "your uploaded document",
                "last_verified_date": date.today().isoformat(),
                "notes": "AUTO-IMPORTED: Needs human review and proper categorisation before this chunk is trusted."
            }
            chunks.append(chunk)
    
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# CHUNK FACTORY: for manually chunked PDF text
# ─────────────────────────────────────────────────────────────────────────────

def create_raw_pdf_chunk(pdf_path: Path, page_text: str, chunk_index: int) -> dict:
    """
    Create a placeholder knowledge base chunk from a raw PDF page.
    These chunks are marked 'REVIEW NEEDED' so the user knows to
    properly categorise and clean them.
    """
    return {
        "id": f"raw-pdf-{pdf_path.stem}-chunk{chunk_index:03d}".lower().replace(" ", "-"),
        "topic": f"Content from {pdf_path.name} (chunk {chunk_index})",
        "category": "FAQs",  # placeholder
        "question_it_answers": "[REVIEW NEEDED] What does this section cover?",
        "answer": f"[REVIEW NEEDED — raw text below]\n\n{page_text[:3000]}",
        "source_name": pdf_path.name,
        "source_url": "",
        "source_type": "your uploaded PDF",
        "last_verified_date": date.today().isoformat(),
        "notes": "AUTO-IMPORTED: Needs human review, proper topic/question/answer, and category assignment."
    }


def chunk_pdf_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list[str]:
    """
    Split a large text into overlapping chunks.
    Simple character-based chunking — sufficient for now.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_chunks(chunks: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Validate all chunks against the required schema.
    Returns (valid_chunks, list_of_warnings).
    """
    valid = []
    warnings = []
    
    for chunk in chunks:
        chunk_id = chunk.get("id", "UNKNOWN")
        
        # Check all required fields exist
        missing = [f for f in REQUIRED_FIELDS if f not in chunk or not str(chunk[f]).strip()]
        if missing:
            warnings.append(f"Chunk '{chunk_id}': missing or empty fields: {missing}")
        
        # Check category is valid
        if chunk.get("category") not in CATEGORIES:
            warnings.append(
                f"Chunk '{chunk_id}': category '{chunk.get('category')}' not in the 13 standard categories. "
                f"Valid: {CATEGORIES}"
            )
        
        # Check no [REVIEW NEEDED] chunks are being silently trusted
        if "[REVIEW NEEDED]" in str(chunk.get("answer", "")):
            warnings.append(
                f"Chunk '{chunk_id}': marked 'REVIEW NEEDED' — do not use in production until reviewed."
            )
        
        valid.append(chunk)  # include even if warnings — let human decide
    
    return valid, warnings


# ─────────────────────────────────────────────────────────────────────────────
# SAVE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def save_json(chunks: list[dict], path: Path):
    """Save knowledge base as JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(chunks)} chunks -> {path}")


def save_excel(chunks: list[dict], kb_path: Path, source_map_path: Path):
    """Save knowledge base as Excel (human-readable) and source mapping."""
    df = pd.DataFrame(chunks, columns=REQUIRED_FIELDS)
    df.to_excel(kb_path, index=False, sheet_name="Knowledge Base")
    print(f"  Saved Excel knowledge base -> {kb_path}")
    
    # Generate source mapping
    source_map = (
        df.groupby(["category", "source_name", "source_type"])
        .agg(fact_count=("id", "count"))
        .reset_index()
    )
    source_map.columns = ["Category", "Source Document/Website", "Source Type", "Number of Facts Extracted"]
    source_map["Reliability"] = source_map["Source Type"].map({
        "government website": "High - Official government source",
        "government portal": "High - Official government portal",
        "government regulation": "High - Official regulation",
        "government circular": "High - Official circular",
        "government policy": "High - Official policy",
        "government statistics": "High - Official statistics",
        "government regulator": "High - Regulatory body",
        "government body": "High - Government body",
        "government scheme": "High - Government scheme",
        "government trade body": "High - Government trade body",
        "export promotion body": "Medium-High - Officially recognised body",
        "international trade standard": "High - International standard",
        "international trade body": "Medium-High - International body",
        "foreign government authority": "Medium - Foreign govt source; verify for latest rules",
        "your uploaded document": "Review - Needs verification",
        "your uploaded PDF": "Review - Needs verification",
    }).fillna("Review - Verify reliability")
    
    source_map.to_excel(source_map_path, index=False, sheet_name="Source Mapping")
    print(f"  Saved source mapping -> {source_map_path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN INGESTION PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def load_existing_json() -> list[dict]:
    """Load the existing knowledge_base.json if it exists."""
    if KB_JSON.exists():
        with open(KB_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def ingest_raw_documents() -> list[dict]:
    """
    Read all PDFs and Excel files from data/raw/ and return new chunks.
    These are ADDED to the existing knowledge_base.json (not replacing it).
    """
    new_chunks = []
    files = list(RAW_DIR.iterdir())
    
    if not files or all(f.name == ".gitkeep" for f in files):
        print("  No documents found in data/raw/. Skipping ingestion from raw files.")
        return []
    
    for file_path in files:
        if file_path.name.startswith("."):
            continue
        
        suffix = file_path.suffix.lower()
        print(f"\n  Processing: {file_path.name}")
        
        if suffix == ".pdf":
            try:
                text = read_pdf(file_path)
                raw_chunks = chunk_pdf_text(text)
                for i, chunk_text in enumerate(raw_chunks):
                    new_chunks.append(create_raw_pdf_chunk(file_path, chunk_text, i + 1))
                print(f"    -> Created {len(raw_chunks)} chunks from PDF")
            except Exception as e:
                print(f"    ERROR reading PDF: {e}")
        
        elif suffix in (".xlsx", ".xls", ".csv"):
            try:
                if suffix == ".csv":
                    df = pd.read_csv(file_path)
                    # Treat as a single sheet
                    excel_chunks = []
                    if all(field in df.columns for field in ["topic", "answer", "source_name"]):
                        for i, row in df.iterrows():
                            excel_chunks.append({
                                "id": str(row.get("id", f"csv-{i:04d}")),
                                "topic": str(row.get("topic", "")),
                                "category": str(row.get("category", "FAQs")),
                                "question_it_answers": str(row.get("question_it_answers", "")),
                                "answer": str(row.get("answer", "")),
                                "source_name": str(row.get("source_name", file_path.name)),
                                "source_url": str(row.get("source_url", "")),
                                "source_type": str(row.get("source_type", "your uploaded document")),
                                "last_verified_date": str(row.get("last_verified_date", date.today().isoformat())),
                                "notes": str(row.get("notes", ""))
                            })
                    new_chunks.extend(excel_chunks)
                else:
                    excel_chunks = read_excel(file_path)
                    new_chunks.extend(excel_chunks)
                print(f"    -> Created {len(excel_chunks)} chunks from Excel/CSV")
            except Exception as e:
                print(f"    ERROR reading Excel/CSV: {e}")
        
        else:
            print(f"    Skipping unsupported file type: {suffix}")
    
    return new_chunks


def deduplicate(chunks: list[dict]) -> list[dict]:
    """Remove duplicate chunks by ID."""
    seen_ids = set()
    unique = []
    for chunk in chunks:
        chunk_id = chunk.get("id", "")
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            unique.append(chunk)
        else:
            print(f"  Duplicate ID skipped: {chunk_id}")
    return unique


def run_ingestion(from_json_only: bool = False):
    """Main ingestion pipeline."""
    print("\n" + "="*60)
    print("PIPELINE A: Knowledge Base Ingestion")
    print("="*60)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Load existing knowledge base
    existing = load_existing_json()
    print(f"\n[1/4] Loaded {len(existing)} existing chunks from knowledge_base.json")
    
    if from_json_only:
        print("      --from-json mode: skipping raw document ingestion")
        new_chunks = []
    else:
        # Step 2: Ingest new documents from data/raw/
        print(f"\n[2/4] Scanning {RAW_DIR} for new documents...")
        new_chunks = ingest_raw_documents()
        print(f"      Found {len(new_chunks)} new chunks from raw documents")
    
    # Step 3: Merge and deduplicate
    print("\n[3/4] Merging and deduplicating...")
    all_chunks = deduplicate(existing + new_chunks)
    print(f"      Total unique chunks: {len(all_chunks)}")
    
    # Validate
    all_chunks, warnings = validate_chunks(all_chunks)
    if warnings:
        print(f"\n  [WARN] {len(warnings)} validation warnings:")
        for w in warnings[:10]:  # show first 10
            print(f"     - {w}")
        if len(warnings) > 10:
            print(f"     ... and {len(warnings)-10} more")
    
    # Step 4: Save
    print("\n[4/4] Saving outputs...")
    save_json(all_chunks, KB_JSON)
    save_excel(all_chunks, KB_XLSX, SOURCE_MAP_XLSX)
    
    print("\n" + "="*60)
    print(f"[OK] Ingestion complete!")
    print(f"   {len(all_chunks)} chunks in knowledge base")
    print(f"   Next step: run  python src/build_index.py")
    print("="*60 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest PDF/Excel documents from data/raw/ into knowledge_base.json"
    )
    parser.add_argument(
        "--from-json",
        action="store_true",
        help="Skip raw document processing; just regenerate Excel from existing JSON"
    )
    args = parser.parse_args()
    run_ingestion(from_json_only=args.from_json)
