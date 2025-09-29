import streamlit as st
from dedup import process_uploaded_files, record_to_ris

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker Removal",
    page_icon="logo.png",  # Professional logo in repo root
    layout="centered"
)

# ---------------- Custom CSS for Dark Blue Theme ---------------- #
st.markdown(
    """
    <style>
    /* Main background */
    .stApp {
        background-color: #0D1B2A;
        color: #E0E1DD;
        font-family: 'Arial', sans-serif;
    }

    /* Sidebar */
    .css-1d391kg { 
        background-color: #1B263B;
        color: #E0E1DD;
    }

    /* Headings */
    .css-10trblm { 
        color: #E0E1DD;
    }

    /* File uploader button */
    .stButton>button {
        background-color: #415A77;
        color: #E0E1DD;
        border-radius: 5px;
        height: 40px;
        width: 250px;
    }

    /* Success messages */
    .stSuccess {
        background-color: #1B263B;
        color: #A5BECC;
    }

    /* Info messages */
    .stInfo {
        background-color: #1B263B;
        color: #A5BECC;
    }

    /* Download button */
    .stDownloadButton>button {
        background-color: #778DA9;
        color: #E0E1DD;
        border-radius: 5px;
        height: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
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
