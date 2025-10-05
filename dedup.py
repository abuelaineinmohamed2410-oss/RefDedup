import re
import unicodedata
from typing import List, Dict, Any, Tuple
from rapidfuzz import fuzz


def normalize_text(text: str) -> str:
    """Normalize text for comparison - more conservative approach."""
    if not isinstance(text, str):
        text = str(text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('utf-8')
    
    # Convert to lowercase and clean whitespace
    text = re.sub(r'\s+', ' ', text).strip().lower()
    
    # Only remove basic punctuation, keep more structure
    text = re.sub(r'[^\w\s\-\(\)\[\]]', ' ', text)
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
                        return doi.lower()  # Normalize DOI case
            else:
                doi = extract_doi_from_text(str(value))
                if doi:
                    return doi.lower()  # Normalize DOI case
    return ""


def extract_doi_from_text(text: str) -> str:
    """Extract DOI from text using regex patterns."""
    if not text:
        return ""
    
    # More specific DOI patterns to avoid false matches
    doi_patterns = [
        r'10\.\d{4,9}/[^\s]+',  # Standard DOI pattern - more specific
        r'doi:\s*10\.\d{4,9}/[^\s]+',  # DOI with prefix
        r'https?://doi\.org/10\.\d{4,9}/[^\s]+',  # DOI URL
        r'https?://dx\.doi\.org/10\.\d{4,9}/[^\s]+'  # Alternative DOI URL
    ]
    
    for pattern in doi_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group(0)
            # Clean up the DOI
            doi = re.sub(r'^(doi:\s*|https?://d?x?\.?doi\.org/)', '', doi, flags=re.IGNORECASE)
            # Remove trailing punctuation that might not be part of DOI
            doi = re.sub(r'[.,;)\]}]+$', '', doi)
            return doi.strip()
    
    return ""


def extract_pmid_from_record(record: Dict[str, Any]) -> str:
    """Extract PMID more carefully."""
    # Fields that might contain PMID
    pmid_fields = ['PMID', 'M3', 'AID', 'AN']
    
    for field in pmid_fields:
        if field in record:
            value = record[field]
            if isinstance(value, list):
                for v in value:
                    pmid = extract_pmid_from_text(str(v))
                    if pmid:
                        return pmid
            else:
                pmid = extract_pmid_from_text(str(value))
                if pmid:
                    return pmid
    return ""


def extract_pmid_from_text(text: str) -> str:
    """Extract PMID from text."""
    if not text:
        return ""
    
    # PMID patterns
    pmid_patterns = [
        r'\b(\d{7,8})\b',  # 7-8 digit numbers (typical PMID range)
        r'pmid:\s*(\d{7,8})',  # PMID with prefix
        r'pubmed/(\d{7,8})'  # PubMed URL format
    ]
    
    for pattern in pmid_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pmid = match.group(1) if match.groups() else match.group(0)
            # Validate PMID range (should be reasonable)
            if pmid.isdigit() and 1000000 <= int(pmid) <= 99999999:
                return pmid
    
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


def are_titles_similar(title1: str, title2: str, threshold: int = 90) -> Tuple[bool, int]:
    """Check if two titles are similar with more conservative matching."""
    if not title1 or not title2:
        return False, 0
    
    norm_title1 = normalize_text(title1)
    norm_title2 = normalize_text(title2)
    
    # If titles are too short, be more conservative
    if len(norm_title1) < 20 or len(norm_title2) < 20:
        threshold = min(95, threshold + 5)
    
    # Calculate similarity
    similarity = fuzz.ratio(norm_title1, norm_title2)
    
    # Additional check: if titles are very different in length, be more conservative
    len_diff = abs(len(norm_title1) - len(norm_title2))
    if len_diff > max(len(norm_title1), len(norm_title2)) * 0.3:
        threshold += 5
    
    return similarity >= threshold, similarity


def remove_duplicates(records: List[Dict[str, Any]], title_threshold: int = 95) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Remove duplicate records using DOI, PMID, and fuzzy title matching.
    Returns (cleaned_records, removed_records) for analysis."""
    if not records:
        return [], []
    
    cleaned = []
    removed = []
    seen_titles = {}  # Store title -> record mapping for debugging
    seen_dois = {}
    seen_pmids = {}
    
    for i, record in enumerate(records):
        # Extract identifiers
        pmid = extract_pmid_from_record(record)
        doi = extract_doi_from_record(record)
        title = get_title_from_record(record)
        title_normalized = normalize_text(title)
        
        is_duplicate = False
        duplicate_reason = ""
        matching_record_index = -1
        
        # Check for exact DOI matches first (most reliable)
        if doi and doi in seen_dois:
            is_duplicate = True
            duplicate_reason = f"DOI match: {doi}"
            matching_record_index = seen_dois[doi]
        
        # Check for exact PMID matches
        elif pmid and pmid in seen_pmids:
            is_duplicate = True
            duplicate_reason = f"PMID match: {pmid}"
            matching_record_index = seen_pmids[pmid]
        
        # Check title similarity only if no exact ID match
        elif title_normalized and len(title_normalized) > 10:  # Only for meaningful titles
            for seen_title, seen_index in seen_titles.items():
                is_similar, similarity_score = are_titles_similar(title_normalized, seen_title, title_threshold)
                if is_similar:
                    is_duplicate = True
                    duplicate_reason = f"Title similarity: {similarity_score}% with record {seen_index + 1}"
                    matching_record_index = seen_index
                    break
        
        # Add record if not duplicate and has valid title
        if not is_duplicate and title_normalized:
            record_index = len(cleaned)
            cleaned.append(record)
            
            # Remember this record's identifiers
            if doi:
                seen_dois[doi] = record_index
            if pmid:
                seen_pmids[pmid] = record_index
            if title_normalized:
                seen_titles[title_normalized] = record_index
        else:
            # Store information about why this record was removed
            record['_duplicate_reason'] = duplicate_reason
            record['_original_index'] = i + 1
            record['_matching_record'] = matching_record_index + 1 if matching_record_index >= 0 else -1
            removed.append(record)
    
    return cleaned, removed


def process_uploaded_files(uploaded_files, title_threshold: int = 95) -> Tuple[List[Dict[str, Any]], int, int, Dict[str, int], List[Dict[str, Any]]]:
    """Process uploaded NBIB or RIS files and remove duplicates.
    Returns (cleaned_records, total_before, total_after, file_stats, removed_records)."""
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
    cleaned_records, removed_records = remove_duplicates(all_records, title_threshold=title_threshold)
    total_after = len(cleaned_records)
    
    return cleaned_records, total_before, total_after, file_stats, removed_records
