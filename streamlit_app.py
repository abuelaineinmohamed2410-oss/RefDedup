import streamlit as st
from pathlib import Path
import tempfile

# Import your duplicate detection class (assuming it's in the same directory)
from bibliographic_duplicate_detector import BibliographicDuplicateDetector

st.set_page_config(
    page_title="BiblioDedupe - Streamlit",
    layout="wide",
    page_icon="📚"
)

st.title("📚 BiblioDedupe: Bibliographic Duplicate Detection")
st.markdown(
    "Upload your bibliographic files (RIS, BIB, CSV, NBIB) to detect and remove duplicate references. "
)

uploaded_files = st.file_uploader(
    "Upload files",
    type=["ris", "bib", "csv", "nbib", "txt"],
    accept_multiple_files=True,
    help="You can upload multiple files from different sources."
)

threshold = st.slider(
    "Title similarity threshold", 0.80, 1.00, 0.95, 0.01,
    help="Lower threshold detects more duplicates, higher is stricter."
)

if st.button("Run Duplicate Detection") and uploaded_files:
    with st.spinner("Processing files..."):
        # Save uploaded files to temp files for processing
        file_paths = []
        for uploaded in uploaded_files:
            suffix = Path(uploaded.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmpf:
                tmpf.write(uploaded.read())
                file_paths.append(tmpf.name)

        # Instantiate and run the detector
