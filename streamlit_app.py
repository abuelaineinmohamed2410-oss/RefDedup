# streamlit_app.py
import streamlit as st
from io import BytesIO
from dedup import process_uploaded_files

st.set_page_config(page_title="RefDedup", layout="centered")
st.title("📚 RefDedup — Duplicate Reference Remover")

st.markdown("Upload one or more `.ris` or `.nbib` files. The app will merge and deduplicate them and let you download a cleaned `.ris` file.")

# Options
threshold = st.slider("Title similarity threshold (higher = stricter)", 80, 100, 90)
use_author_year = st.checkbox("Require first author + year match for fuzzy-title duplicates (recommended)", value=True)

uploaded = st.file_uploader("Upload RIS/NBIB files", type=["ris", "nbib"], accept_multiple_files=True)

progress_bar = st.progress(0)
status = st.empty()

if st.button("Run deduplication") and uploaded:
    # prepare uploaded files list in the form expected by dedup.process_uploaded_files
    status.info("Reading files...")
    progress_bar.progress(5)
    files = uploaded  # streamlit UploadedFile objects are accepted by dedup.process_uploaded_files

    # progress callback updates Streamlit progress and status text
    def progress_cb(percent, message=""):
        try:
            progress_bar.progress(min(max(int(percent),0),100))
        except Exception:
            pass
        if message:
            status.text(message)

    status.text("Starting processing...")
    ris_text, file_counts, total_before, total_after = process_uploaded_files(files, title_threshold=threshold, use_author_year=use_author_year, progress_callback=progress_cb)
    progress_bar.progress(100)
    status.success("Processing complete!")

    # show results
    st.subheader("Results")
    st.write(f"Files processed: {len(file_counts)}")
    for name, cnt in file_counts.items():
        st.write(f"- **{name}**: {cnt} records")
    st.write(f"**Total before**: {total_before}")
    st.write(f"**Total after**: {total_after}")
    st.write(f"**Duplicates removed**: {total_before - total_after}")

    # download button
    st.download_button("Download cleaned RIS", data=ris_text, file_name="cleaned_references.ris", mime="text/plain")
elif st.button("Run deduplication") and not uploaded:
    st.warning("Please upload at least one .ris or .nbib file first.")
