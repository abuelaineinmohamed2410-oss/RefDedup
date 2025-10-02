import streamlit as st
import pandas as pd
import rispy
from rapidfuzz import fuzz
import io

# -------------------
# Utility Functions
# -------------------

def load_ris(file):
    """Load RIS file and return as DataFrame."""
    entries = rispy.load(file)
    return pd.DataFrame(entries)

def load_nbib(file):
    """Parse NBIB file manually and return as DataFrame."""
    content = file.read().decode("utf-8", errors="ignore")
    records, entry = [], {}

    for line in content.splitlines():
        if line.strip() == "":
            if entry:
                records.append(entry)
                entry = {}
        elif line.startswith("TI"):
            entry["title"] = line[6:].strip()
        elif line.startswith("AU"):
            entry.setdefault("author", []).append(line[6:].strip())
        elif line.startswith("DP") or line.startswith("YR"):
            entry["year"] = line[6:].strip()

    if entry:
        records.append(entry)

    # Flatten authors into string
    for r in records:
        if isinstance(r.get("author"), list):
            r["author"] = "; ".join(r["author"])
    return pd.DataFrame(records)

def deduplicate(df, threshold=90):
    """Fuzzy title matching for deduplication."""
    unique, duplicates = [], []

    for _, row in df.iterrows():
        title = str(row.get("title", ""))
        if not title:
            continue

        is_dup = False
        for u in unique:
            score = fuzz.token_sort_ratio(title, str(u["title"]))
            if score >= threshold:
                duplicates.append(row)
                is_dup = True
                break
        if not is_dup:
            unique.append(row)

    return pd.DataFrame(unique), pd.DataFrame(duplicates)

def export_ris(df):
    """Convert DataFrame to RIS format string."""
    buf = io.StringIO()
    for _, row in df.iterrows():
        buf.write("TY  - JOUR\n")
        buf.write(f"TI  - {row.get('title','')}\n")
        buf.write(f"AU  - {row.get('author','')}\n")
        buf.write(f"PY  - {row.get('year','')}\n")
        buf.write("ER  -\n\n")
    return buf.getvalue().encode("utf-8")

# -------------------
# Streamlit UI
# -------------------

st.title("Reference Deduplication Tool")
st.write("Upload your `.nbib` or `.ris` file. The tool will remove duplicates (based on title similarity) and provide two RIS files: one cleansed set and one containing duplicates.")

uploaded_file = st.file_uploader("Upload File", type=["nbib", "ris"])

threshold = st.slider("Deduplication Threshold (%)", 70, 100, 90)

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()

    if ext == "ris":
        df = load_ris(uploaded_file)
    elif ext == "nbib":
        df = load_nbib(uploaded_file)
    else:
        df = None
        st.error("Unsupported file format.")

    if df is not None and not df.empty:
        st.success(f"Loaded {len(df)} references.")

        cleaned, duplicates = deduplicate(df, threshold)

        st.write(f"✅ {len(cleaned)} unique references")
        st.write(f"⚠️ {len(duplicates)} duplicates found")

        # Downloads
        st.download_button(
            "Download Cleaned References (RIS)",
            data=export_ris(cleaned),
            file_name="cleaned.ris",
            mime="application/x-research-info-systems"
        )

        st.download_button(
            "Download Duplicate References (RIS)",
            data=export_ris(duplicates),
            file_name="duplicates.ris",
            mime="application/x-research-info-systems"
        )
