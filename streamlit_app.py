import streamlit as st
from dedup import process_uploaded_files, record_to_ris  # Fixed import

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker Removal",
    page_icon="logo.png",  # Your professional logo in repo root
    layout="centered"
)

# ---------------- Sidebar ---------------- #
st.sidebar.header("About RefDedup")
st.sidebar.write(
    """
    **RefDedup**  
    Developed by **Mohamed Abu Elainein**  

    Remove duplicate references from **RIS** and **NBIB** files  
    based on **Title, DOI, PMID, and Authors**.
    """
)

# ---------------- Main Page ---------------- #
st.title("RefDedup - Duplicate Checker Removal")
st.write("Upload your RIS or NBIB files below to remove duplicates.")

# File uploader
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files", 
    type=["ris", "nbib"], 
    accept_multiple_files=True
)

# Start processing
if uploaded_files:
    st.info("Processing files... This may take a few seconds.")

    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=90)

        # Generate cleaned RIS content
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])

        # Download link
        st.success("Processing complete!")
        st.write(f"**Total records before deduplication:** {total_before}")
        st.write(f"**Total records after deduplication:** {total_after}")

        st.download_button(
            label="Download Cleaned RIS File",
            data=cleaned_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
