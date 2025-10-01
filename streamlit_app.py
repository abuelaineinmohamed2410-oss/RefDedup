import streamlit as st
from dedup import parse_file, deduplicate, export_references

st.set_page_config(page_title="RefDedup", layout="centered", page_icon="logo.png")

# ---------- HEADER DESIGN ---------- #
st.markdown("""
    <div style="background-color:#0B3D91;padding:20px;border-radius:10px;text-align:center;">
        <h1 style="color:white;margin:0;">RefDedup - Reference Deduplicator</h1>
        <h4 style="color:orange;margin:0;">Developed by Mohamed Abu Elainein</h4>
    </div>
""", unsafe_allow_html=True)

st.write("Upload reference files below (RIS, NBIB, BibTeX, EndNote XML, CSV, TXT).")

# ---------- FILE UPLOAD ---------- #
uploaded_files = st.file_uploader(
    "Upload reference files",
    type=["ris", "nbib", "bib", "xml", "csv", "txt"],
    accept_multiple_files=True
)

threshold = st.slider("Similarity threshold (%)", 50, 100, 90)

if uploaded_files:
    st.info("Processing files... Please wait.")
    all_records = []
    for f in uploaded_files:
        try:
            all_records.extend(parse_file(f))
        except Exception as e:
            st.error(f"Error reading {f.name}: {e}")

    kept, duplicates, total_count = deduplicate(all_records, threshold=threshold)

    st.success("Deduplication complete!")
    st.write(f"**Total references:** {total_count}")
    st.write(f"**After deduplication:** {len(kept)}")
    st.write(f"**Duplicates found:** {len(duplicates)}")

    # ---------- PREVIEW ---------- #
    st.subheader("Preview (first 5 cleaned references):")
    st.write(kept[:5])

    # ---------- DOWNLOAD BUTTONS ---------- #
    st.download_button(
        "⬇️ Download Cleaned (RIS)", export_references(kept, "ris"), "cleaned_references.ris"
    )
    st.download_button(
        "⬇️ Download Duplicates (RIS)", export_references(duplicates, "ris"), "duplicates.ris"
    )
    st.download_button(
        "⬇️ Download Cleaned (BibTeX)", export_references(kept, "bib"), "cleaned_references.bib"
    )
    st.download_button(
        "⬇️ Download Cleaned (CSV)", export_references(kept, "csv"), "cleaned_references.csv"
    )
    st.download_button(
        "⬇️ Download Cleaned (NBIB)", export_references(kept, "nbib"), "cleaned_references.nbib"
    )

# ---------- SIDEBAR ---------- #
st.sidebar.header("About RefDedup")
st.sidebar.write("""
**RefDedup** removes duplicate references from:
- RIS
- NBIB
- BibTeX
- EndNote XML
- CSV / TXT  

It outputs both **cleaned references** and a file of **duplicates**.  
Recommended threshold: **90%** (balanced).
""")
