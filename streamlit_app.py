import streamlit as st
import os
from dedup import remove_duplicates_from_folder, record_to_ris  # Make sure dedup.py is in the same repo

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker",
    page_icon="logo.png",  # your uploaded logo
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Styles ---------------- #
st.markdown(
    """
    <style>
    body {
        background-color: #f0f4f8;
        color: #0d1b2a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #1d4ed8;
        color: white;
        font-size: 16px;
        height: 50px;
        width: 200px;
        border-radius: 8px;
    }
    .stDownloadButton>button {
        background-color: #2563eb;
        color: white;
        font-size: 16px;
        height: 50px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ---------------- #
st.title("RefDedup - Duplicate Checker Removal")
st.markdown("Developed by **Mohamed Abu Elainein**")
st.markdown("Upload your RIS or NBIB files to remove duplicates based on **Title, DOI, PMID, and Authors**.")

# ---------------- File Uploader ---------------- #
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

# ---------------- Processing ---------------- #
if uploaded_files:
    st.info("Processing files... This may take a few seconds.")
    temp_folder = "temp_uploads"
    os.makedirs(temp_folder, exist_ok=True)
    
    # Save uploaded files to temp folder
    for file in uploaded_files:
        with open(os.path.join(temp_folder, file.name), "wb") as f:
            f.write(file.getbuffer())
    
    # Process duplicates
    cleaned_records, total_before, total_after, output_file = remove_duplicates_from_folder(
        temp_folder, title_threshold=90
    )
    
    st.success("Processing complete!")
    st.markdown(f"**Total records before deduplication:** {total_before}")
    st.markdown(f"**Total records after deduplication:** {total_after}")
    st.markdown(f"**Duplicates removed:** {total_before - total_after}")
    
    # Download button
    with open(output_file, "rb") as f:
        st.download_button(
            label="Download Cleaned RIS File",
            data=f,
            file_name="cleaned_references.ris",
            mime="application/octet-stream"
        )
    
    # Cleanup temp files
    for file in os.listdir(temp_folder):
        os.remove(os.path.join(temp_folder, file))
