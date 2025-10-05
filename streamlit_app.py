import streamlit as st
from dedup import process_uploaded_files, record_to_ris

st.set_page_config(page_title="RefDedup", layout="centered")

st.title("RefDedup")
st.subheader("Reference Duplicate Remover for Systematic Reviews")

st.write("Upload your RIS or NBIB files to remove duplicates.")

uploaded_files = st.file_uploader("Upload files", type=["ris", "nbib"], accept_multiple_files=True)

if uploaded_files:
    st.info("Processing files...")
    try:
        cleaned_records, total_before, total_after = process_uploaded_files(uploaded_files)
        output_content = "

".join([record_to_ris(rec) for rec in cleaned_records])
        st.success("Processing complete!")
        st.write(f"Records before: {total_before}")
        st.write(f"Records after: {total_after}")
        st.download_button("Download Cleaned File", data=output_content, file_name="cleaned.ris")
    except Exception as e:
        st.error(f"Error: {e}")

st.sidebar.write("**RefDedup** by Mohamed Abu Elainein")
