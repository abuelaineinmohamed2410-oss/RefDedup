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

# Clean Professional Dark Blue Theme
st.markdown("""
    <style>
    /* Professional color palette */
    :root {
        --navy-primary: #1e3a8a;
        --navy-secondary: #1e40af;
        --navy-light: #3b82f6;
        --slate-dark: #0f172a;
        --slate-medium: #1e293b;
        --slate-light: #334155;
        --text-white: #ffffff;
        --text-light: #e2e8f0;
        --text-dark: #1f2937;
        --success: #059669;
        --warning: #d97706;
        --error: #dc2626;
        --border-light: #e5e7eb;
        --border-dark: #374151;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, var(--slate-dark) 0%, var(--navy-primary) 100%);
        color: var(--text-white);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--slate-medium) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--text-white) !important;
    }
    
    /* Headers */
    .main-header {
        font-size: 3rem;
        color: var(--text-white);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: var(--text-light);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 1.3rem;
        color: var(--text-white);
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 2px solid var(--navy-light);
        padding-bottom: 0.5rem;
    }
    
    /* Prerelease badge */
    .prerelease-badge {
        background: var(--warning);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: block;
        text-align: center;
        width: fit-content;
        margin: 0 auto 2rem auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Cards and containers */
    .info-box, .feature-box, .method-card, .sidebar-section {
        background: var(--slate-light);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-dark);
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .info-box h4, .feature-box h4, .method-card .method-title {
        color: var(--navy-light);
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .info-box p, .info-box li,
    .feature-box p, .feature-box li,
    .method-card p,
    .sidebar-section p, .sidebar-section li {
        color: var(--text-light);
        line-height: 1.6;
    }
    
    /* Version info */
    .version-info {
        background: var(--slate-light);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-dark);
        margin: 1rem 0;
        text-align: center;
    }
    
    .version-info p {
        color: var(--text-white);
        margin: 0.2rem 0;
    }
    
    /* File list */
    .file-list {
        background: var(--slate-light);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-dark);
        margin: 1rem 0;
    }
    
    .file-list p {
        color: var(--text-white);
        margin: 0.3rem 0;
    }
    
    .file-list span {
        color: var(--text-light);
    }
    
    /* Metric cards */
    .metric-card {
        background: var(--slate-light);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-dark);
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-light);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    /* Messages */
    .success-message {
        background: var(--success);
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .error-message {
        background: var(--error);
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Download section */
    .download-section {
        background: var(--slate-light);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--success);
        margin: 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .download-section h4 {
        color: var(--text-white);
        margin-bottom: 1rem;
    }
    
    .download-section p {
        color: var(--text-light);
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: var(--text-light);
        font-style: italic;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid var(--border-dark);
    }
    
    /* Streamlit components - let them keep their default styling but ensure readability */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
    }
    
    .stDownloadButton > button {
        border-radius: 6px;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
    }
    
    /* File uploader - keep Streamlit's default styling */
    .stFileUploader label {
        color: var(--text-white) !important;
    }
    
    /* Slider */
    .stSlider label {
        color: var(--text-white) !important;
    }
    
    /* General text */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-white);
    }
    
    .stMarkdown {
        color: var(--text-light);
    }
    
    /* Method cards hover effect */
    .method-card {
        transition: transform 0.2s ease;
    }
    
    .method-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
    st.markdown('<h3 class="section-header">Configuration</h3>', unsafe_allow_html=True)
    
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
    st.markdown('<h3 class="section-header">Detection Methods</h3>', unsafe_allow_html=True)
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
            files_html += f'<p><strong>{i}.</strong> {file.name} <span>({file.size:,} bytes)</span></p>'
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
            <li style="margin-bottom: 0.5rem;">• Professional interface design</li>
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
                        <div class="metric-value" style="color: #3b82f6;">{}</div>
                        <div class="metric-label">Original Records</div>
                    </div>
                    """.format(total_before), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #059669;">{}</div>
                        <div class="metric-label">Final Records</div>
                    </div>
                    """.format(total_after), unsafe_allow_html=True)
                
                with col3:
                    duplicates_removed = total_before - total_after
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #dc2626;">{}</div>
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
                        <div class="metric-value" style="color: #d97706;">{:.1f}%</div>
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
