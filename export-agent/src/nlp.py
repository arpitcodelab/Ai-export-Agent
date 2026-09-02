"""
nlp.py — Natural Language Processing helpers
==============================================
Improves the agent's understanding of user questions before retrieval.

Features:
  1. Query normalisation — expand abbreviations, fix typos, strip noise,
     so the retriever matches better.
  2. Intent detection — classify the user's question into a broad intent
     (documents, registration, payment, country, incentives, logistics, etc.)
     so the agent can route or respond appropriately.
  3. Question cleaning — remove filler words and normalize whitespace.

All rules are deterministic and lightweight (no heavy NLP models needed),
keeping the app fast and offline-friendly.
"""

from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Abbreviation / jargon expansion map
# Expands common export abbreviations to their full form so embedding
# retrieval matches the knowledge base better.
# ─────────────────────────────────────────────────────────────────────────────

ABBREVIATIONS = {
    "iec": "import export code",
    "gstin": "gst identification number",
    "ad code": "authorized dealer code",
    "rcmc": "registration cum membership certificate",
    "rodtp": "remission of duties and taxes on exported products",
    "fob": "free on board",
    "cif": "cost insurance and freight",
    "cfr": "cost and freight",
    "cpt": "carriage paid to",
    "fca": "free carrier",
    "ddu": "delivered duty unpaid",
    "ddp": "delivered duty paid",
    "lc": "letter of credit",
    "tt": "telegraphic transfer",
    "gd": "goods declaration",
    "sb": "shipping bill",
    "boe": "bill of entry",
    "epa": "economic partnership agreement",
    "pta": "preferential trade agreement",
    "fta": "free trade agreement",
    "cepa": "comprehensive economic partnership agreement",
    "hs": "harmonized system",
    "apeda": "agricultural and processed food products export development authority",
    "mpeda": "marine products export development authority",
    "epc": "export promotion council",
    "amo": "adopted merchanting arrangement",
    "rrl": "rupee realisation limit",
    "eepp": "export of services",
}

