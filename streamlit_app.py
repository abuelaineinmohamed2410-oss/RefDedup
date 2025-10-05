import streamlit as st
from dedup import process_uploaded_files, record_to_ris

st.set_page_config(
    page_title="RefDedup - Duplicate Removal for SR",
    page_icon=None,
    layout="centered"
)

# Style (no icons/AI; simple, professional)
st.markdown(
    """
    <style>
    .stApp { background: #fff; }
    .header { background-color: #1a3d76; padding: 18px 0; border-radius: 8px; text-align:center; }
    .header h1 { color: white; font-size: 2.2em; margin-bottom: 7px; }
    .header h4 { color: #FFA000; margin-top: 0; }
    .stText, .stMarkdown, .stTable { color: #111; }
    </style>
    """, unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='header'>
        <h1>RefDedup</h1>
        <h4>Reference Duplicate Remover for Systematic Reviews</h4>
    </div>
    """, unsafe_allow_html=True
)

st.write(
    "Upload your **RIS** or **NBIB** files below. RefDedup removes near-duplicate references based on Title, DOI, and PMID, streamlining the initial screening for systematic reviews."
)

uploaded_files = st.file_uploader(
    "Upload files (.ris, .nbib)",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Removing duplicates..."):
        try:
            cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files, title_threshold=91)
            cleaned_content = "

".join([record_to_ris(rec) for rec in cleaned_records])
            st.success("Deduplication completed.")
            st.write(f"Total records uploaded: **{total_before}**")
            st.write(f"Total unique references: **{total_after}**")
            st.download_button(
                label="Download Cleaned RIS",
                data=cleaned_content,
                file_name="deduplicated_references.ris",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f"Error during deduplication: {e}")

st.sidebar.header("About")
st.sidebar.write(
    """
    **RefDedup**  
    Created by Mohamed Abu Elainein

    Removes duplicates from RIS and NBIB files  
    using Titles, DOIs and PMIDs.
    """
)
