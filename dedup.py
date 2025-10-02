import re
from rapidfuzz import fuzz
import pandas as pd
from unidecode import unidecode

def normalize_text(text):
    if not text:
        return ""
    text = unidecode(text)
    text = re.sub(r"\s+", " ", text.strip().lower())
    return text

def parse_nbib_from_string(content):
    # Unchanged from your version...
    # (The existing parse_nbib_from_string)

def parse_ris_from_string(content):
    # Unchanged from your version...
    # (The existing parse_ris_from_string)

def parse_bib_from_string(content):
    # Simple bib parser with regex or use bibtexparser library (if installed)
    import bibtexparser
    bib_db = bibtexparser.loads(content)
    records = []
    for entry in bib_db.entries:
        rec = {}
        for key, val in entry.items():
            rec[key.upper()] = val
        records.append(rec)
    return records

def parse_csv_from_string(content):
    df = pd.read_csv(StringIO(content))
    records = []
    for _, row in df.iterrows():
        rec = {}
        for col_name, val in row.items():
            rec[str(col_name).upper()] = val if pd.notna(val) else ""
        records.append(rec)
    return records

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

def remove_duplicates(records, title_threshold=90):
    cleaned = []
    duplicates = []

    seen_dois_pmids = set()
    seen_titles = []

    for rec in records:
        title = rec.get("TI", "") or rec.get("TITLE", "")
        doi = rec.get("LID", "") or rec.get("DOI", "") or rec.get("ID", "")
        pmid = rec.get("PMID", "")

        # Normalize
        title_norm = normalize_text(title)
        doi_norm = normalize_text(doi)
        pmid_norm = normalize_text(str(pmid))

        # Author check
        authors = rec.get("AU", rec.get("AUTHORS", []))
        if isinstance(authors, str):
            authors_list = [a.strip() for a in re.split(r"[;,|]", authors) if a.strip()]
        elif isinstance(authors, list):
            authors_list = authors
        else:
            authors_list = []

        duplicate = False

        # Check DOI/PMID
        id_key = None
        if doi_norm:
            id_key = "DOI:" + doi_norm
        elif pmid_norm:
            id_key = "PMID:" + pmid_norm

        if id_key and id_key in seen_dois_pmids:
            duplicate = True
        else:
            # Fuzzy title match with author validation
            for seen_title, seen_authors in seen_titles:
                sim = fuzz.ratio(title_norm, seen_title)
                if sim >= title_threshold:
                    # Check author overlap: simple set intersection threshold >30%
                    common_authors = set([a.lower() for a in authors_list]) & set([a.lower() for a in seen_authors])
                    if len(common_authors) / max(len(authors_list), 1) > 0.3:
                        duplicate = True
                        break

        if not duplicate:
            cleaned.append(rec)
            if id_key:
                seen_dois_pmids.add(id_key)
            seen_titles.append((title_norm, authors_list))
        else:
            duplicates.append(rec)

    return cleaned, duplicates

def process_uploaded_files(uploaded_files, title_threshold=90):
    all_records = []
    for uf in uploaded_files:
        name = uf.name.lower()
        content = uf.getvalue().decode("utf-8")
        if name.endswith(".nbib"):
            records = parse_nbib_from_string(content)
        elif name.endswith(".ris"):
            records = parse_ris_from_string(content)
        elif name.endswith(".bib"):
            records = parse_bib_from_string(content)
        elif name.endswith(".csv"):
            records = parse_csv_from_string(content)
        else:
            records = []
        all_records.extend(records)

    total_before = len(all_records)
    cleaned, duplicates = remove_duplicates(all_records, title_threshold=title_threshold)
    total_after = len(cleaned)
    return cleaned, duplicates, total_before, total_after
