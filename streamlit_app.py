# streamlit_app.py
import streamlit as st
from dedup import process_uploaded_files, export_to_ris, export_to_bib, export_to_csv, export_to_nbib, record_to_ris
# record_to_ris is not defined in dedup; we'll use dedup.export_to_ris instead for downloads
from dedup import export_to_ris as dedup_export_ris
from dedup import export_to_bib as dedup_export_bib
from dedup import export_to_csv as dedup_export_csv
from dedup import export_to_nbib as dedup_export_nbib

st.set_page_config(page_title="RefDedup - Duplicate Removal",
                   page_icon="logo.png",
                   layout="centered")

# ---- Styles ----
st.markdown("""
<style>
.stApp { background-color: white; }
.header-box {
    background-color: #0B3D91;
    padding: 18px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 18px;
}
.header-box h1 { color: white; margin: 0; font-size: 26px; }
.header-box h4 { color: #F6F0E3; margin: 4px 0 0 0; font-size: 14px; font-weight: normal; }
.controls-row { display:flex; gap:10px; align-items:center; }
.stats { background:#f8f9fa; padding:12px; border-radius:8px; border:1px solid #e6e6e6; margin-bottom:12px; }
.small-muted { color:#6c757d; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("""
<div class="header-box">
  <h1>RefDedup — Duplicate Checker</h1>
  <h4>Developed by Mohamed Abu Elainein</h4>
</div>
""", unsafe_allow_html=True)

st.write("Upload one or more reference files (RIS, NBIB, BibTeX, EndNote XML, CSV).")
st.write("Recommended deduplication threshold: **90%** (balanced). Lower = more aggressive, Higher = stricter.")

# ---- Upload & Controls ----
uploaded_files = st.file_uploader("Upload reference files", accept_multiple_files=True,
                                  type=['ris', 'nbib', 'bib', 'xml', 'csv', 'txt'])

threshold = st.slider("Similarity threshold (%)", 70, 100, 90, help="Title similarity threshold (recommended 90%).")

process_button = st.button("Process files")

if process_button:
    if not uploaded_files:
        st.warning("Please upload at least one reference file.")
    else:
        with st.spinner("Parsing and deduplicating..."):
            kept, duplicates, total_count = process_uploaded_files(uploaded_files, title_threshold=threshold)

        st.success("Done processing.")
        st.markdown(f"<div class='stats'>Total imported records: <b>{total_count}</b><br>"
                    f"Unique (kept): <b>{len(kept)}</b><br>"
                    f"Duplicates found: <b>{len(duplicates)}</b></div>", unsafe_allow_html=True)

        # download formats selection
        col1, col2 = st.columns(2)
        with col1:
            fmt_clean = st.selectbox("Export cleaned as", options=['ris', 'nbib', 'bib', 'csv'], index=0)
            if fmt_clean == 'ris':
                data_clean = dedup_export_ris(kept)
                mime = "text/plain"
                fname_clean = "cleaned_references.ris"
            elif fmt_clean == 'nbib':
                data_clean = dedup_export_nbib(kept)
                mime = "text/plain"
                fname_clean = "cleaned_references.nbib"
            elif fmt_clean == 'bib':
                data_clean = dedup_export_bib(kept)
                mime = "text/plain"
                fname_clean = "cleaned_references.bib"
            else:
                data_clean = dedup_export_csv(kept)
                mime = "text/csv"
                fname_clean = "cleaned_references.csv"

            st.download_button("Download cleaned file", data=data_clean, file_name=fname_clean, mime=mime)

        with col2:
            fmt_dup = st.selectbox("Export duplicates as", options=['ris', 'nbib', 'bib', 'csv'], index=0)
            if fmt_dup == 'ris':
                data_dup = dedup_export_ris(duplicates)
                mime2 = "text/plain"
                fname_dup = "duplicates.ris"
            elif fmt_dup == 'nbib':
                data_dup = dedup_export_nbib(duplicates)
                mime2 = "text/plain"
                fname_dup = "duplicates.nbib"
            elif fmt_dup == 'bib':
                data_dup = dedup_export_bib(duplicates)
                mime2 = "text/plain"
                fname_dup = "duplicates.bib"
            else:
                data_dup = dedup_export_csv(duplicates)
                mime2 = "text/csv"
                fname_dup = "duplicates.csv"

            st.download_button("Download duplicates file", data=data_dup, file_name=fname_dup, mime=mime2)

        # preview panels
        st.subheader("Preview — Kept (first 20)")
        for r in kept[:20]:
            title = r.get('title') or '(no title)'
            authors = "; ".join(r.get('authors') or [])
            st.markdown(f"**{title}**  \n{authors}  \n<small class='small-muted'>{r.get('year') or ''} | DOI: {r.get('doi') or ''} | PMID: {r.get('pmid') or ''}</small>", unsafe_allow_html=True)

        st.subheader("Preview — Duplicates (first 20)")
        for r in duplicates[:20]:
            title = r.get('title') or '(no title)'
            authors = "; ".join(r.get('authors') or [])
            score = r.get('match_score', '')
            st.markdown(f"**{title}**  \n{authors}  \n<small class='small-muted'>Matched score: {score}</small>", unsafe_allow_html=True)

        # search
        with st.expander("Search kept references"):
            q = st.text_input("Search (title/DOI/PMID/author):")
            if q:
                ql = q.lower().strip()
                found = []
                for r in kept:
                    txt = " ".join([
                        str(r.get('title') or ''),
                        "; ".join(r.get('authors') or []),
                        str(r.get('doi') or ''),
                        str(r.get('pmid') or '')
                    ]).lower()
                    if ql in txt:
                        found.append(r)
                st.write(f"Found {len(found)} matching records")
                for r in found[:200]:
                    st.write(r.get('title') or '')
