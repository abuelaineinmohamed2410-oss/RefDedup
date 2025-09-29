# streamlit_app.py
import streamlit as st
from dedup import process_uploaded_files, record_to_ris
import os

# ------------------- Page Configuration ------------------- #
st.set_page_config(
    page_title="RefDedup - Duplicate Checker",
    page_icon="logo.png", 
    layout="wide"
)

# ------------------- App Title ------------------- #
st.markdown(
    """
    <div style="background-color:#4CAF50;padding:10px;border-radius:10px;">
        <h2 style="color:white;text-align:center;">RefDedup - Duplicate Checker Removal</h2>
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("Developed by **Mohamed Abu Elainein**")

st.write("Upload your RIS or NBIB files below to remove duplicates based on title, DOI, PMID, and authors.")

# ------------------- File Upload ------------------- #
uploaded_files = st.file_uploader(
    "Upload RIS/NBIB files",
    type=['ris', 'nbib'],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("Processing files... This may take a few seconds."):
        try:
            cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files)

            st.success("Processing complete!")
            st.write(f"**Total records before deduplication:** {total_before}")
            st.write(f"**Total records after deduplication:** {total_after}")
            st.write(f"**Duplicates removed:** {total_before - total_after}")

            # Save cleaned file
            output_file = "cleaned_references.ris"
            with open(output_file, "w", encoding="utf-8") as f:
                for rec in cleaned_records:
                    f.write(record_to_ris(rec) + "\n\n")

            st.download_button(
                label="Download Cleaned RIS",
                data=open(output_file, "r", encoding="utf-8").read(),
                file_name=output_file,
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Error processing files: {e}")

# ------------------- Footer ------------------- #
st.markdown(
    """
    <hr>
    <div style="text-align:center;font-size:12px;color:gray;">
        RefDedup - Duplicate Checker Removal | Developed by Mohamed Abu Elainein
    </div>
    """, unsafe_allow_html=True
)
