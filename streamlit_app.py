import streamlit as st
from dedup import parse_file, deduplicate, export_references

st.title("📚 Reference Deduplicator")

uploaded_files = st.file_uploader("Upload reference files (.bib, .ris, .nbib, .csv)", type=["bib","ris","nbib","csv"], accept_multiple_files=True)

threshold = st.slider("Deduplication similarity threshold", 0.5, 1.0, 0.85)

if uploaded_files:
    records = []
    for f in uploaded_files:
        records.extend(parse_file(f))

    unique, duplicates = deduplicate(records, threshold)

    st.success(f"✅ Found {len(unique)} unique references and {len(duplicates)} duplicates.")

    # Preview unique references
    st.subheader("Unique References (cleaned)")
    st.write(unique[:10])  # show preview

    # Export options
    fmt = st.selectbox("Export format", ["bib", "csv", "json"])
    if st.button("Export Cleaned References"):
        cleaned = export_references(unique, fmt)
        st.download_button("Download Cleaned", cleaned, f"cleaned.{fmt}")
    if st.button("Export Duplicates"):
        dups = export_references(duplicates, fmt)
        st.download_button("Download Duplicates", dups, f"duplicates.{fmt}")
