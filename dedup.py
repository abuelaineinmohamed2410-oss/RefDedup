import rispy, bibtexparser, pandas as pd
import io, json, xml.etree.ElementTree as ET
from rapidfuzz import fuzz

def normalize_record(rec):
    return {
        "title": (rec.get("title") or "").strip(),
        "authors": rec.get("authors", []),
        "year": rec.get("year", ""),
        "journal": rec.get("journal", "")
    }

def parse_file(file):
    name = file.name.lower()
    content = file.read().decode("utf-8", errors="ignore")

    if name.endswith(".ris"):
        return [normalize_record(r) for r in rispy.loads(content)]
    if name.endswith(".nbib"):
        records, entry = [], {}
        for line in content.splitlines():
            if line.strip() == "":
                if entry:
                    records.append(normalize_record(entry))
                    entry = {}
            elif line.startswith("TI"):
                entry["title"] = line[6:].strip()
            elif line.startswith("AU"):
                entry.setdefault("authors", []).append(line[6:].strip())
        if entry:
            records.append(normalize_record(entry))
        return records
    if name.endswith(".bib"):
        return [normalize_record(r) for r in bibtexparser.loads(content).entries]
    if name.endswith(".xml"):
        records = []
        root = ET.fromstring(content)
        for rec in root.findall(".//record"):
            title = rec.findtext("titles/title/style", "")
            authors = [a.text for a in rec.findall("contributors/authors/author")]
            records.append(normalize_record({"title": title, "authors": authors}))
        return records
    if name.endswith(".csv"):
        df = pd.read_csv(io.StringIO(content))
        return [normalize_record(row) for _, row in df.iterrows()]
    return [{"title": line.strip()} for line in content.splitlines() if line.strip()]

def deduplicate(records, threshold=90):
    seen, duplicates = [], []
    for rec in records:
        title = rec["title"]
        if not title:
            continue
        matched = False
        for s in seen:
            if fuzz.token_sort_ratio(title, s["title"]) >= threshold:
                duplicates.append(rec)
                matched = True
                break
        if not matched:
            seen.append(rec)
    return seen, duplicates

def export_references(records, fmt):
    if fmt == "csv":
        return pd.DataFrame(records).to_csv(index=False).encode("utf-8")
    if fmt == "ris":
        return "\n".join([f"TY  - JOUR\nTI  - {r['title']}\nER  -" for r in records]).encode("utf-8")
    if fmt == "bib":
        return "\n".join([f"@article{{,\n  title={{ {r['title']} }}\n}}" for r in records]).encode("utf-8")
    if fmt == "nbib":
        return "\n".join([f"TI  - {r['title']}" for r in records]).encode("utf-8")
    return json.dumps(records, indent=2).encode("utf-8")
