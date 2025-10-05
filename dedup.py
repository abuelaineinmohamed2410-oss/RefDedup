import re
import unicodedata
from typing import List, Dict, Any, Tuple
from rapidfuzz import fuzz


def normalize_text(text: str) -> str:
    """Normalize text for comparison by removing accents, punctuation, and case differences."""
    if not isinstance(text, str):
        text = str(text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    
    # Remove extra whitespace and convert to lowercase
    text = re.sub(r'\s+', ' ', text).strip().lower()
    
    # Remove common punctuation that might interfere with matching
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_doi_from_record(record: Dict[str, Any]) -> str:
    """Extract DOI from various possible fields in the record."""
    # Common fields where DOI might be stored
    doi_fields = ['LID', 'DO', 'DOI', 'M3', 'UR', 'AID']
    
    for field in doi_fields:
        if field in record:
            value = record[field]
            if isinstance(value, list):
                for v in value:
                    doi = extract_doi_from_text(str(v))
                    if doi:
                        return doi
            else:
                doi = extract_doi_from_text(str(value))
                if doi:
                    return doi
    return ""


def extract_doi_from_text(text: str) -> str:
    """Extract DOI from text using regex patterns."""
    if not text:
        return ""
    
    # Common DOI patterns
    doi_patterns = [
        r'10\.\d{4,}[^\s]*',  # Standard DOI pattern
        r'doi:\s*10\.\d{4,}[^\s]*',  # DOI with prefix
        r'https?://doi\.org/10\.\d{4,}[^\s]*',  # DOI URL
        r'https?://dx\.doi\.org/10\.\d{4,}[^\s]*'  # Alternative DOI URL
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group(0)
            # Clean up the DOI
            doi = re.sub(r'^(doi:\s*|https?://d?x?\.?doi\.org/)', '', doi, flags=re.IGNORECASE)
            return doi.strip()
    
    return ""


def parse_nbib_from_string(content: str) -> List[Dict[str, Any]]:
    """Parse NBIB (.nbib) content into a list of records."""
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
            
        # Match NBIB format: TAG- value
        match = re.match(r"^([A-Z0-9]+)\s*-\s*(.*)$", line)
        if match:
            tag, value = match.groups()
            
            if tag in record:
                # Handle multiple values for the same tag
                if isinstance(record[tag], list):
                    record[tag].append(value)
                else:
                    record[tag] = [record[tag], value]
            else:
                record[tag] = value
            last_tag = tag
        else:
            # Continuation of previous line
            if last_tag and last_tag in record:
                if isinstance(record[last_tag], list):
                    record[last_tag][-1] += " " + line
                else:
                    record[last_tag] += " " + line
    
    # Don't forget the last record
    if record:
        records.append(record)
    
    return records


def parse_ris_from_string(content: str) -> List[Dict[str, Any]]:
    """Parse RIS (.ris) content into a list of records."""
    records = []
    record = {}
    last_tag = None
    
    for line in content.splitlines():
        line = line.strip()
        
        if line == "ER  -":
            if record:
                records.append(record)
                record = {}
            last_tag = None
            continue
            
        # Match RIS format: TY  - value
        match = re.match(r"^([A-Z0-9]{2})\s\s-\s(.*)$", line)
        if match:
            tag, value = match.groups()
            
            if tag in record:
                # Handle multiple values for the same tag
                if isinstance(record[tag], list):
                    record[tag].append(value)
                else:
                    record[tag] = [record[tag], value]
            else:
                record[tag] = value
            last_tag = tag
        else:
            # Continuation of previous line
            if last_tag and last_tag in record:
                if isinstance(record[last_tag], list):
                    record[last_tag][-1] += " " + line
                else:
                    record[last_tag] += " " + line
    
    # Don't forget the last record if file doesn't end with ER
    if record:
        records.append(record)
    
    return records


def record_to_ris(record: Dict[str, Any]) -> str:
    """Convert a record dictionary back to RIS format."""
    ris_lines = []
    
    # Start with record type
    if 'TY' in record:
        ris_lines.append(f"TY  - {record['TY']}")
    else:
        ris_lines.append("TY  - JOUR")
    
    # Add all other fields
    for tag, value in record.items():
        if tag == 'TY':  # Already handled
            continue
            
        if isinstance(value, list):
            for v in value:
                ris_lines.append(f"{tag}  - {v}")
        else:
            ris_lines.append(f"{tag}  - {value}")
    
    # End record
    ris_lines.append("ER  -")
    
    return "\n".join(ris_lines)


def get_title_from_record(record: Dict[str, Any]) -> str:
    """Extract title from record, handling both RIS and NBIB formats."""
    # Try different title fields
    title_fields = ['TI', 'T1', 'Title']
    
    for field in title_fields:
        if field in record:
            title = record[field]
            if isinstance(title, list):
                title = " ".join(str(t) for t in title)
            return str(title).strip()
    
    return ""


def remove_duplicates(records: List[Dict[str, Any]], title_threshold: int = 90) -> List[Dict[str, Any]]:
    """Remove duplicate records using DOI, PMID, and fuzzy title matching."""
    if not records:
        return []
    
    cleaned = []
    seen_titles = set()
    seen_dois = set()
    seen_pmids = set()
    
    for record in records:
        # Extract identifiers
        pmid = str(record.get("PMID", "")).strip()
        doi = extract_doi_from_record(record)
        title = get_title_from_record(record)
        title_normalized = normalize_text(title)
        
        is_duplicate = False
        
        # Check for exact ID matches first (most reliable)
        if doi and doi in seen_dois:
            is_duplicate = True
        elif pmid and pmid in seen_pmids:
            is_duplicate = True
        
        # Check title similarity only if no exact ID match
        if not is_duplicate and title_normalized:
            for seen_title in seen_titles:
                similarity = fuzz.ratio(title_normalized, seen_title)
                if similarity >= title_threshold:
                    is_duplicate = True
                    break
        
        # Add record if not duplicate and has valid title
        if not is_duplicate and title_normalized:
            cleaned.append(record)
            
            # Remember this record's identifiers
            if doi:
                seen_dois.add(doi)
            if pmid:
                seen_pmids.add(pmid)
            seen_titles.add(title_normalized)
    
    return cleaned


def process_uploaded_files(uploaded_files, title_threshold: int = 90) -> Tuple[List[Dict[str, Any]], int, int, Dict[str, int]]:
    """Process uploaded NBIB or RIS files and remove duplicates."""
    all_records = []
    file_stats = {}
    
    for uploaded_file in uploaded_files:
        try:
            file_name = uploaded_file.name
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            
            if file_name.lower().endswith(".nbib"):
                records = parse_nbib_from_string(content)
            elif file_name.lower().endswith(".ris"):
                records = parse_ris_from_string(content)
            else:
                continue
            
            file_stats[file_name] = len(records)
            all_records.extend(records)
            
        except Exception as e:
            # Log error but continue processing other files
            file_stats[uploaded_file.name] = f"Error: {str(e)}"
            continue
    
    total_before = len(all_records)
    cleaned_records = remove_duplicates(all_records, title_threshold=title_threshold)
    total_after = len(cleaned_records)
    
    return cleaned_records, total_before, total_after, file_stats
