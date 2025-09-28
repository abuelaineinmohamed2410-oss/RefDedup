import re
from rapidfuzz import fuzz

# ---------------- Parsing Functions ---------------- #
def parse_nbib(source):
    records = []
    record = {}
    last_tag = None

    # Detect if source is path or uploaded file
    if hasattr(source, "read"):  # uploaded file
        lines = source.read().decode("utf-8").splitlines()
    else:  # path
        with open(source, "r", encoding="utf-8") as f:
            lines = f.readlines()

    for line in lines:
        line = line.rstrip("\n").strip()
        if not line:
            if record:
                records.append(record)
                record = {}
            last_tag = None
            continue
        match = re.match(r"^([A-Z0-9]+)\s*-\s*(.*)$", line)
        if match:
            tag, value = match.groups()
            if tag in record:
                if isinstance(record[tag], list):
                    record[tag].append(value)
                else:
                    record[tag] = [record[tag], value]
            else:
                record[tag] = value
            last_tag = tag
        else:
            if last_tag:
                if last_tag not in record:
                    record[last_tag] = line
                elif isinstance(record[last_tag], list):
                    record[last_tag][-1] += " " + line
                else:
                    record[last_tag] += " " + line
    if record:
        records.append(record)
    return records


def parse_ris(source):
    records = []
    record = {}
    last_tag = None
    pattern = r"^([A-Z0-9]{2})  - (.*)$"

    # Detect if source is path or uploaded file
    if hasattr(source, "read"):  # uploaded file
        lines = source.read().decode("utf-8").splitlines()
    else:  # path
        with open(source, "r", encoding="utf-8") as f:
            lines = f.readlines()

    for line in lines:
        line = line.rstrip("\n").strip()
        if line == "ER  -":
            if record:
                records.append(record)
                record = {}
            last_tag = None
            continue
        match = re.match(pattern, line)
        if match:
            tag, value = match.groups()
            if tag in record:
                if isinstance(record[tag], list):
                    record[tag].append(value)
                else:
                    record[tag] = [record[tag], value]
            else:
                record[tag] = value
            last_tag = tag
        else:
            if last_tag:
                if last_tag not in record:
                    record[last_tag] = line
                elif isinstance(record[last_tag], list):
                    record[last_tag][-1] += " " + line
                else:
                    record[last_tag] += " " + line
    return records


# ---------------- RIS Export ---------------- #
def record_to_ris(record):
    ris_lines = ["TY  - JOUR"]
    for tag in record:
        value = record[tag]
        if isinstance(value, list):
            for v in value:
                ris_lines.append(f"{tag}  - {v}")
        else:
            ris_lines.append(f"{tag}  - {value}")
    ris_lines.append("ER  -")
    return "\n".join(ris_lines)


# ---------------- Duplicate Removal ---------------- #
def remove_duplicates(records, title_threshold=90):
    cleaned = []
    seen_titles = []
    seen_ids = set()  # for PMID or DOI

    for rec in records:
        pmid = rec.get("PMID", "")
        doi = rec.get("LID", "")
        title = rec.get("TI", "")

        if isinstance(title, list):
            title = " ".join(title)
        if isinstance(doi, list):
            doi = doi[0]
        if isinstance(pmid, list):
            pmid = pmid[0]

        duplicate = False
        if pmid in seen_ids or doi in seen_ids:
            duplicate = True
        else:
            for t in seen_titles:
                if fuzz.ratio(title.lower(), t.lower()) >= title_threshold:
                    duplicate = True
                    break

        if not duplicate:
            cleaned.append(rec)
            seen_titles.append(title)
            if pmid:
                seen_ids.add(pmid)
            if doi:
                seen_ids.add(doi)

    return cleaned
