import streamlit as st
import pandas as pd
from dedup import process_uploaded_files, record_to_ris
import time

# Page configuration
st.set_page_config(
    page_title="RefDedup - Reference Duplicate Remover",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CLEAN THEME - PERFECT CONTRAST EVERYWHERE
st.markdown("""
    <style>
    /* Clean color system */
    :root {
        --white: #ffffff;
        --light-gray: #f5f5f5;
        --medium-gray: #e0e0e0;
        --dark-gray: #333333;
        --black: #000000;
        --blue: #0066cc;
        --green: #28a745;
        --red: #dc3545;
        --orange: #ff9800;
    }
    
    /* MAIN APP: WHITE background, BLACK text */
    .stApp {
        background-color: var(--white) !important;
        color: var(--black) !important;
    }
    
    /* SIDEBAR: DARK background, WHITE text */
    section[data-testid="stSidebar"] {
        background-color: var(--dark-gray) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--white) !important;
    }
    
    /* HEADERS: BLACK text on WHITE background */
    .main-header {
        font-size: 2.5rem;
        color: var(--black) !important;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: var(--black) !important;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 1.2rem;
        color: var(--black) !important;
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 2px solid var(--medium-gray);
        padding-bottom: 0.5rem;
    }
    
    /* PRERELEASE BADGE: ORANGE background, BLACK text */
    .prerelease-badge {
        background-color: var(--orange) !important;
        color: var(--black) !important;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        display: block;
        text-align: center;
        width: fit-content;
        margin: 0 auto 2rem auto;
    }
    
    /* LIGHT CARDS: LIGHT background, BLACK text */
    .info-box, .feature-box, .method-card, .file-list, .metric-card, .download-section {
        background-color: var(--light-gray) !important;
        color: var(--black) !important;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid var(--medium-gray);
        margin: 1rem 0;
    }
    
    /* ALL TEXT IN LIGHT CARDS: BLACK */
    .info-box *, .feature-box *, .method-card *, .file-list *, .metric-card *, .download-section * {
        color: var(--black) !important;
    }
    
    /* ACCENT COLORS for headers in cards */
    .info-box h4, .feature-box h4, .method-title, .download-section h4 {
        color: var(--blue) !important;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* SIDEBAR CARDS: DARKER background, WHITE text */
    .sidebar-section, .version-info {
        background-color: #555555 !important;
        color: var(--white) !important;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .sidebar-section *, .version-info * {
        color: var(--white) !important;
    }
    
    /* METRIC VALUES: Colored numbers */
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #666666 !important;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    /* SUCCESS MESSAGE: GREEN background, WHITE text */
    .success-message {
        background-color: var(--green) !important;
        color: var(--white) !important;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .success-message * {
        color: var(--white) !important;
    }
    
    /* ERROR MESSAGE: RED background, WHITE text */
    .error-message {
        background-color: var(--red) !important;
        color: var(--white) !important;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .error-message * {
        color: var(--white) !important;
    }
    
    /* FOOTER: BLACK text on WHITE background */
    .footer-text {
        text-align: center;
        color: #666666 !important;
        font-style: italic;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid var(--medium-gray);
    }
    
    /* STREAMLIT OVERRIDES */
    .stFileUploader label {
        color: var(--black) !important;
    }
    
    .stSlider label {
        color: var(--white) !important;
    }
    
    /* ALL HEADERS: BLACK text */
    h1, h2, h3, h4, h5, h6 {
        color: var(--black) !important;
    }
    
    /* MAIN TEXT: BLACK */
    .stMarkdown {
        color: var(--black) !important;
    }
    
    p {
        color: var(--black) !important;
    }
    
    /* HOVER EFFECTS */
    .metric-card:hover, .method-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    
    /* Force all Streamlit text to be readable */
    .stApp * {
        color: var(--black) !important;
    }
    
    /* Override only sidebar */
    section[data-testid="stSidebar"] * {
        color: var(--white) !important;
    }
    
    /* Override success/error messages */
    .success-message *, .error-message * {
        color: var(--white) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">RefDedup</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Reference Duplicate Remover for Systematic Reviews</p>', unsafe_allow_html=True)

# Prerelease badge
st.markdown('<div class="prerelease-badge">Prerelease Version</div>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown('<h3 style="color: white !important; margin-bottom: 1rem; font-weight: 600; border-bottom: 2px solid #666; padding-bottom: 0.5rem;">Configuration</h3>', unsafe_allow_html=True)
    
    # Title similarity threshold
    title_threshold = st.slider(
        "Title Similarity Threshold (%)",
        min_value=85,
        max_value=100,
        value=95,
        step=1,
        help="Higher values are more conservative. 95% recommended for optimal results."
    )
    
    st.markdown("---")
    
    # Information section
    st.markdown('<h3 style="color: white !important; margin-bottom: 1rem; font-weight: 600; border-bottom: 2px solid #666; padding-bottom: 0.5rem;">Detection Methods</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-section">
        <p><strong>Priority order:</strong></p>
        <ol>
            <li><strong>DOI matching</strong> - Exact match</li>
            <li><strong>PMID matching</strong> - Exact match</li>
            <li><strong>Title similarity</strong> - Configurable threshold</li>
        </ol>
        
        <p><strong>Supported formats:</strong></p>
        <ul>
            <li>RIS (.ris)</li>
            <li>NBIB (.nbib)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Version and credits
    st.markdown("""
    <div class="version-info">
        <p><strong>Version:</strong> 1.0</p>
        <p><strong>Status:</strong> Prerelease</p>
        <p><strong>Developer:</strong> Mohamed Abu Elainein</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File upload section
    st.markdown('<h3 class="section-header">Upload Files</h3>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose RIS or NBIB files",
        type=["ris", "nbib"],
        accept_multiple_files=True,
        help="Upload multiple files to combine and deduplicate them together"
    )
    
    if uploaded_files:
        # Show uploaded files
        st.markdown('<h4 class="section-header">Uploaded Files</h4>', unsafe_allow_html=True)
        files_html = '<div class="file-list">'
        for i, file in enumerate(uploaded_files, 1):
            files_html += f'<p><strong>{i}.</strong> {file.name} <span style="color: #666 !important;">({file.size:,} bytes)</span></p>'
        files_html += '</div>'
        st.markdown(files_html, unsafe_allow_html=True)

with col2:
    # Features box
    st.markdown("""
    <div class="feature-box">
        <h4>Key Features</h4>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin-bottom: 0.5rem;">• Multiple file format support</li>
            <li style="margin-bottom: 0.5rem;">• Intelligent duplicate detection</li>
            <li style="margin-bottom: 0.5rem;">• Conservative similarity matching</li>
            <li style="margin-bottom: 0.5rem;">• Dual output files (clean + duplicates)</li>
            <li style="margin-bottom: 0.5rem;">• Clean professional interface</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Processing section
if uploaded_files:
    st.markdown("---")
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Process Files", type="primary", use_container_width=True):
            # Show processing indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Processing steps with progress updates
                status_text.text("Reading uploaded files...")
                progress_bar.progress(20)
                time.sleep(0.3)
                
                status_text.text("Parsing reference data...")
                progress_bar.progress(40)
                time.sleep(0.3)
                
                status_text.text("Extracting identifiers (DOI, PMID)...")
                progress_bar.progress(60)
                time.sleep(0.3)
                
                status_text.text("Detecting duplicates...")
                progress_bar.progress(80)
                
                # Process the files
                cleaned_records, total_before, total_after, file_stats, removed_records = process_uploaded_files(
                    uploaded_files, 
                    title_threshold=title_threshold
                )
                
                progress_bar.progress(100)
                status_text.text("Processing complete")
                time.sleep(0.3)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Results section
                st.markdown('<h3 class="section-header">Processing Results</h3>', unsafe_allow_html=True)
                
                # Statistics cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #0066cc !important;">{}</div>
                        <div class="metric-label">Original Records</div>
                    </div>
                    """.format(total_before), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #28a745 !important;">{}</div>
                        <div class="metric-label">Final Records</div>
                    </div>
                    """.format(total_after), unsafe_allow_html=True)
                
                with col3:
                    duplicates_removed = total_before - total_after
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #dc3545 !important;">{}</div>
                        <div class="metric-label">Duplicates Found</div>
                    </div>
                    """.format(duplicates_removed), unsafe_allow_html=True)
                
                with col4:
                    if total_before > 0:
                        reduction_percent = (duplicates_removed / total_before) * 100
                    else:
                        reduction_percent = 0
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #ff9800 !important;">{:.1f}%</div>
                        <div class="metric-label">Reduction</div>
                    </div>
                    """.format(reduction_percent), unsafe_allow_html=True)
                
                # Success message
                st.markdown("""
                <div class="success-message">
                    <strong>Processing completed successfully</strong><br>
                    Your cleaned references and duplicate records are ready for download.
                </div>
                """, unsafe_allow_html=True)
                
                # Generate output files
                cleaned_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
                
                # Generate duplicates file
                duplicates_content = ""
                if removed_records:
                    duplicates_ris = []
                    for record in removed_records:
                        # Remove the debugging fields before converting to RIS
                        clean_record = {k: v for k, v in record.items() if not k.startswith('_')}
                        duplicates_ris.append(record_to_ris(clean_record))
                    duplicates_content = "\n\n".join(duplicates_ris)
                
                # Download section
                st.markdown("""
                <div class="download-section">
                    <h4>Download Results</h4>
                    <p>Two files are available for download:</p>
                """, unsafe_allow_html=True)
                
                # Two download buttons side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="Download Cleaned References",
                        data=cleaned_content,
                        file_name=f"cleaned_references_{total_after}_records.ris",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True,
                        help=f"Contains {total_after} unique references"
                    )
                    st.write(f"**File size:** {len(cleaned_content.encode('utf-8')):,} bytes")
                
                with col2:
                    if duplicates_content:
                        st.download_button(
                            label="Download Duplicate Records",
                            data=duplicates_content,
                            file_name=f"duplicate_records_{duplicates_removed}_found.ris",
                            mime="text/plain",
                            use_container_width=True,
                            help=f"Contains {duplicates_removed} duplicate references for review"
                        )
                        st.write(f"**File size:** {len(duplicates_content.encode('utf-8')):,} bytes")
                    else:
                        st.info("No duplicates found")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-message">
                    <strong>Error processing files:</strong> {str(e)}<br>
                    Please verify your files are in valid RIS or NBIB format.
                </div>
                """, unsafe_allow_html=True)

else:
    # Instructions when no files uploaded
    st.markdown("""
    <div class="info-box">
        <h4>How to Use RefDedup</h4>
        <ol>
            <li><strong>Upload Files:</strong> Select your RIS or NBIB reference files using the file uploader above</li>
            <li><strong>Configure Settings:</strong> Adjust the similarity threshold in the sidebar (95% recommended)</li>
            <li><strong>Process:</strong> Click the "Process Files" button to identify and remove duplicates</li>
            <li><strong>Download:</strong> Get two RIS files - cleaned references and duplicate records</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-header">Duplicate Detection Methods</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">DOI Matching (Priority 1)</div>
            <p>Exact matching of Digital Object Identifiers. Most reliable method with enhanced pattern recognition.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">PMID Matching (Priority 2)</div>
            <p>Exact matching of PubMed IDs with validation. Highly accurate for medical literature.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">Title Similarity (Priority 3)</div>
            <p>Conservative fuzzy matching with adjustable thresholds to minimize false positives.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer-text">RefDedup v1.0 Prerelease - Professional Reference Management Tool</div>', unsafe_allow_html=True)
