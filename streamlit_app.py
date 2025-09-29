import streamlit as st
from depup import process_uploaded_files, record_to_ris

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker Removal",
    page_icon="logo.png",
    layout="centered"
)

# ---------------- Custom CSS ---------------- #
st.markdown(
    """
    <style>
    /* Set main page background to white */
    .stApp {
        background-color: #FFFFFF;
        color: #000000;
        font-family: 'Arial', sans-serif;
    }

    /* Dark blue cards/rectangles */
    .dark-blue-card {
        background-color: #0B1D3F;
        padding: 20px;
        border-radius: 10px;
        color: #FFFFFF;
        margin-bottom: 20px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #0B1D3F;
        color: #FFFFFF;
        border-radius: 5px;
        height: 40px;
        width: 250px;
    }

    .stDownloadButton>button {
        background-color: #1F4E79;
        color: #FFFFFF;
        border-radius: 5px;
        height: 40px;
    }

    /* File uploader text */
    .stFileUploader>div>div>div>div {
        color: #000000;
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

# Dark blue section for file upload
with st.container():
    st.markdown('<div class="dark-blue-card">', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload RIS/NBIB files", 
        type=["ris", "nbib"], 
        accept_multiple_files=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Process files
if uploaded_files:
    st.info("Processing files... This may take a few seconds.")

    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=90)

        # Generate cleaned RIS content
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])

        # Dark blue section for download
        with st.container():
            st.markdown('<div class="dark-blue-card">', unsafe_allow_html=True)
            st.success("Processing complete!")
            st.write(f"**Total records before deduplication:** {total_before}")
            st.write(f"**Total records after deduplication:** {total_after}")

            st.download_button(
                label="Download Cleaned RIS File",
                data=cleaned_content,
                file_name="cleaned_references.ris",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
