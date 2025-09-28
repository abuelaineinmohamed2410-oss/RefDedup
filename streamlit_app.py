```python
import streamlit as st
from dedup import parse_ris, parse_nbib, process_files

st.set_page_config(
    page_title="RefDedup",
    page_icon="📑",
    layout="centered",
)

# App header
st.markdown(
    """
    <h1 style='text-align: center; color: #2c3e50;'>RefDedup</h1>
    <p style='text-align: center; font-size:18px; color:#34495e;'>
    A tool for detecting and removing duplicate references in RIS/NBIB files.<br>
    Developed by <b>Mohamed Abu Elainein</b>
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# Upload files
uploaded_files = st.file_uploader(
    "Upload one or more RIS/NBIB files",
    type=["ris", "nbib"],
    accept_multiple_files=True
)

if uploaded_files:
    try:
        # Process uploaded files
        records, unique_records, duplicates = process_files(uploaded_files)

        # Display results
        st.success("Processing complete!")
        st.write(f"**Total records:** {len(records)}")
        st.write(f"**Duplicates detected:** {len(duplicates)}")
        st.write(f"**Unique references:** {len(unique_records)}")

        # Export results
        st.download_button(
            label="Download Deduplicated File",
            data="\n".join(unique_records),
            file_name="deduplicated_output.ris",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"An error occurred while processing: {e}")
```
