import streamlit as st
import pandas as pd

# Import dedup functions from dedup.py
from dedup import process_uploaded_files, record_to_ris

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
    .stApp { background-color: white; }
    .header-box {
        background-color: #0B3D91;  /* Dark blue */
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .header-box h1 { color: white; margin: 0; }
    .header-box h4 { color: orange; margin: 0; }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- Header ---------------- #
st.markdown(
    """
    <div class="header-box">
        <h1>RefDedup - Duplicate Checker Removal</h1>
        <h4>Developed by Mohamed Abu Elainein</h4>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Upload your RIS or NBIB files below to remove duplicates based on Title, DOI, PMID, and Authors.")

# ---------------- Threshold Slider ---------------- #
similarity = st.slider(
    "Set Similarity Threshold (higher = stricter matching)",
    min_value=70,
    max_value=100,
    value=90,
    step=1
)

# ---------------- File Uploader ---------------- #
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

# ---------------- Processing ---------------- #
if uploaded_files:
    st.info("Processing files... Please wait.")

    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=similarity)

        # Generate cleaned RIS content
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])

        # ---------------- Stats ---------------- #
        st.success("Processing complete!")
        st.write(f"**Total records before deduplication:** {total_before}")
        st.write(f"**Total records after deduplication:** {total_after}")
        st.write(f"**Duplicates removed:** {total_before - total_after} ({round((total_before-total_after)/total_before*100,2)}%)")

        # ---------------- Preview Table ---------------- #
        st.subheader("Preview of Cleaned References")
        preview_df = pd.DataFrame(cleaned_records)
        st.dataframe(preview_df.head(20))  # Show first 20 rows only

        # ---------------- Download Button ---------------- #
        st.download_button(
            label="Download Cleaned RIS File",
            data=cleaned_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

# ---------------- Sidebar ---------------- #
st.sidebar.header("About RefDedup")
st.sidebar.write(
    """
    **RefDedup**  
    Developed by **Mohamed Abu Elainein**  

     Removes duplicate references from **RIS** and **NBIB** files.  
     Matching based on **Title, DOI, PMID, and Authors**.  
     Adjustable similarity threshold for flexible deduplication.  
     Clean and simple interface with stats + preview.  
    """
)
