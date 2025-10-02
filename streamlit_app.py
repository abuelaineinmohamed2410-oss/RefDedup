import streamlit as st
from dedup import parse_file, deduplicate, export_references

st.set_page_config(page_title="Reference Deduplicator", layout="wide")

st.title("📚 Reference Deduplicator")
st.write("Upload your reference files (.bib, .ris, .nbib, .csv, .txt). The app will merge them, remove duplicates, and allow you to export results.")

uploaded_files = st.file_uploader(
    "Upload one or more files", 
    type=["bib", "ris", "nbib", "csv", "txt"], 
    accept_multiple_files=True
)

# Threshold with recommendation
threshold = st.slider("Deduplication similarity threshold", 0.5, 1.0, 0.85)
st.caption("🔹 Recommended: 0.85 (strict), 0.75 (balanced), 0.65 (loose)")

if uploaded_files:
    records = []
    for f in uploaded_files:
        try:
            records.extend(parse_file(f))
        except Exception as e:
            st.error(f"Could not parse {f.name}: {e}")

    if not records:
        st.warning("No records found.")
    else:
        unique, duplicates = deduplicate(records, threshold)

        st.success(f"✅ Found {len(unique)} unique references and {len(duplicates)} duplicates across {len(uploaded_files)} files.")

        # Preview unique references
        st.subheader("Unique References (Cleaned Preview)")
        for r in unique[:5]:
            st.text(f"- {r.get('title') or r.get('TI') or 'No title'}")

        st.subheader("Duplicate References (Preview)")
        for r in duplicates[:5]:
            st.text(f"- {r.get('title') or r.get('TI') or 'No title'}")

        # Export options
        fmt = st.selectbox("Export format", ["csv", "bib", "ris", "json"])

        col1, col2 = st.columns(2)

        with col1:
            cleaned = export_references(unique, fmt)
            st.download_button("⬇️ Download Cleaned References", cleaned, f"cleaned.{fmt}")

        with col2:
            dups = export_references(duplicates, fmt)
            st.download_button("⬇️ Download Duplicate References", dups, f"duplicates.{fmt}")
