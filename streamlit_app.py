import streamlit as st
from dedup import parse_nbib, parse_ris, remove_duplicates, record_to_ris
import io

# ---------------- Streamlit Interface ---------------- #
st.markdown("<h1 style='text-align: center;'>Reference Deduplicator</h1>", unsafe_allow_html=True)
st.write("Upload your **NBIB** or **RIS** files and this tool will automatically remove duplicates. "
         "Designed for systematic reviews and meta-analysis workflows.")

uploaded_files = st.file_uploader("Upload your reference files", type=["nbib", "ris"], accept_multiple_files=True)

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
        st.success(f"Total records uploaded: {len(all_records)}")

        cleaned_records = remove_duplicates(all_records, title_threshold=90)
        st.info(f"Total records after removing duplicates: {len(cleaned_records)}")

        # Convert cleaned records to RIS format
        ris_output = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
        ris_bytes = io.BytesIO(ris_output.encode("utf-8"))

        st.download_button(
            label="Download Cleaned References",
            data=ris_bytes,
            file_name="cleaned_references.ris",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("<p style='text-align: center;'>Developed by <b>Mohamed Abu Elainien</b></p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>GitHub: "
            "<a href='https://github.com/abuelaineinmohamed2410-oss' target='_blank'>RefDedup</a></p>",
            unsafe_allow_html=True)
