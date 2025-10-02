import rispy
import pandas as pd
import io
import difflib
import xml.etree.ElementTree as ET

# ------------------- FILE PARSERS ------------------- #
def parse_file(file):
    ext = file.name.split(".")[-1].lower()
    content = file.read().decode("utf-8", errors="ignore")

    if ext == "ris":
        file.seek(0)
        return rispy.load(file)

    elif ext == "nbib":
        records = []
        entry = {}
        for line in content.splitlines():
            if line.startswith("PMID-"):
                if entry: records.append(entry)
                entry = {"PMID": line[6:].strip()}
            elif line.startswith("TI  -"):
                entry["title"] = line[6:].strip()
            elif line.startswith("AU  -"):
                entry.setdefault("authors", "")
                entry["authors"] += line[6:].strip() + "; "
        if entry: records.append(entry)
        return records

    elif ext == "bib":
        records = []
        for entry in content.split("@")[1:]:
            lines = entry.splitlines()
            title, authors = "", ""
            for line in lines:
                if "title" in line.lower():
                    title = line.split("=",1)[1].strip().strip("{}, ")
                if "author" in line.lower():
                    authors = line.split("=",1)[1].strip().strip("{}, ")
            records.append({"title": title, "authors": authors})
        return records

    elif ext == "xml":
        records = []
        root = ET.fromstring(content)
        for rec in root.findall(".//record"):
            title = rec.findtext("titles/title", "")
            authors = "; ".join([a.text for a in rec.findall(".//contributors/authors/author")])
            records.append({"title": title, "authors": authors})
        return records

    elif ext == "csv" or ext == "txt":
        df = pd.read_csv(io.StringIO(content))
        return df.to_dict("records")

    return []


# ------------------- DEDUPLICATION ------------------- #
def deduplicate(records, threshold=90):
    seen, kept, duplicates = [], [], []

    for rec in records:
        title = rec.get("title", "").strip()
        if not title:
            kept.append(rec)
            continue

        matched = False
        for seen_title in seen:
            if difflib.SequenceMatcher(None, title.lower(), seen_title.lower()).ratio()*100 >= threshold:
                duplicates.append(rec)
                matched = True
                break

        if not matched:
            kept.append(rec)
            seen.append(title)

    return kept, duplicates, len(records)


# ------------------- EXPORTERS ------------------- #
def export_references(records, fmt="ris"):
    buf = io.StringIO()

    if fmt == "ris":
        for r in records:
            buf.write("TY  - JOUR\n")
            if "title" in r: buf.write(f"TI  - {r['title']}\n")
            if "authors" in r: 
                for a in r['authors'].split(";"):
                    if a.strip():
                        buf.write(f"AU  - {a.strip()}\n")
            buf.write("ER  - \n\n")

    elif fmt == "bib":
        for i, r in enumerate(records):
            buf.write(f"@article{{ref{i},\n")
            if "title" in r: buf.write(f"  title = {{{r['title']}}},\n")
            if "authors" in r: buf.write(f"  author = {{{r['authors']}}},\n")
            buf.write("}\n\n")

    elif fmt == "csv":
        df = pd.DataFrame(records)
        return df.to_csv(index=False)

    elif fmt == "nbib":
        for r in records:
            if "PMID" in r: buf.write(f"PMID- {r['PMID']}\n")
            if "title" in r: buf.write(f"TI  - {r['title']}\n")
            if "authors" in r:
                for a in r['authors'].split(";"):
                    if a.strip():
                        buf.write(f"AU  - {a.strip()}\n")
            buf.write("\n")

    return buf.getvalue()
