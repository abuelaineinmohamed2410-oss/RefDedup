import bibtexparser
import csv
import json
from io import StringIO
from difflib import SequenceMatcher

# ---------- Parsing different file types ----------
def parse_file(uploaded_file):
    """Parse uploaded reference file into a list of dicts"""
    name = uploaded_file.name.lower()
    data = uploaded_file.read().decode("utf-8", errors="ignore")

    records = []

    # BibTeX
    if name.endswith(".bib"):
        bib_db = bibtexparser.loads(data)
        records = bib_db.entries

    # RIS or NBIB
    elif name.endswith(".ris") or name.endswith(".nbib") or name.endswith(".txt"):
        for ref in data.strip().split("\n\n"):
            entry = {}
            for line in ref.split("\n"):
                if "  - " in line:
                    key, val = line.split("  - ", 1)
                    entry[key.strip()] = val.strip()
            if entry:
                records.append(entry)

    # CSV
    elif name.endswith(".csv"):
        reader = csv.DictReader(StringIO(data))
        records = list(reader)

    else:
        raise ValueError("Unsupported file type. Please upload .bib, .ris, .nbib, .csv, or .txt")

    return records


# ---------- Deduplication ----------
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate(records, threshold=0.85):
    unique = []
    duplicates = []
    for rec in records:
        title = rec.get("title", rec.get("TI", ""))  # RIS uses TI for title
        if not title:
            unique.append(rec)
            continue

        if any(similar(title, u.get("title", u.get("TI", ""))) >= threshold for u in unique):
            duplicates.append(rec)
        else:
            unique.append(rec)
    return unique, duplicates


# ---------- Exporting ----------
def export_references(records, fmt="csv"):
    if not records:
        return ""

    if fmt == "json":
        return json.dumps(records, indent=2)

    elif fmt == "csv":
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue()

    elif fmt == "bib":
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = records
        return bibtexparser.dumps(db)

    elif fmt == "ris":
        output = []
        for rec in records:
            for k, v in rec.items():
                output.append(f"{k}  - {v}")
            output.append("")  # blank line between refs
        return "\n".join(output)

    else:
        return str(records)
