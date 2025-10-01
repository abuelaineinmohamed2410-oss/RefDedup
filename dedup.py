import rispy
import bibtexparser
import csv
import io
import json
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

def parse_file(file):
    name = file.name.lower()
    content = file.read().decode("utf-8", errors="ignore")

    # RIS
    if name.endswith(".ris"):
        return rispy.loads(content)

    # NBIB (PubMed)
    if name.endswith(".nbib"):
        records = []
        entry = {}
        for line in content.splitlines():
            if line.strip() == "":
                if entry:
                    records.append(entry)
                    entry = {}
            elif line.startswith("TI"):
                entry["title"] = line[6:].strip()
            elif line.startswith("AU"):
                entry.setdefault("authors", []).append(line[6:].strip())
        if entry:
            records.append(entry)
        return records

    # BibTeX
    if name.endswith(".bib"):
        return bibtexparser.loads(content).entries

    # EndNote XML
    if name.endswith(".xml"):
        records = []
        try:
            tree = ET.ElementTree(ET.fromstring(content))
            for rec in tree.findall(".//record"):
                title = rec.findtext("titles/title/style")
                authors = [a.text for a in rec.findall("contributors/authors/author")]
                records.append({"title": title, "authors": authors})
        except Exception:
            pass
        return records

    # CSV
    if name.endswith(".csv"):
        reader = csv.DictReader(io.StringIO(content))
        return [row for row in reader]

    # TXT (fallback)
    if name.endswith(".txt"):
        return [{"title": line.strip()} for line in content.splitlines() if line.strip()]

    return []

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def deduplicate(records, threshold=0.9):
    seen = []
    duplicates = []

    for rec in records:
        title = rec.get("title", "").strip()
        if not title:
            continue

        matched = False
        for s in seen:
            if similar(title, s.get("title", "")) >= threshold:
                duplicates.append(rec)
                matched = True
                break
        if not matched:
            seen.append(rec)

    return seen, duplicates

def export_references(records, fmt):
    if fmt == "csv":
        all_fields = set()
        for r in records:
            all_fields.update(r.keys())
        fieldnames = sorted(list(all_fields))

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            row = {key: r.get(key, "") for key in fieldnames}
            writer.writerow(row)
        return output.getvalue().encode("utf-8")

    elif fmt == "ris":
        return "\n".join([f"TY  - JOUR\nTI  - {r.get('title','')}\nER  -" for r in records]).encode("utf-8")

    elif fmt == "bib":
        return "\n".join([f"@article{{{i},\n  title={{ {r.get('title','')} }}\n}}" for i, r in enumerate(records)]).encode("utf-8")

    elif fmt == "nbib":
        return "\n".join([f"TI  - {r.get('title','')}" for r in records]).encode("utf-8")

    else:  # JSON
        return json.dumps(records, indent=2).encode("utf-8")
