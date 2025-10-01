import rispy
import bibtexparser
import pandas as pd
import io
import difflib
import xml.etree.ElementTree as ET

# ---------------- Parsing ---------------- #

def parse_file(file):
    ext = file.name.split(".")[-1].lower()
    content = file.read().decode("utf-8", errors="ignore")

    if ext in ["ris", "nbib"]:
        return rispy.loads(content)

    elif ext == "bib":
        return bibtexparser.loads(content).entries

    elif ext == "xml":  # EndNote XML
        try:
            tree = ET.fromstring(content)
            records = []
            for rec in tree.findall(".//record"):
                title = rec.findtext("titles/title", "")
                authors = [a.text for a in rec.findall("contributors/authors/author")]
                records.append({"title": title, "authors": "; ".join(authors)})
            return records
        except:
            return []

    elif ext == "csv":
        df = pd.read_csv(io.StringIO(content))
        return df.to_dict(orient="records")

    elif ext == "txt":
        return [{"title": line.strip()} for line in content.splitlines() if line.strip()]

    return []


# ---------------- Deduplication ---------------- #

def is_duplicate(ref1, ref2, threshold):
    title1 = ref1.get("title", "").lower()
    title2 = ref2.get("title", "").lower()
    if not title1 or not title2:
        return False
    return difflib.SequenceMatcher(None, title1, title2).ratio() >= threshold

def process_uploaded_files(files, threshold=0.9):
    all_records = []
    for f in files:
        f.seek(0)  # important when reading multiple
        all_records.extend(parse_file(f))

    kept, duplicates = [], []
    for rec in all_records:
        if any(is_duplicate(rec, k, threshold) for k in kept):
            duplicates.append(rec)
        else:
            kept.append(rec)

    return kept, duplicates, len(all_records)


# ---------------- Export ---------------- #

def export_references(records, fmt):
    buf = io.StringIO()

    if fmt == "csv":
        pd.DataFrame(records).to_csv(buf, index=False)

    elif fmt in ["ris", "nbib"]:
        for r in records:
            buf.write("TY  - JOUR\n")
            if "title" in r: buf.write(f"TI  - {r['title']}\n")
            if "authors" in r: buf.write(f"AU  - {r['authors']}\n")
            buf.write("ER  - \n\n")

    elif fmt == "bib":
        for i, r in enumerate(records):
            buf.write(f"@article{{ref{i},\n")
            if "title" in r: buf.write(f"  title={{ {r['title']} }},\n")
            if "authors" in r: buf.write(f"  author={{ {r['authors']} }},\n")
            buf.write("}\n")

    return buf.getvalue().encode("utf-8")
