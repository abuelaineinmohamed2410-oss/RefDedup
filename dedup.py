import re
import io
import csv
import rispy
import xml.etree.ElementTree as ET
from rapidfuzz import fuzz


# ---------------- NBIB Parser ---------------- #
def parse_nbib(content: str):
    records = []
    record = {}
    last_tag = None
    for line in content.splitlines():
        line = line.strip()
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


# ---------------- BibTeX Parser ---------------- #
def parse_bib(content: str):
    records = []
    entry = {}
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("@"):
            if entry:
                records.append(entry)
                entry = {}
        elif "=" in line:
            key, value = line.split("=", 1)
            entry[key.strip()] = value.strip().strip("{},")
    if entry:
        records.append(entry)
    return records


# ---------------- EndNote XML Parser ---------------- #
def parse_endnote_xml(content: str):
    records = []
    root = ET.fromstring(content)
    for record in root.findall(".//record"):
        entry = {}
        for field in record:
            tag = field.tag
            value = "".join(field.itertext()).strip()
            if tag in entry:
                if isinstance(entry[tag], list):
                    entry[tag].append(value)
                else:
                    entry[tag] = [entry[tag], value]
            else:
                entry[tag] = value
        records.append(entry)
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
    dups = []
    seen_titles = []
    seen_ids = set()

    for rec in records:
        pmid = rec.get("PMID", "")
        doi = rec.get("DO", rec.get("LID", ""))
        title = rec.get("TI", rec.get("title", ""))

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
                if fuzz.ratio(str(title).lower(), str(t).lower()) >= title_threshold:
                    duplicate = True
                    break

        if duplicate:
            dups.append(rec)
