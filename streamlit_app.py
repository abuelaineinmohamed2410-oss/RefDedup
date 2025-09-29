import streamlit as st
from depup import process_uploaded_files, record_to_ris

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker",
    page_icon="logo.png",  # Ensure logo.png is in repo root
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
st.markdown("<h1 style='text-align: center; color: #0F4C81;'>RefDedup - Duplicate Checker Removal</h1>", unsafe_allow_html=True)
st.write("Upload your RIS or NBIB files below to remove duplicates based on title, DOI, PMID, and authors.")

# File uploader
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files", 
    type=["ris", "nbib"], 
    accept_multiple_files=True
)

# Start processing
if uploaded_files:
    st.info("Processing files... Please wait.")
    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=90)
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])

        # Display results
        st.success("Processing complete!")
        st.markdown(f"**Total records before deduplication:** {total_before}")
        st.markdown(f"**Total records after deduplication:** {total_after}")

        # Download button
        st.download_button(
            label="Download Cleaned RIS File",
            data=cleaned_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
