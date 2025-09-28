import streamlit as st
from dedup import parse_nbib, parse_ris, remove_duplicates, record_to_ris
import io

# ---------------- Page Config ---------------- #
st.set_page_config(
    page_title="RefDedup - Reference Deduplicator",
    page_icon=None,
    layout="centered"
)

# ---------------- Header ---------------- #
st.markdown(
    """
    <div style='text-align: center; padding: 20px; background-color: #2C3E50; border-radius: 10px;'>
        <h1 style='color: #ECF0F1; margin-bottom: 10px;'>RefDedup</h1>
        <h3 style='color: #BDC3C7;'>Smart Reference Deduplication Tool</h3>
        <p style='color: #95A5A6;'>Upload your RIS / NBIB files. Designed for systematic reviews and meta-analysis workflows.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- File Upload ---------------- #
uploaded_files = st.file_uploader(
    "📂 Upload your reference files",
    type=["nbib", "ris"],
    accept_multiple_files=True
)

# ---------------- Processing ---------------- #
if uploaded_files:
    all_records = []

    for file in uploaded_files:
        if file.name.lower().endswith(".nbib"):
            records = parse_nbib(file)
        elif file.name.lower().endswith(".ris"):
            records = parse_ris(file)
        else:
            records = []
        all_records.extend(records)

    if all_records:
        st.markdown(
            f"<div style='padding: 15px; background-color: #27AE60; color: white; border-radius: 8px;'>"
            f"✅ Total records uploaded: <b>{len(all_records)}</b></div>",
            unsafe_allow_html=True
        )

        cleaned_records = remove_duplicates(all_records, title_threshold=90)

        st.markdown(
            f"<div style='padding: 15px; background-color: #2980B9; color: white; border-radius: 8px;'>"
            f"📊 Total records after removing duplicates: <b>{len(cleaned_records)}</b></div>",
            unsafe_allow_html=True
        )

        # Convert cleaned records to RIS format
        ris_output = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
        ris_bytes = io.BytesIO(ris_output.encode("utf-8"))

        st.download_button(
            label="⬇️ Download Cleaned References",
            data=ris_bytes,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

# ---------------- Footer ---------------- #
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 10px;'>
        <p style='color: #7F8C8D; font-size: 14px;'>
        Developed by <b>Mohamed Abu Elainein</b><br>
        <a href='https://github.com/abuelaineinmohamed2410-oss' target='_blank' style='color: #2980B9;'>
        GitHub Repository</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
