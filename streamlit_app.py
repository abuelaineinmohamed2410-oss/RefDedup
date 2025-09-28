import streamlit as st
from dedup import parse_ris, parse_nbib, remove_duplicates, record_to_ris
import os

st.set_page_config(
    page_title="RefDedup",
    page_icon="📚",
    layout="wide",
)

# ------------------- Header ------------------- #
st.markdown(
    """
    <div style="text-align:center; padding:15px; background-color:#2E86C1; border-radius:10px;">
        <h1 style="color:white; margin:0;">RefDedup</h1>
        <p style="color:#D6EAF8; margin:0;">Duplicate Checker for RIS & NBIB Files</p>
        <p style="color:#FAD7A0; margin:0;">Developed by <b>Mohamed Abu Elainein</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ------------------- File Upload ------------------- #
uploaded_files = st.file_uploader(
    "Upload your RIS or NBIB files", type=["ris", "nbib"], accept_multiple_files=True
)

similarity = st.slider("Select similarity threshold for duplicates", 70, 100, 90)

if uploaded_files:
    st.info(f"📂 {len(uploaded_files)} file(s) uploaded. Click below to process.")

    if st.button("🚀 Start Deduplication"):
        all_records = []
        file_counts = {}

        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            if file_name.lower().endswith(".ris"):
                records = parse_ris(uploaded_file)
            elif file_name.lower().endswith(".nbib"):
                records = parse_nbib(uploaded_file)
            else:
                continue

            file_counts[file_name] = len(records)
            all_records.extend(records)

        total_before = len(all_records)
        cleaned = remove_duplicates(all_records, title_threshold=similarity)
        total_after = len(cleaned)

        # Export cleaned RIS
        output_file = "cleaned_references.ris"
        with open(output_file, "w", encoding="utf-8") as f:
            for rec in cleaned:
                f.write(record_to_ris(rec) + "\n\n")

        with open(output_file, "rb") as f:
            st.download_button(
                "⬇️ Download Cleaned References",
                f,
                file_name="cleaned_references.ris",
                mime="application/x-research-info-systems",
            )

        st.success("✅ Deduplication completed successfully!")

        st.subheader("📊 Results")
        st.write("### Per-file record counts:")
        for k, v in file_counts.items():
            st.write(f"- {k}: {v} records")

        st.write(f"**Total records before deduplication:** {total_before}")
        st.write(f"**Total records after deduplication:** {total_after}")

else:
    st.warning("👆 Please upload at least one .ris or .nbib file to begin.")
