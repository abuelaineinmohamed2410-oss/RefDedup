import streamlit as st
from dedup import process_uploaded_files, record_to_ris

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Removal",
    page_icon="logo.png",
    layout="centered"
)

# ---------------- Custom CSS ---------------- #
st.markdown(
    """
    <style>
    .stApp { background-color: white; }
    .header-box {
        background-color: #0B3D91;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .header-box h1 { color: white; margin: 0; font-size: 28px; }
    .header-box h4 { color: orange; margin: 0; font-size: 16px; }
    .stats-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ---------------- #
st.markdown(
    """
    <div class="header-box">
        <h1>RefDedup - Duplicate Checker</h1>
        <h4>Developed by Mohamed Abu Elainein</h4>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Upload your RIS or NBIB files below to remove duplicates based on **Title, DOI, PMID, and Authors**.")

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
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=90)

        # Generate cleaned RIS content
        cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])

        # ---------------- Stats ---------------- #
        st.markdown(
            f"""
            <div class="stats-box">
                <b>Total records before:</b> {total_before}  
                <br><b>Total records after:</b> {total_after}  
                <br><b>Duplicates removed:</b> {total_before - total_after}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------- Download Button ---------------- #
        st.download_button(
            label="⬇️ Download Cleaned RIS File",
            data=cleaned_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

        # ---------------- Search / Preview ---------------- #
        with st.expander("🔍 Preview & Search Cleaned References"):
            search_term = st.text_input("Search by title/DOI/PMID/author:")
            if search_term:
                filtered = [r for r in cleaned_records if search_term.lower() in record_to_ris(r).lower()]
            else:
                filtered = cleaned_records[:50]  # show first 50 if no search

            st.write(f"Showing {len(filtered)} references (out of {len(cleaned_records)})")
            for rec in filtered:
                st.text(record_to_ris(rec))

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

# ---------------- Sidebar ---------------- #
st.sidebar.header("About RefDedup")
st.sidebar.write(
    """
    **RefDedup**  
    Developed by **Mohamed Abu Elainein**  

    ✔ Remove duplicates from **RIS/NBIB** files  
    ✔ Based on **Title, DOI, PMID, Authors**  
    ✔ Simple, accurate & transparent  
    """
)