# Multi-word terms must be matched before single tokens to avoid partial matches
_MULTIWORD = sorted(
    [k for k in ABBREVIATIONS if " " in k],
    key=len,
    reverse=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# Filler / stop words to strip from the start/end of a question
# ─────────────────────────────────────────────────────────────────────────────

FILLERS = {
    "hello", "hi", "hey", "please", "can", "could", "would", "you", "i",
    "do", "does", "is", "are", "tell", "me", "about", "regarding", "what",
    "how", "why", "when", "where", "who", "okay", "ok", "thanks", "thank",
    "xa", "ask", "wanted", "need", "want", "know", "like", "the", "a", "an",
}

# Simple regex-free word stems for rudimentary plural/tense normalisation
_WORD_LOWERCASE = str.lower


# ─────────────────────────────────────────────────────────────────────────────
# 1. Query normalisation
# ─────────────────────────────────────────────────────────────────────────────

def expand_abbreviations(text: str) -> str:
    """
    Expand known export abbreviations to their full form.
    E.g. "How to get my IEC?" -> "How to get my import export code?"
    This boosts embedding similarity with the knowledge base.
    """
    import re

    working = f" {text.lower().strip()} "

    # Multi-word abbreviations first (e.g. "ad code")
    for abbr in _MULTIWORD:
        working = re.sub(rf"\b{re.escape(abbr)}\b", ABBREVIATIONS[abbr], working)

    # Single-word abbreviations (word-boundary, case handled by lowercase above)
    for abbr in ABBREVIATIONS:
        if " " in abbr:
            continue
        working = re.sub(rf"\b{re.escape(abbr)}\b", ABBREVIATIONS[abbr], working)

    return re.sub(r"\s+", " ", working).strip()


def clean_question(text: str) -> str:
    """
    Clean up a question: collapse whitespace, remove leading/trailing filler.
    """
    import re

    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()
    # Strip leading fillers but keep a core verb/noun so we don't lose meaning
    while words and _WORD_LOWERCASE(words[0]).strip("?.,!") in FILLERS and len(words) > 3:
        words.pop(0)

    cleaned = " ".join(words)
    if not cleaned:
        return text

    # Fix spacing before punctuation
    cleaned = re.sub(r"\s+([?.!,;:])", r"\1", cleaned)
    return cleaned


def normalize_query(question: str) -> str:
    """
    Full normalisation pipeline: clean -> expand abbreviations.
    Returns a better embedding query.
    """
    cleaned = clean_question(question)
    expanded = expand_abbreviations(cleaned)
    return expanded or question


# ─────────────────────────────────────────────────────────────────────────────
# 2. Intent detection
# ─────────────────────────────────────────────────────────────────────────────

# Keyword -> intent mapping. Order matters: first match wins.
INTENT_RULES = [
    ("registration", [
        "iec", "import export code", "gst", "gstin", "ad code", "rcmc",
        "register", "registration", "anuchek", "become an exporter",
    ]),
    ("documents", [
        "document", "paperwork", "certificate", "shipping bill", "bill of lading",
        "invoice", "packing list", "phytosanitary", "fssai", "coo", "memo",
        "needed", "required", "require", "list",
    ]),
    ("payment", [
        "payment", "letter of credit", "lc", "telegraphic", "remittance",
        "foreign exchange", "forex", "rupee", "invoice payment", "money", "get paid",
    ]),
    ("incoterms", [
        "incoterm", "fob", "cif", "cfr", "free on board", "cost insurance",
        "shipment terms", "delivery terms",
    ]),
    ("hs_code", [
        "hs code", "hsn", "harmonized", "hs classification", "tariff",
    ]),
    ("incentives", [
        "incentive", "rodtp", "duty", "drawback", "scheme", "subsidy",
        "remission", "refund", "benefit",
    ]),
    ("logistics", [
        "logistics", "shipping", "freight", "carrier", "customs clearance",
        "port", "warehouse", "customs broker", "sailing", "transport",
    ]),
    ("country", [
        "to ", "country", "germany", "usa", "united states", "uae", "uk",
        "united kingdom", "europe", "european", "import requirements",
    ]),
    ("certification", [
        "certification", "certificate", "fssai", "apeda", "bis", "gmp",
        "halal", "organic", "quality",
    ]),
    ("faq", [
        "what is", "what's", "meaning", "define", "explain",
    ]),
]

# Normalised intent names used in the UI/prompt routing
INTENT_LABELS = {
    "registration": "Registrations & Licences",
    "documents": "Documents & Procedures",
    "payment": "Payments & Forex",
    "incoterms": "Incoterms & Trade Terms",
    "hs_code": "HS Code Guidance",
    "incentives": "Incentives & Schemes",
    "logistics": "Logistics & Customs",
    "country": "Country-Specific Import Requirements",
    "certification": "Product Certifications",
    "faq": "General Query",
}


def detect_intent(question: str) -> str:
    """
    Classify the user's question into a broad intent category.
    Returns the intent key (see INTENT_RULES) or 'general'.
    """
    q = question.lower().strip()
    for intent, keywords in INTENT_RULES:
        for kw in keywords:
            if kw in q:
                return intent
    return "general"


def intent_label(intent: str) -> str:
    """Human-readable label for an intent key."""
    return INTENT_LABELS.get(intent, "General Query")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Convenience wrapper
# ─────────────────────────────────────────────────────────────────────────────

def process_question(question: str) -> dict:
    """
    One-stop helper: normalise + detect intent.
    Returns a dict with the enriched query and metadata.
    """
    normalized = normalize_query(question)
    intent = detect_intent(question)
    return {
        "original": question.strip(),
        "normalized": normalized,
        "intent": intent,
        "intent_label": intent_label(intent),
    }
