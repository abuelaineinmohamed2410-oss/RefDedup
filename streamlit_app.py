# streamlit_app.py
import streamlit as st
from dedup import process_uploaded_files, export_to_ris, export_to_bib, export_to_csv, export_to_nbib

st.set_page_config(page_title="RefDedup", layout="centered", page_icon=None)

st.markdown("""
<div style="background:#0B3D91;padding:16px;border-radius:8px;text-align:center;">
  <h1 style="color:white;margin:0;">RefDedup — Duplicate Checker</h1>
  <div style="color:#F6F0E3;margin-top:6px;">Developed by Mohamed Abu Elainein</div>
</div>
""", unsafe_allow_html=True)

st.write("Upload reference files (RIS, NBIB, BibTeX, EndNote XML, CSV, TXT). Multiple files allowed.")

uploaded = st.file_uploader("Select files", type=['ris','nbib','bib','xml','csv','txt'], accept_multiple_files=True)
threshold = st.slider("Similarity threshold (%)", 70, 100, 90, help="Recommended = 90%")

if uploaded:
    st.info("Processing, please wait...")
    kept, dups, total = process_uploaded_files(uploaded, title_threshold_percent=threshold)
    st.success("Done")

    st.write(f"Total parsed records: {total}")
    st.write(f"Kept (unique): {len(kept)}")
    st.write(f"Duplicates found: {len(dups)}")

    st.subheader("Preview — kept (first 10)")
    for r in kept[:10]:
        st.write(r.get('title', '(no title)'))
        if r.get('authors'):
            st.write("  " + "; ".join(r.get('authors')))

    st.subheader("Preview — duplicates (first 10)")
    for r in dups[:10]:
        st.write(r.get('title', '(no title)'), f" — score: {r.get('match_score','') if 'match_score' in r else ''}")

    # downloads
    col1, col2 = st.columns(2)
    with col1:
        fmt_clean = st.selectbox("Format for cleaned file", ['ris','nbib','bib','csv'])
        if st.button("Download cleaned references"):
            if fmt_clean == 'ris':
                st.download_button("Download", export_to_ris(kept), file_name="cleaned.ris", mime="text/plain")
            elif fmt_clean == 'nbib':
                st.download_button("Download", export_to_nbib(kept), file_name="cleaned.nbib", mime="text/plain")
            elif fmt_clean == 'bib':
                st.download_button("Download", export_to_bib(kept), file_name="cleaned.bib", mime="text/plain")
            else:
                st.download_button("Download", export_to_csv(kept), file_name="cleaned.csv", mime="text/csv")
    with col2:
        fmt_dup = st.selectbox("Format for duplicates file", ['ris','nbib','bib','csv'], index=1)
        if st.button("Download duplicates"):
            if fmt_dup == 'ris':
                st.download_button("Download", export_to_ris(dups), file_name="duplicates.ris", mime="text/plain")
            elif fmt_dup == 'nbib':
                st.download_button("Download", export_to_nbib(dups), file_name="duplicates.nbib", mime="text/plain")
            elif fmt_dup == 'bib':
                st.download_button("Download", export_to_bib(dups), file_name="duplicates.bib", mime="text/plain")
            else:
                st.download_button("Download", export_to_csv(dups), file_name="duplicates.csv", mime="text/csv")
