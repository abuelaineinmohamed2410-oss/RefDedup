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

# Simple Clean Theme with Perfect Contrast
st.markdown("""
    <style>
    /* Simple, clean colors */
    :root {
        --dark-bg: #1a1a1a;
        --medium-bg: #2d2d2d;
        --light-bg: #404040;
        --white-text: #ffffff;
        --light-text: #e0e0e0;
        --accent-blue: #4a90e2;
        --success-green: #27ae60;
        --warning-orange: #f39c12;
        --error-red: #e74c3c;
        --border-gray: #555555;
    }
    
    /* Main app background */
    .stApp {
        background-color: var(--dark-bg);
        color: var(--white-text);
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--medium-bg) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--white-text) !important;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        color: var(--white-text);
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: var(--light-text);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 1.2rem;
        color: var(--white-text);
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 1px solid var(--border-gray);
        padding-bottom: 0.5rem;
    }
    
    /* Prerelease badge */
    .prerelease-badge {
        background-color: var(--warning-orange);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        display: block;
        text-align: center;
        width: fit-content;
        margin: 0 auto 2rem auto;
    }
    
    /* Cards */
    .info-box, .feature-box, .method-card, .sidebar-section, .version-info, .file-list, .download-section {
        background-color: var(--medium-bg);
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid var(--border-gray);
        margin: 1rem 0;
    }
    
    .info-box h4, .feature-box h4 {
        color: var(--accent-blue);
        margin-bottom: 0.8rem;
        font-weight: 600;
    }
    
    .method-title {
        color: var(--accent-blue);
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .info-box p, .info-box li,
    .feature-box p, .feature-box li,
    .method-card p,
    .sidebar-section p, .sidebar-section li,
    .download-section p {
        color: var(--light-text);
        line-height: 1.5;
    }
    
    .version-info p, .file-list p {
        color: var(--white-text);
        margin: 0.2rem 0;
    }
    
    .file-list span {
        color: var(--light-text);
    }
    
    /* Metric cards */
    .metric-card {
        background-color: var(--medium-bg);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-gray);
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--light-text);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Messages */
    .success-message {
        background-color: var(--success-green);
        color: white;
        padding: 1rem;
        border-radius: 6px;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: var(--error-red);
        color: white;
        padding: 1rem;
        border-radius: 6px;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: var(--light-text);
        font-style: italic;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid var(--border-gray);
    }
    
    /* Streamlit overrides only where necessary */
    .stFileUploader label {
        color: var(--white-text) !important;
    }
    
    .stSlider label {
        color: var(--white-text) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--white-text);
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
                        <div class="metric-value" style="color: #4a90e2;">{}</div>
                        <div class="metric-label">Original Records</div>
                    </div>
                    """.format(total_before), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #27ae60;">{}</div>
                        <div class="metric-label">Final Records</div>
                    </div>
                    """.format(total_after), unsafe_allow_html=True)
                
                with col3:
                    duplicates_removed = total_before - total_after
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #e74c3c;">{}</div>
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
                        <div class="metric-value" style="color: #f39c12;">{:.1f}%</div>
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
                    <h4 style="color: white; margin-bottom: 1rem;">Download Results</h4>
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
