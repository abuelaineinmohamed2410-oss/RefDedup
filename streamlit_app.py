import streamlit as st

# Try importing depup.py or dedup.py depending on your repo
try:
    from depup import process_uploaded_files, record_to_ris
except ModuleNotFoundError:
    from dedup import process_uploaded_files, record_to_ris

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker Removal",
    page_icon="logo.png",  # your logo file in repo root
    layout="centered"
)

# ---------------- Custom CSS ---------------- #
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background-color: white;
    }
    /* Header rectangle */
    .header-box {
        background-color: #0B3D91;  /* Dark blue */
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    /* Header text */
    .header-box h1 {
        color: white;
        margin: 0;
    }
    /* Other texts */
    .stText, .stMarkdown {
        color: black;
    }
    </style>
    """, unsafe_allow_html=True
)

# ---------------- Header ---------------- #
st.markdown(
    """
    <div class="header-box">
        <h1>RefDedup - Duplicate Checker Removal</h1>
        <p>Developed by Mohamed Abu Elainein</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Upload your RIS or NBIB files below to remove duplicates based on Title, DOI, PMID, and Authors.")

# ---------------- File Uploader ---------------- #
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

# ---------------- Processing ---------------- #
if uploaded_files:
    st.info("Processing files... This may take a few seconds.")

    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=90)

        # Generate cleaned RIS content
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])

        # Show results
        st.success("Processing complete!")
        st.write(f"**Total records before deduplication:** {total_before}")
        st.write(f"**Total records after deduplication:** {total_after}")

        # Download button
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

    Remove duplicate references from **RIS** and **NBIB** files  
    based on **Title, DOI, PMID, and Authors**.
    """
)
