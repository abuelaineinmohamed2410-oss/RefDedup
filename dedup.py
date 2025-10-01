# dedup.py
import re
import csv
import io
import xml.etree.ElementTree as ET
from rapidfuzz import fuzz

# ---------- Parsing helpers (string input) ----------

def parse_ris_from_string(content):
    records = []
    record = {}
    last_tag = None
    pattern = r"^([A-Z0-9]{2})  - (.*)$"
    for raw in content.splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            if record:
                records.append(record)
                record = {}
            last_tag = None
            continue
        m = re.match(pattern, line)
        if m:
            tag, value = m.groups()
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
                    record[last_tag][-1] += " " + line.strip()
                else:
                    record[last_tag] = record.get(last_tag, "") + " " + line.strip()
    if record:
        records.append(record)
    return records

def parse_nbib_from_string(content):
    # NBIB is like RIS but tags may be alphanumeric; reuse RIS-style parsing
    records = []
    record = {}
    last_tag = None
    pattern = r"^([A-Z0-9]+)\s*-\s*(.*)$"
    for raw in content.splitlines():
        line = raw.rstrip("\n")
        if not line.strip():
            if record:
                records.append(record)
                record = {}
            last_tag = None
            continue
        m = re.match(pattern, line)
        if m:
            tag, value = m.groups()
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
                    record[last_tag][-1] += " " + line.strip()
                else:
                    record[last_tag] = record.get(last_tag, "") + " " + line.strip()
    if record:
        records.append(record)
    return records

def parse_bib_from_string(content):
    # Lightweight BibTeX parser focusing on title, author, year, doi
    records = []
    entry = {}
    in_entry = False
    key = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('@') and '{' in line:
            in_entry = True
            entry = {}
            key = line.split('{', 1)[1].rstrip(',').strip()
            continue
        if in_entry:
            if line.startswith('}'):
                if entry:
                    records.append(entry)
                entry = {}
                in_entry = False
                key = None
                continue
            # simple field match
            m = re.match(r'(\w+)\s*=\s*[{"](.+)[}"],?$', line)
            if m:
                field, val = m.groups()
                entry[field.lower()] = val
            else:
                # continuation lines: append to last field if present
                if '=' not in line and entry:
                    # get last key
                    last_key = list(entry.keys())[-1]
                    entry[last_key] = entry[last_key] + ' ' + line.strip().rstrip('",')
    return records

def parse_endnote_xml_from_string(content):
    # Minimal EndNote XML parser extracting titles, authors, year, doi
    records = []
    try:
        root = ET.fromstring(content)
    except Exception:
        return records
    # try common structure: records/record
    for rec in root.findall('.//record'):
        r = {}
        title = rec.find('.//titles/title')
        if title is not None and title.text:
            r['title'] = title.text
        # authors
        authors = []
        for au in rec.findall('.//contributors/authors/author'):
            if au is not None and au.text:
                authors.append(au.text)
        if authors:
            r['author'] = authors
        year = rec.find('.//dates/year')
        if year is not None and year.text:
            r['year'] = year.text
        doi = rec.find('.//electronic-resource-num')
        if doi is not None and doi.text:
            r['doi'] = doi.text
        records.append(r)
    return records

def parse_csv_from_string(content):
    # Attempt to read CSV; return list of dicts
    records = []
    f = io.StringIO(content)
    try:
        reader = csv.DictReader(f)
    except Exception:
        return records
    for row in reader:
        records.append({k: v for k, v in row.items()})
    return records

# ---------- Normalization to a common schema ----------

def normalize_record(raw):
    """Take parsed raw record (dict) and return common schema dict:
       {title, authors (list), year, doi, pmid, original}"""
    rec = {
        'title': None,
        'authors': [],
        'year': None,
        'doi': None,
        'pmid': None,
        'original': raw  # keep original for full export
    }

    # common keys from RIS/NBIB
    # Title: TI, T1, title
    for k in ('TI', 'T1', 'title', 'Title'):
        if k in raw:
            rec['title'] = raw[k] if not isinstance(raw[k], list) else " ".join(raw[k])
            break
    # Authors: AU, FAU, author
    authors = []
    for k in ('AU', 'FAU', 'AU1', 'author', 'authors'):
        if k in raw:
            val = raw[k]
            if isinstance(val, list):
                authors.extend(val)
            else:
                # sometimes authors in string separated by ';' or ' and '
                authors.extend(re.split(r'\s*;\s*|\sand\s|,\s*', val))
    rec['authors'] = [a.strip() for a in authors if a and a.strip()]

    # Year: DP, PY, year
    for k in ('DP', 'PY', 'year', 'Year'):
        if k in raw:
            v = raw[k]
            if isinstance(v, list):
                v = v[0]
            # take first token that looks like 4-digit year
            m = re.search(r'(\d{4})', str(v))
            if m:
                rec['year'] = m.group(1)
            else:
                rec['year'] = str(v)
            break

    # DOI: LID, DO, doi
    for k in ('LID', 'DO', 'doi', 'DOI'):
        if k in raw:
            v = raw[k]
            if isinstance(v, list):
                v = v[0]
            rec['doi'] = str(v).strip()
            break

    # PMID: PMID, pmid
    for k in ('PMID', 'pmid'):
        if k in raw:
            v = raw[k]
            if isinstance(v, list):
                v = v[0]
            rec['pmid'] = str(v).strip()
            break

    # If parsed bib fields
    if 'title' in raw and not rec['title']:
        rec['title'] = raw.get('title')
    if 'author' in raw and not rec['authors']:
        if isinstance(raw.get('author'), list):
            rec['authors'] = raw.get('author')
        else:
            rec['authors'] = [a.strip() for a in re.split(r'\s*;\s*|\sand\s|,\s*', str(raw.get('author')))]
    if 'year' in raw and not rec['year']:
        rec['year'] = raw.get('year')
    if 'doi' in raw and not rec['doi']:
        rec['doi'] = raw.get('doi')

    # fallback title from any string values
    if not rec['title']:
        for v in raw.values():
            if isinstance(v, str) and len(v) > 10:
                rec['title'] = v
                break

    # normalize title for matching
    rec['norm_title'] = normalize_text(rec['title'])
    return rec

