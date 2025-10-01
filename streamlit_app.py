import streamlit as st
from dedup import process_uploaded_files, export_references

st.set_page_config(page_title="Reference Deduplicator", layout="centered")

st.title("Reference Deduplicator")
st.caption("Developed by Mohamed Abu Elainein")

st.markdown("""
Upload one or more reference files (RIS, NBIB, BibTeX, EndNote XML, CSV, TXT).  
**Recommended deduplication threshold: 90%**  
- Lower = more aggressive (may merge different papers)  
- Higher = stricter (may miss near-duplicates)  
""")

uploaded_files = st.file_uploader(
    "Upload reference files",
    type=["ris", "nbib", "bib", "xml", "csv", "txt"],
    accept_multiple_files=True
)

threshold = st.slider("Similarity threshold (%)", 70, 100, 90)

if uploaded_files:
    kept, duplicates, total_count = process_uploaded_files(uploaded_files, threshold/100)

    st.success(f"Processed {total_count} references. "
               f"Kept {len(kept)} unique, found {len(duplicates)} duplicates.")

    st.subheader("Preview of Cleaned References")
    st.write(kept[:10])  

    st.subheader("Preview of Duplicates Removed")
    st.write(duplicates[:10])  

    st.download_button("⬇ Download Cleaned (RIS)", export_references(kept, "ris"), "cleaned_references.ris")
    st.download_button("⬇ Download Duplicates (RIS)", export_references(duplicates, "ris"), "duplicates.ris")

    st.download_button("⬇ Download Cleaned (NBIB)", export_references(kept, "nbib"), "cleaned_references.nbib")
    st.download_button("⬇ Download Duplicates (NBIB)", export_references(duplicates, "nbib"), "duplicates.nbib")

    st.download_button("⬇ Download Cleaned (BibTeX)", export_references(kept, "bib"), "cleaned_references.bib")
    st.download_button("⬇ Download Duplicates (BibTeX)", export_references(duplicates, "bib"), "duplicates.bib")

    st.download_button("⬇ Download Cleaned (CSV)", export_references(kept, "csv"), "cleaned_references.csv")
    st.download_button("⬇ Download Duplicates (CSV)", export_references(duplicates, "csv"), "duplicates.csv")
