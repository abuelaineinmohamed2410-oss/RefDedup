# streamlit_app.py
import streamlit as st
from dedup import process_files, record_to_ris
import tempfile
import os

st.title("📚 Reference Deduplication Tool")

uploaded_files = st.file_uploader(
    "Upload .nbib or .ris files", 
    type=["nbib", "ris"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} files")

    # Save uploaded files temporarily
    temp_files = []
    for uf in uploaded_files:
        temp_path = os.path.join(tempfile.gettempdir(), uf.name)
        with open(temp_path, "wb") as f:
            f.write(uf.getbuffer())
        temp_files.append(temp_path)

    if st.button("Remove Duplicates"):
        file_counts, total_before, total_after, cleaned_records = process_files(temp_files)

        st.subheader("📊 Results")
        st.write("Per-file record counts:")
        for k, v in file_counts.items():
            st.write(f"- {k}: {v} records")

        st.write(f"**Total records before:** {total_before}")
        st.write(f"**Total records after:** {total_after}")
        st.write(f"**Duplicates removed:** {total_before - total_after}")

        # Export cleaned RIS
        ris_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
        st.download_button(
            "⬇️ Download Cleaned RIS",
            ris_content,
            "cleaned_references.ris",
            "text/plain"
        )
