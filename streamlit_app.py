import streamlit as st
from depup import process_uploaded_files, record_to_ris

# ---------------- Page config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker Removal",
    page_icon="logo.png",  # make sure logo.png is in your repo
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------------- App Title ---------------- #
st.title("RefDedup - Duplicate Checker Removal")
st.markdown("Developed by **Mohamed Abu Elainein**")
st.write(
    "Upload your RIS or NBIB files below to remove duplicates based on title, DOI, PMID, and authors."
)

# ---------------- File uploader ---------------- #
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

# ---------------- Process uploaded files ---------------- #
if uploaded_files:
    st.info("Processing files... This may take a few seconds.")
    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=90)
        
        # Export cleaned RIS
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
        st.success("Processing complete!")
        st.write(f"**Total records before deduplication:** {total_before}")
        st.write(f"**Total records after deduplication:** {total_after}")
        
        st.download_button(
            "Download Cleaned RIS",
            data=cleaned_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

    except Exception as e:
        st.error("An error occurred while processing the files.")
        st.error(str(e))

# ---------------- Sidebar / About ---------------- #
with st.sidebar:
    st.header("About RefDedup")
    st.write(
        "RefDedup is a Python-powered tool for detecting and removing duplicate references "
        "from NBIB and RIS files used in systematic reviews and meta-analysis workflows."
    )
    st.write("Version: 1.0")
    st.write("Developed by Mohamed Abu Elainein")
