# dedup.py

import rispy
import csv
import io
import re

# ---------------- NBIB Parsing ---------------- #
def parse_nbib(text):
    """Parse NBIB formatted text into records."""
    records = []
    current = {}
    for line in text.splitlines():
        if line.startswith("PMID-"):
            if current:
                records.append(current)
                current = {}
            current["pmid"] = line.replace("PMID-", "").strip()
        elif line.startswith("TI  -"):
            current["title"] = line.replace("TI  -", "").strip()
        elif line.startswith("AU  -"):
            current.setdefault("authors", []).append(line.replace("AU  -", "").strip())
    if current:
        records.append(current)
    return records

# ---------------- Deduplication ---------------- #
def process_uploaded_files(uploaded_files, title_threshold=90):
    """Process multiple files, merge, and deduplicate by title."""
    all_records = []

    for file in uploaded_files:
        name = file.name.lower()
        content = file.read()

        if name.endswith(".ris"):
            file.seek(0)
            records = rispy.load(file)
        elif name.endswith(".nbib"):
            records = parse_nbib(content.decode("utf-8"))
        elif name.endswith(".csv"):
            file.seek(0)
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            records = list(reader)
        elif name.endswith(".bib"):
            records = parse_bib(content.decode("utf-8"))
        else:
            raise ValueError("Unsupported file format")

        all_records.extend(records)

    # Deduplicate (simple exact title match, case-insensitive)
    unique_records, duplicates = [], []
    seen = set()
    for rec in all_records:
        title = str(rec.get("title", "")).strip().lower()
        if not title:
            continue
        if title in seen:
            duplicates.append(rec)
        else:
            seen.add(title)
            unique_records.append(rec)

    return unique_records, duplicates, len(all_records), len(unique_records)

# ---------------- Export Helpers ---------------- #
def export_to_ris(records):
    return "\n\n".join([record_to_ris(r) for r in records])

def export_to_bib(records):
    return "\n\n".join([record_to_bib(r) for r in records])

def export_to_csv(records):
    output = io.StringIO()
    if not records:
        return ""
    writer = csv.DictWriter(output, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()

def export_to_nbib(records):
    return "\n\n".join([record_to_nbib(r) for r in records])

# ---------------- Converters ---------------- #
def record_to_ris(record):
    return f"TY  - JOUR\nTI  - {record.get('title','')}\nAU  - {', '.join(record.get('authors', []) if isinstance(record.get('authors'), list) else [record.get('authors','')])}\nER  -"

def record_to_bib(record):
    return f"@article{{,\ntitle={{ {record.get('title','')} }},\nauthor={{ {' and '.join(record.get('authors', []) if isinstance(record.get('authors'), list) else [record.get('authors','')])} }},\n}}"

def record_to_nbib(record):
    return f"PMID- {record.get('pmid','')}\nTI  - {record.get('title','')}\n" + "\n".join([f"AU  - {a}" for a in (record.get('authors', []) if isinstance(record.get('authors'), list) else [record.get('authors','')])])

# ---------------- Bib Parser ---------------- #
def parse_bib(text):
    """Very simple BibTeX parser (just extracts title & authors)."""
    records = []
    entries = text.split("@")[1:]
    for entry in entries:
        rec = {}
        title_match = re.search(r"title\s*=\s*[{](.*?)[}]", entry, re.I)
        author_match = re.search(r"author\s*=\s*[{](.*?)[}]", entry, re.I)
        if title_match:
            rec["title"] = title_match.group(1)
        if author_match:
            rec["authors"] = [a.strip() for a in author_match.group(1).split(" and ")]
        records.append(rec)
    return records
