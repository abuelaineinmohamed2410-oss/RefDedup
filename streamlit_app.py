import streamlit as st
from depup import process_uploaded_files, record_to_ris

st.set_page_config(
    page_title="RefDedup - Duplicate Removal",
    page_icon="logo.png",
    layout="wide"
)

st.title("RefDedup - Duplicate Checker Removal")
st.caption("Developed by Mohamed Abu Elainein")

st.write("Upload your RIS or NBIB files below to remove duplicates based on title, DOI, and PMID.")

uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

title_threshold = st.slider("Title similarity threshold (%)", 70, 100, 90)

if uploaded_files:
    st.info("Processing files... This may take a few seconds.")
    cleaned_records, total_before, total_after = process_uploaded_files(
        uploaded_files, title_threshold=title_threshold
    )
    
    # Save to .ris file
    cleaned_text = "\n\n".join([record_to_ris(r) for r in cleaned_records])
    st.success("Processing complete!")
    st.write(f"Total records before deduplication: {total_before}")
    st.write(f"Total records after deduplication: {total_after}")

    st.download_button(
        "Download cleaned RIS file",
        data=cleaned_text,
        file_name="cleaned_references.ris",
        mime="text/plain"
    )
