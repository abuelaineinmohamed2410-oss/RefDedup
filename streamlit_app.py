import streamlit as st
import pandas as pd
import rispy
import bibtexparser
from rapidfuzz import fuzz
import io

# -------------------
# Utility Functions
# -------------------

def load_ris(file):
    entries = rispy.load(file)
    return pd.DataFrame(entries)

def load_csv(file):
    return pd.read_csv(file)

def load_bib(file):
    content = file.read().decode("utf-8", errors="ignore")
    bib_db = bibtexparser.loads(content)
    records = []
    for entry in bib_db.entries:
        records.append({
            "title": entry.get("title", ""),
            "author": entry.get("author", ""),
            "year": entry.get("year", ""),
        })
    return pd.DataFrame(records)

def deduplicate(df, threshold=85):
    unique = []
    duplicates = []

    for _, row in df.iterrows():
        is_dup = False
        for u in unique:
            score = fuzz.ratio(str(row['title']), str(u['title']))
            if score >= threshold:
                duplicates.append(row)
                is_dup = True
                break
        if not is_dup:
            unique.append(row)

    cleaned = pd.DataFrame(unique)
    duplicates = pd.DataFrame(duplicates)
    return cleaned, duplicates

def export_file(df, fmt="csv"):
    buf = io.StringIO()
    if fmt == "csv":
        df.to_csv(buf, index=False)
    elif fmt == "ris":
        for _, row in df.iterrows():
            buf.write("TY  - JOUR\n")
            buf.write(f"TI  - {row.get('title','')}\n")
            buf.write(f"AU  - {row.get('author','')}\n")
            buf.write(f"PY  - {row.get('year','')}\n")
            buf.write("ER  -\n\n")
    elif fmt == "bib":
        for i, row in df.iterrows():
            buf.write(f"@article{{ref{i},\n")
            buf.write(f"  title={{ {row.get('title','')} }},\n")
            buf.write(f"  author={{ {row.get('author','')} }},\n")
            buf.write(f"  year={{ {row.get('year','')} }}\n")
            buf.write("}\n\n")
    return buf.getvalue()

# -------------------
# Streamlit UI
# -------------------

st.title("📚 Reference Deduplication Tool")
st.write("Upload your reference files, set a deduplication threshold, and export cleaned + duplicates.")

uploaded_file = st.file_uploader(
    "Upload Reference File (RIS, BibTeX, CSV)", 
    type=["ris", "bib", "csv", "txt"]
)

threshold = st.slider("Deduplication Threshold (%)", 70, 100, 85)

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()

    if ext == "ris":
        df = load_ris(uploaded_file)
    elif ext == "csv":
        df = load_csv(uploaded_file)
    elif ext == "bib":
        df = load_bib(uploaded_file)
    else:
        st.error("Unsupported file format yet.")
        df = None

    if df is not None and not df.empty:
        st.success(f"Loaded {len(df)} references.")

        cleaned, duplicates = deduplicate(df, threshold)

        st.subheader("Preview of Cleaned References")
        st.dataframe(cleaned.head(20))

        # Export options
        st.subheader("Download Results")

        col1, col2 = st.columns(2)

        with col1:
            fmt = st.selectbox("Export Format for Cleaned", ["csv", "ris", "bib"])
            st.download_button(
                "Download Cleaned References",
                data=export_file(cleaned, fmt),
                file_name=f"cleaned.{fmt}",
                mime="text/plain"
            )

        with col2:
            fmt2 = st.selectbox("Export Format for Duplicates", ["csv", "ris", "bib"])
            st.download_button(
                "Download Duplicate References",
                data=export_file(duplicates, fmt2),
                file_name=f"duplicates.{fmt2}",
                mime="text/plain"
            )
