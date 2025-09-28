import streamlit as st
from dedup import parse_ris, parse_nbib, remove_duplicates, record_to_ris
import os

st.set_page_config(page_title="RefDedup", layout="wide")

st.title("RefDedup: Duplicate Reference Remover")
st.markdown("""
RefDedup is a Python-powered app for detecting and removing duplicate references in RIS/NBIB files.
Developed by **Mohamed Abu Elainein**.
""")

st.write("Upload one or more `.ris` or `.nbib` files to remove duplicates automatically.")

uploaded_files = st.file_uploader(
    "Choose RIS or NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

if uploaded_files:
    all_records = []
    file_info = []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        if filename.lower().endswith(".ris"):
            records = parse_ris(uploaded_file)
        else:
            records = parse_nbib(uploaded_file)

        all_records.extend(records)
        file_info.append(f"{filename}: {len(records)} records")

    st.subheader("Uploaded Files Summary")
    st.write("\n".join(file_info))

    # Remove duplicates (fixed 90% similarity)
    cleaned_records = remove_duplicates(all_records, title_threshold=90)

    st.subheader("Deduplication Result")
    st.write(f"Total records before deduplication: {len(all_records)}")
    st.write(f"Total unique records after deduplication: {len(cleaned_records)}")

    # Prepare file for download
    output_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
    st.download_button(
        label="Download Cleaned RIS",
        data=output_content,
        file_name="cleaned_references.ris",
        mime="text/plain"
    )

st.markdown("---")
st.markdown("Developed by **Mohamed Abu Elainein** | RefDedup V1")
