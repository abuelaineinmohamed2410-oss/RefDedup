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

# Custom CSS for clean, professional appearance
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    .section-header {
        font-size: 1.4rem;
        color: #34495e;
        margin-bottom: 1rem;
        font-weight: 500;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 0.5rem;
    }
    
    .stats-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #fdfdfe;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e1e8ed;
        margin: 1rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .feature-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e1e8ed;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #e1e8ed;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .success-message {
        background-color: #d5f4e6;
        color: #27ae60;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        font-weight: 500;
    }
    
    .error-message {
        background-color: #fadbd8;
        color: #e74c3c;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
        font-weight: 500;
    }
    
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .method-card {
        background-color: #ffffff;
        padding: 1.2rem;
        border-radius: 6px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .method-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .file-list {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    
    .stFileUploader > div > div > div > div {
        background-color: #fdfdfe;
        border: 2px dashed #3498db;
        border-radius: 8px;
        padding: 2rem;
    }
    
    .process-button {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .download-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        margin: 1.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">RefDedup</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Reference Duplicate Remover for Systematic Reviews</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown('<h3 class="section-header">Configuration</h3>', unsafe_allow_html=True)
    
    # Title similarity threshold
    title_threshold = st.slider(
        "Title Similarity Threshold (%)",
        min_value=70,
        max_value=100,
        value=90,
        step=5,
        help="Higher values require more similar titles to be considered duplicates"
    )
    
    st.markdown("---")
    
    # Information section
    st.markdown('<h3 class="section-header">Information</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-section">
        <p><strong>RefDedup</strong> intelligently removes duplicate references using multiple detection methods:</p>
        <ul>
            <li><strong>DOI matching</strong> - Most reliable identifier</li>
            <li><strong>PMID matching</strong> - PubMed unique identifier</li>
            <li><strong>Title similarity</strong> - Fuzzy matching algorithm</li>
        </ul>
        
        <p><strong>Supported formats:</strong></p>
        <ul>
            <li>RIS (.ris)</li>
            <li>NBIB (.nbib)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Credits
    st.markdown("**Developer:** Mohamed Abu Elainein")
    st.markdown("**Version:** 2.0 Professional")

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
            files_html += f'<p><strong>{i}.</strong> {file.name} <span style="color: #7f8c8d;">({file.size:,} bytes)</span></p>'
        files_html += '</div>'
        st.markdown(files_html, unsafe_allow_html=True)

with col2:
    # Features box
    st.markdown("""
    <div class="feature-box">
        <h4 style="color: #2c3e50; margin-bottom: 1rem;">Key Features</h4>
        <ul style="list-style-type: none; padding-left: 0;">
            <li style="margin-bottom: 0.5rem;">• Multiple file format support</li>
            <li style="margin-bottom: 0.5rem;">• Intelligent duplicate detection</li>
            <li style="margin-bottom: 0.5rem;">• Configurable similarity threshold</li>
            <li style="margin-bottom: 0.5rem;">• Detailed processing statistics</li>
            <li style="margin-bottom: 0.5rem;">• Clean, professional interface</li>
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
                progress_bar.progress(25)
                time.sleep(0.3)
                
                status_text.text("Parsing reference data...")
                progress_bar.progress(50)
                time.sleep(0.3)
                
                status_text.text("Detecting duplicates...")
                progress_bar.progress(75)
                
                # Process the files
                cleaned_records, total_before, total_after, file_stats = process_uploaded_files(
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
                        <div class="metric-value" style="color: #3498db;">{}</div>
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
                        <div class="metric-label">Duplicates Removed</div>
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
                
                # File breakdown for multiple files
                if len(file_stats) > 1:
                    st.markdown('<h4 class="section-header">File Breakdown</h4>', unsafe_allow_html=True)
                    
                    file_df = pd.DataFrame([
                        {"File Name": name, "Records": count}
                        for name, count in file_stats.items()
                        if isinstance(count, int)
                    ])
                    
                    if not file_df.empty:
                        st.dataframe(file_df, use_container_width=True, hide_index=True)
                
                # Success message
                st.markdown("""
                <div class="success-message">
                    <strong>Processing completed successfully</strong><br>
                    Your deduplicated references are ready for download.
                </div>
                """, unsafe_allow_html=True)
                
                # Generate output
                output_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
                
                # Download section
                st.markdown("""
                <div class="download-section">
                    <h4 style="color: #2c3e50; margin-bottom: 1rem;">Download Results</h4>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.download_button(
                        label="Download Cleaned References (RIS)",
                        data=output_content,
                        file_name=f"deduplicated_references_{len(cleaned_records)}_records.ris",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True
                    )
                
                with col2:
                    st.metric("File Size", f"{len(output_content.encode('utf-8')):,} bytes")
                
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
        <h4 style="color: #2c3e50;">How to Use RefDedup</h4>
        <ol>
            <li><strong>Upload Files:</strong> Select your RIS or NBIB reference files using the file uploader above</li>
            <li><strong>Configure Settings:</strong> Adjust the similarity threshold in the sidebar (default: 90%)</li>
            <li><strong>Process:</strong> Click the "Process Files" button to identify and remove duplicates</li>
            <li><strong>Download:</strong> Download your cleaned reference file in RIS format</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 class="section-header">Duplicate Detection Methods</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">DOI Matching</div>
            <p>Most reliable identification method using Digital Object Identifiers. Provides exact matching across different reference formats.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">PMID Matching</div>
            <p>Uses PubMed unique identifiers for precise duplicate detection, particularly effective for medical and life science literature.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="method-card">
            <div class="method-title">Title Similarity</div>
            <p>Fuzzy string matching algorithm that identifies duplicates based on title similarity, with configurable threshold settings.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*RefDedup provides researchers with accurate, efficient duplicate removal for high-quality systematic review preparation.*")
