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

# Custom CSS for professional dark blue theme
st.markdown("""
    <style>
    /* Global theme colors */
    :root {
        --primary-dark-blue: #1a365d;
        --secondary-blue: #2c5282;
        --accent-blue: #3182ce;
        --light-blue: #4299e1;
        --text-primary: #ffffff;
        --text-secondary: #e2e8f0;
        --text-muted: #a0aec0;
        --bg-primary: #0f1419;
        --bg-secondary: #1a202c;
        --bg-card: #2d3748;
        --border-color: #4a5568;
        --success-color: #38a169;
        --warning-color: #d69e2e;
        --error-color: #e53e3e;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--primary-dark-blue) 100%);
        color: var(--text-primary);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--bg-secondary);
    }
    
    .main-header {
        font-size: 3.2rem;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
        letter-spacing: -1px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #ffffff, #4299e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 1.4rem;
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-weight: 600;
        border-bottom: 2px solid var(--accent-blue);
        padding-bottom: 0.5rem;
    }
    
    .prerelease-badge {
        background: linear-gradient(45deg, var(--warning-color), #f6ad55);
        color: #1a202c;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .version-info {
        background-color: var(--bg-card);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        text-align: center;
    }
    
    .stats-container {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--accent-blue);
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .info-box {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--accent-blue);
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: var(--text-primary);
    }
    
    .feature-box {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid var(--accent-blue);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        color: var(--text-primary);
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.8rem;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        text-align: center;
        border: 1px solid var(--accent-blue);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
    }
    
    .success-message {
        background: linear-gradient(45deg, var(--success-color), #48bb78);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #38a169;
        font-weight: 500;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .error-message {
        background: linear-gradient(45deg, var(--error-color), #f56565);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--error-color);
        font-weight: 500;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.2rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    .method-card {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--accent-blue);
        margin-bottom: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        color: var(--text-primary);
    }
    
    .method-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        border-color: var(--light-blue);
    }
    
    .method-title {
        font-weight: 600;
        color: var(--light-blue);
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .file-list {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    .stFileUploader > div > div > div > div {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        border: 2px dashed var(--accent-blue);
        border-radius: 12px;
        padding: 2.5rem;
        color: var(--text-primary);
    }
    
    .download-section {
        background: linear-gradient(135deg, var(--bg-card), var(--secondary-blue));
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--success-color);
        margin: 1.5rem 0;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        color: var(--text-primary);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--accent-blue), var(--light-blue));
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.8rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, var(--light-blue), #60a5fa);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, var(--success-color), #48bb78);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(45deg, #48bb78, #68d391);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        color: var(--accent-blue);
    }
    
    /* Text colors */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary);
    }
    
    p, li, span {
        color: var(--text-secondary);
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: var(--text-muted);
        font-style: italic;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid var(--border-color);
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">RefDedup</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Reference Duplicate Remover for Systematic Reviews</p>', unsafe_allow_html=True)

# Prerelease badge
st.markdown('<div class="prerelease-badge">⚠ Prerelease Version</div>', unsafe_allow_html=True)

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
            files_html += f'<p><strong>{i}.</strong> {file.name} <span style="color: #a0aec0;">({file.size:,} bytes)</span></p>'
        files_html += '</div>'
        st.markdown(files_html, unsafe_allow_html=True)

with col2:
    # Features box
    st.markdown("""
    <div class="feature-box">
        <h4 style="color: #4299e1; margin-bottom: 1rem;">Key Features</h4>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin-bottom: 0.5rem;">• Multiple file format support</li>
            <li style="margin-bottom: 0.5rem;">• Intelligent duplicate detection</li>
            <li style="margin-bottom: 0.5rem;">• Conservative similarity matching</li>
            <li style="margin-bottom: 0.5rem;">• Dual output files (clean + duplicates)</li>
            <li style="margin-bottom: 0.5rem;">• Professional dark blue interface</li>
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
                        <div class="metric-value" style="color: #4299e1;">{}</div>
                        <div class="metric-label">Original Records</div>
                    </div>
                    """.format(total_before), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #38a169;">{}</div>
                        <div class="metric-label">Final Records</div>
                    </div>
                    """.format(total_after), unsafe_allow_html=True)
                
                with col3:
                    duplicates_removed = total_before - total_after
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value" style="color: #e53e3e;">{}</div>
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
                        <div class="metric-value" style="color: #d69e2e;">{:.1f}%</div>
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
                    <h4 style="color: #ffffff; margin-bottom: 1rem;">Download Results</h4>
                    <p style="color: #e2e8f0;">Two files are available for download:</p>
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
        <h4 style="color: #4299e1;">How to Use RefDedup</h4>
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
