import re
import unicodedata
from rapidfuzz import fuzz, process

def normalize_text(text):
    if not isinstance(text, str):
        text = str(text)
    # Remove accents, unify case, strip
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    return re.sub(r's+', ' ', text).strip().lower()

def parse_nbib_from_string(content):
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
        match = re.match(r"^([A-Z0-9]+)s*-s*(.*)$", line)
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

def parse_ris_from_string(content):
    records = []
    record = {}
    last_tag = None
    pattern = r"^([A-Z0-9]{2})  - (.*)$"
    for line in content.splitlines():
        line = line.strip()
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
    if record:
        records.append(record)
    return records

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
    return "
".join(ris_lines)

def remove_duplicates(records, title_threshold=90):
    cleaned = []
    seen_titles = set()
    seen_ids = set()
    for rec in records:
        pmid = str(rec.get("PMID", "")).strip()
        doi = str(rec.get("LID", "")).strip()
        title = rec.get("TI", "")
        title = " ".join(title) if isinstance(title, list) else str(title)
        title_key = normalize_text(title)

        # Remove near-duplicates instead of only exact
        is_duplicate = False
        # Check IDs
        for ident in (pmid, doi):
            if ident and ident in seen_ids:
                is_duplicate = True
                break
        # Check title fuzzy
        if not is_duplicate:
            for t in seen_titles:
                if fuzz.ratio(title_key, t) >= title_threshold:
                    is_duplicate = True
                    break
        if not is_duplicate and title_key.strip():
            cleaned.append(rec)
            for ident in (pmid, doi):
                if ident:
                    seen_ids.add(ident)
            seen_titles.add(title_key)
    return cleaned

def process_uploaded_files(uploaded_files, title_threshold=90):
    all_records = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name.lower()
        content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        if file_name.endswith(".nbib"):
            records = parse_nbib_from_string(content)
        elif file_name.endswith(".ris"):
            records = parse_ris_from_string(content)
        else:
            continue
        all_records.extend(records)
    total_before = len(all_records)
    cleaned_records = remove_duplicates(all_records, title_threshold=title_threshold)
    total_after = len(cleaned_records)
    return cleaned_records, total_before, total_after
