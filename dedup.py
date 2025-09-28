# dedup.py
import os
import re
from rapidfuzz import fuzz

# ---------------- Parsing Functions ---------------- #
def parse_nbib(file_path):
    records = []
    record = {}
    last_tag = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
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
                    if isinstance(record[last_tag], list):
                        record[last_tag][-1] += " " + line
                    else:
                        record[last_tag] += " " + line
    if record:
        records.append(record)
    return records


def parse_ris(file_path):
    records = []
    record = {}
    last_tag = None
    pattern = r"^([A-Z0-9]{2})  - (.*)$"
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
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
                    if isinstance(record[last_tag], list):
                        record[last_tag][-1] += " " + line
                    else:
                        record[last_tag] += " " + line
    return records


# ---------------- RIS Export ---------------- #
def record_to_ris(record):
    ris_lines = ["TY  - JOUR"]
    for tag, value in record.items():
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


# ---------------- Processing Function ---------------- #
def process_files(files, title_threshold=90):
    all_records = []
    file_counts = {}

    for file_path in files:
        records_from_file = []
        if file_path.lower().endswith(".nbib"):
            records_from_file = parse_nbib(file_path)
        elif file_path.lower().endswith(".ris"):
            records_from_file = parse_ris(file_path)

        file_counts[os.path.basename(file_path)] = len(records_from_file)
        all_records.extend(records_from_file)

    total_records_before = len(all_records)
    cleaned_records = remove_duplicates(all_records, title_threshold=title_threshold)
    total_records_after = len(cleaned_records)

    return file_counts, total_records_before, total_records_after, cleaned_records
