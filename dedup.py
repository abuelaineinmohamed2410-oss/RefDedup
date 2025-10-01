import bibtexparser
import csv
import json
from io import StringIO
from difflib import SequenceMatcher

# --- Parse input files ---
def parse_file(uploaded_file):
    name = uploaded_file.name.lower()
    data = uploaded_file.read().decode("utf-8", errors="ignore")

    if name.endswith(".bib"):
        bib_db = bibtexparser.loads(data)
        return bib_db.entries
    elif name.endswith(".ris"):
        return [dict([line.split(" - ") for line in ref.split("\n") if " - " in line]) for ref in data.split("\n\n") if ref.strip()]
    elif name.endswith(".nbib"):
        return [dict([line.split(" - ") for line in ref.split("\n") if " - " in line]) for ref in data.split("\n\n") if ref.strip()]
    elif name.endswith(".csv"):
        reader = csv.DictReader(StringIO(data))
        return list(reader)
    else:
        raise ValueError("Unsupported file type. Please upload .bib, .ris, .nbib, or .csv")

# --- Simple deduplication ---
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def deduplicate(records, threshold=0.85):
    unique = []
    duplicates = []
    for rec in records:
        if any(similar(rec.get("title",""), u.get("title","")) >= threshold for u in unique):
            duplicates.append(rec)
        else:
            unique.append(rec)
    return unique, duplicates

# --- Export functions ---
def export_references(records, fmt="bib"):
    if fmt == "json":
        return json.dumps(records, indent=2)
    elif fmt == "csv":
        if not records:
            return ""
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
        return output.getvalue()
    elif fmt == "bib":
        db = bibtexparser.bibdatabase.BibDatabase()
        db.entries = records
        return bibtexparser.dumps(db)
    else:
        return str(records)
