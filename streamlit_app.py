import streamlit as st
from dedup import process_uploaded_files, record_to_ris

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup",
    page_icon="logo.png",  # or "assets/logo.png" if in assets folder
    layout="wide"
)



# ---------------- Header ---------------- #
st.markdown(
    """
    <div style="background-color:#004080;padding:15px;border-radius:10px">
        <h1 style="color:white;text-align:center;">RefDedup: Duplicate Checker Removal</h1>
        <p style="color:white;text-align:center;">Pre Release Version</p>
    </div>
    """, unsafe_allow_html=True
)

st.write("---")

# ---------------- Upload Section ---------------- #
st.markdown("### Upload Your RIS or NBIB Files")
uploaded_files = st.file_uploader(
    "Select RIS or NBIB files", 
    type=['ris', 'nbib'], 
    accept_multiple_files=True
)

# Display uploaded files
if uploaded_files:
    st.markdown("#### Uploaded Files")
    for file in uploaded_files:
        st.write(f"- {file.name}")

# ---------------- Deduplication Section ---------------- #
if st.button("Start Deduplication"):
    if not uploaded_files:
        st.warning("Please upload at least one RIS or NBIB file first.")
    else:
        st.info("Processing files... This may take a few seconds.")
        
        # Process files with hardcoded 90% similarity threshold
        cleaned_records, total_before, total_after = process_uploaded_files(
            uploaded_files, title_threshold=90
        )
        
        st.success("Deduplication Complete!")
        st.markdown(f"**Total Records Before:** {total_before}")
        st.markdown(f"**Total Records After:** {total_after}")
        st.markdown(f"**Duplicates Removed:** {total_before - total_after}")

        # ---------------- Download Cleaned RIS ---------------- #
        ris_content = "\n\n".join([record_to_ris(r) for r in cleaned_records])
        st.download_button(
            label="Download Cleaned RIS",
            data=ris_content,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

# ---------------- Footer ---------------- #
st.markdown(
    """
    <div style="background-color:#004080;padding:10px;border-radius:10px;margin-top:20px;">
        <p style="color:white;text-align:center;">
            RefDedup &copy; 2025 | Developed by Mohamed Abu Elainein
        </p>
    </div>
    """, unsafe_allow_html=True
)