def normalize_text(s):
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^\w\s]', '', s)  # remove punctuation
    s = s.strip()
    return s

# ---------- Deduplication ----------

def remove_duplicates(normalized_records, title_threshold=90):
    """
    normalized_records: list of recs from normalize_record
    returns cleaned_recs (kept), duplicate_recs (removed)
    """
    kept = []
    duplicates = []
    seen_ids = set()  # DOI/PMID seen

    for rec in normalized_records:
        doi = (rec.get('doi') or "").lower().strip()
        pmid = (rec.get('pmid') or "").lower().strip()
        title = rec.get('norm_title', "")

        is_dup = False

        # exact match on DOI or PMID
        if doi and doi in seen_ids:
            is_dup = True
        if pmid and pmid in seen_ids:
            is_dup = True

        # otherwise fuzzy match against kept titles
        if not is_dup:
            for kept_rec in kept:
                # prefer token_sort_ratio (handles word order)
                score = fuzz.token_sort_ratio(title, kept_rec.get('norm_title', ''))
                if score >= title_threshold:
                    is_dup = True
                    # mark as duplicate and keep the record of which kept matched
                    rec['matched_with'] = kept_rec
                    rec['match_score'] = score
                    break

        if is_dup:
            duplicates.append(rec)
        else:
            kept.append(rec)
            # register ids
            if doi:
                seen_ids.add(doi)
            if pmid:
                seen_ids.add(pmid)

    return kept, duplicates

# ---------- Exporters (multiple formats) ----------

def export_to_ris(records):
    out = io.StringIO()
    for rec in records:
        orig = rec.get('original') or {}
        # Try to output common fields
        out.write("TY  - JOUR\n")
        title = rec.get('title') or orig.get('TI') or orig.get('title') or ""
        if title:
            out.write(f"TI  - {title}\n")
        for a in rec.get('authors', []):
            out.write(f"AU  - {a}\n")
        if rec.get('year'):
            out.write(f"PY  - {rec.get('year')}\n")
        if rec.get('doi'):
            out.write(f"DO  - {rec.get('doi')}\n")
        if rec.get('pmid'):
            out.write(f"ID  - {rec.get('pmid')}\n")
        out.write("ER  -\n\n")
    return out.getvalue()

def export_to_nbib(records):
    # NBIB is similar to RIS but with different tags: use a simple RIS-like NBIB
    out = io.StringIO()
    for rec in records:
        orig = rec.get('original') or {}
        out.write("PMID- \n")  # optional
        title = rec.get('title') or ""
        if title:
            out.write(f"TI  - {title}\n")
        for a in rec.get('authors', []):
            out.write(f"AU  - {a}\n")
        if rec.get('year'):
            out.write(f"DP  - {rec.get('year')}\n")
        if rec.get('doi'):
            out.write(f"LID - {rec.get('doi')}\n")
        out.write("\n")
    return out.getvalue()

def export_to_bib(records):
    out = io.StringIO()
    for i, rec in enumerate(records, start=1):
        title = rec.get('title') or ""
        authors = " and ".join(rec.get('authors', []))
        year = rec.get('year') or ""
        out.write(f"@article{{ref{i},\n  title = {{{title}}},\n  author = {{{authors}}},\n  year = {{{year}}}\n}}\n\n")
    return out.getvalue()

def export_to_csv(records):
    # flatten to CSV with important columns
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(['title', 'authors', 'year', 'doi', 'pmid'])
    for rec in records:
        writer.writerow([rec.get('title') or "",
                         "; ".join(rec.get('authors') or []),
                         rec.get('year') or "",
                         rec.get('doi') or "",
                         rec.get('pmid') or ""])
    return out.getvalue()

# ---------- Top-level processing for uploaded files ----------

def parse_any_file_by_name_and_content(fname, content):
    ext = fname.lower().split('.')[-1]
    if ext == 'ris':
        return parse_ris_from_string(content)
    if ext in ('nbib', 'nbib.txt'):
        return parse_nbib_from_string(content)
    if ext in ('bib',):
        return parse_bib_from_string(content)
    if ext in ('xml',):
        # try EndNote XML first
        recs = parse_endnote_xml_from_string(content)
        if recs:
            return recs
        # else try as generic xml fallback: no records
        return []
    if ext in ('csv', 'txt'):
        # read csv rows as dicts
        return parse_csv_from_string(content)
    # fallback: try RIS parsing
    return parse_ris_from_string(content)

def process_uploaded_files(uploaded_files, title_threshold=90):
    """Main entry point: takes list of uploaded files (Streamlit UploadedFile),
       returns cleaned_list (normalized schema), duplicates_list (normalized schema),
       and counts"""
    parsed_raw = []
    for f in uploaded_files:
        try:
            content = f.getvalue().decode('utf-8', errors='replace')
        except Exception:
            # if binary, convert bytes->string with replace
            content = f.getvalue().decode('latin-1', errors='replace')
        parsed = parse_any_file_by_name_and_content(f.name, content)
        # parsed can be list of dicts or list of parsed bib entries
        parsed_raw.extend(parsed)

    # normalize
    normalized = [normalize_record(p) for p in parsed_raw]

    # deduplicate
    kept, duplicates = remove_duplicates(normalized, title_threshold=title_threshold)

    return kept, duplicates, len(parsed_raw)
