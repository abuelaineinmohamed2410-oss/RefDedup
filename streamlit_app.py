import streamlit as st
import pandas as pd
from dedup import process_uploaded_files, record_to_ris
import time

# Page configuration
st.set_page_config(
    page_title="RefDedup - Reference Duplicate Remover",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stats-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    
    .feature-box {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
    }
    
    .stFileUploader > div > div > div > div {
        background-color: #f8f9fa;
        border: 2px dashed #1f77b4;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">RefDedup</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Professional Reference Duplicate Remover for Systematic Reviews</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
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
    st.header("ℹ️ About")
    st.markdown("""
    **RefDedup** intelligently removes duplicate references from your systematic review files using:
    
    • **DOI matching** - Most reliable identifier
    • **PMID matching** - PubMed unique identifier  
    • **Title similarity** - Fuzzy matching algorithm
    
    **Supported formats:**
    • RIS (.ris)
    • NBIB (.nbib)
    """)
    
    st.markdown("---")
    
    # Credits
    st.markdown("**Developed by:** Mohamed Abu Elainein")
    st.markdown("**Version:** 2.0")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File upload section
    st.markdown("### 📁 Upload Your Files")
    
    uploaded_files = st.file_uploader(
        "Choose RIS or NBIB files",
        type=["ris", "nbib"],
        accept_multiple_files=True,
        help="You can upload multiple files at once. They will be combined before duplicate removal."
    )
    
    if uploaded_files:
        # Show uploaded files
        st.markdown("### 📋 Uploaded Files")
        for i, file in enumerate(uploaded_files, 1):
            st.write(f"{i}. **{file.name}** ({file.size:,} bytes)")

with col2:
    # Features box
    st.markdown("""
    <div class="feature-box">
        <h4>🚀 Key Features</h4>
        <ul>
            <li>Multiple file format support</li>
            <li>Intelligent duplicate detection</li>
            <li>Configurable similarity threshold</li>
            <li>Detailed processing statistics</li>
            <li>Clean, professional interface</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Processing section
if uploaded_files:
    st.markdown("---")
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Process Files", type="primary", use_container_width=True):
            # Show processing indicator
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Simulate processing steps for better UX
                status_text.text("Reading uploaded files...")
                progress_bar.progress(25)
                time.sleep(0.5)
                
                status_text.text("Parsing reference data...")
                progress_bar.progress(50)
                time.sleep(0.5)
                
                status_text.text("Detecting duplicates...")
                progress_bar.progress(75)
                
                # Process the files
                cleaned_records, total_before, total_after, file_stats = process_uploaded_files(
                    uploaded_files, 
                    title_threshold=title_threshold
                )
                
                progress_bar.progress(100)
                status_text.text("Processing complete!")
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Results section
                st.markdown("### 📊 Processing Results")
                
                # Statistics cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <h3 style="color: #1f77b4;">{}</h3>
                        <p>Original Records</p>
                    </div>
                    """.format(total_before), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <h3 style="color: #28a745;">{}</h3>
                        <p>After Deduplication</p>
                    </div>
                    """.format(total_after), unsafe_allow_html=True)
                
                with col3:
                    duplicates_removed = total_before - total_after
                    st.markdown("""
                    <div class="metric-card">
                        <h3 style="color: #dc3545;">{}</h3>
                        <p>Duplicates Removed</p>
                    </div>
                    """.format(duplicates_removed), unsafe_allow_html=True)
                
                with col4:
                    if total_before > 0:
                        reduction_percent = (duplicates_removed / total_before) * 100
                    else:
                        reduction_percent = 0
                    st.markdown("""
                    <div class="metric-card">
                        <h3 style="color: #ff9800;">{:.1f}%</h3>
                        <p>Reduction</p>
                    </div>
                    """.format(reduction_percent), unsafe_allow_html=True)
                
                # File breakdown
                if len(file_stats) > 1:
                    st.markdown("### 📈 File Breakdown")
                    
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
                    <strong>✅ Processing completed successfully!</strong><br>
                    Your deduplicated references are ready for download.
                </div>
                """, unsafe_allow_html=True)
                
                # Generate output
                output_content = "\n\n".join([record_to_ris(rec) for rec in cleaned_records])
                
                # Download section
                st.markdown("### 💾 Download Results")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.download_button(
                        label="⬇️ Download Cleaned References (RIS)",
                        data=output_content,
                        file_name=f"deduplicated_references_{len(cleaned_records)}_records.ris",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True
                    )
                
                with col2:
                    st.metric("File Size", f"{len(output_content.encode('utf-8')):,} bytes")
                
            except Exception as e:
                st.error(f"❌ **Error processing files:** {str(e)}")
                st.info("Please check that your files are in valid RIS or NBIB format and try again.")

else:
    # Instructions when no files uploaded
    st.markdown("""
    <div class="info-box">
        <h4>📝 How to Use RefDedup</h4>
        <ol>
            <li><strong>Upload Files:</strong> Select your RIS or NBIB reference files</li>
            <li><strong>Configure Settings:</strong> Adjust the similarity threshold in the sidebar</li>
            <li><strong>Process:</strong> Click the process button to remove duplicates</li>
            <li><strong>Download:</strong> Get your cleaned reference file</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Duplicate Detection Methods")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔗 DOI Matching**
        - Most reliable method
        - Exact identifier matching
        - Works across different formats
        """)
    
    with col2:
        st.markdown("""
        **🏥 PMID Matching**
        - PubMed unique identifiers
        - Highly accurate for medical literature
        - Instant duplicate detection
        """)
    
    with col3:
        st.markdown("""
        **📝 Title Similarity**
        - Fuzzy string matching
        - Handles minor variations
        - Configurable threshold
        """)

# Footer
st.markdown("---")
st.markdown("*RefDedup helps researchers maintain high-quality systematic reviews by ensuring reference lists are free from duplicates.*")
