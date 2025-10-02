import streamlit as st
from io import StringIO
from pathlib import Path
from dedup import process_uploaded_files, record_to_ris

# Page config & style
st.set_page_config(page_title="RefDedup", page_icon="📚", layout="centered")
st.markdown("""
<style>
.stApp { background-color: white; }
.header-box {
    background-color: #0B3D91;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
.header-box h1 { color: white; margin: 0; }
.header-box h4 { color: orange; margin: 0; }
.stText, .stMarkdown { color: black; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <h1>RefDedup - Duplicate Checker Removal</h1>
    <h4>Developed by Mohamed Abu Elainein</h4>
</div>
""", unsafe_allow_html=True)

st.write("Upload your RIS, NBIB, BIB, or CSV files to remove duplicates based on Title, DOI, PMID, and Authors.")

uploaded_files = st.file_uploader(
    "Upload bibliographic files",
    type=["ris", "nbib", "bib", "csv"],
    accept_multiple_files=True
)

title_threshold = st.slider("Title similarity threshold (%)", min_value=80, max_value=99, value=90, step=1)

if uploaded_files:
    st.info("Processing files... Please wait.")

    try:
        cleaned_records, duplicate_records, total_before, total_after = process_uploaded_files(
            uploaded_files, title_threshold=title_threshold
        )

        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
        duplicate_content = "\n\n".join([record_to_ris(rec) for rec in duplicate_records])

        st.success("Processing complete!")
        st.write(f"**Total records before deduplication:** {total_before}")
        st.write(f"**Total records after deduplication:** {total_after}")
        st.write(f"**Duplicates found:** {len(duplicate_records)}")

        st.download_button(
            label="Download Cleaned RIS File",
            data=cleaned_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

        if duplicate_records:
            st.download_button(
                label="Download Duplicate RIS File",
                data=duplicate_content,
                file_name="duplicates.ris",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"Error during processing: {e}")

st.sidebar.header("About RefDedup")
st.sidebar.write("""
**RefDedup**  
Developed by **Mohamed Abu Elainein**  

Remove duplicate references from **RIS**, **NBIB**, **BIB**, and **CSV** files  
using accurate matching on **Title, DOI, PMID, and Authors**.
""")
