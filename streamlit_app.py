import streamlit as st
from dedup import parse_file, deduplicate, export_references

st.set_page_config(page_title="Reference Deduplicator", layout="wide")

st.title("Reference Deduplicator")
st.markdown("Upload your exported reference files (RIS, NBIB, BibTeX, EndNote XML, CSV, TXT).")

uploaded_files = st.file_uploader(
    "Upload one or more files", 
    type=["ris", "nbib", "bib", "xml", "csv", "txt"],
    accept_multiple_files=True
)

threshold = st.slider("Similarity threshold (%)", 70, 100, 90)
st.caption("Recommended: 90% (balanced). Lower = more aggressive, higher = stricter.")

if uploaded_files:
    all_records = []
    for file in uploaded_files:
        try:
            records = parse_file(file)
            all_records.extend(records)
        except Exception as e:
            st.error(f"Could not parse {file.name}: {e}")

    if all_records:
        unique, duplicates = deduplicate(all_records, threshold / 100.0)

        st.subheader("Unique References (Cleaned Preview)")
        for r in unique[:10]:
            st.write("- " + r.get("title", "Untitled"))
        if len(unique) > 10:
            st.write(f"... and {len(unique) - 10} more")

        st.subheader("Duplicate References (Preview)")
        for r in duplicates[:10]:
            st.write("- " + r.get("title", "Untitled"))
        if len(duplicates) > 10:
            st.write(f"... and {len(duplicates) - 10} more")

        fmt = st.selectbox("Export format", ["csv", "ris", "bib", "nbib", "json"])

        if st.button("Export Cleaned & Duplicates"):
            cleaned_bytes = export_references(unique, fmt)
            dups_bytes = export_references(duplicates, fmt)

            st.download_button(
                "Download Unique References",
                cleaned_bytes,
                file_name=f"unique_references.{fmt}"
            )
            st.download_button(
                "Download Duplicate References",
                dups_bytes,
                file_name=f"duplicate_references.{fmt}"
            )
