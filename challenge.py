import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import json

# Configure page
st.set_page_config(
    page_title="Challenge",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend URL
API_BASE_URL = "http://localhost:8000"  

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c5aa0;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }

    .analysis-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def upload_data(file):
    """Upload data to FastAPI backend"""
    with st.spinner("Uploading and processing data... This may take a few minutes."):
        try:
            # Reset file pointer
            file.seek(0)
            
            # Prepare file for upload
            files = {"file": (file.name, file.getvalue(), "text/csv")}
            
            # Make API call
            response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                st.success("Data uploaded successfully!")
                
                # Show upload results
                st.json(result)
                
                # Store success state
                st.session_state.data_uploaded = True
                st.session_state.upload_result = result
                
                # Refresh the page to show analysis section
                st.rerun()
                
            else:
                st.error(f"Upload failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            st.error("Upload timed out. Please try again with a smaller file or check server status.")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API server. Please ensure the backend is running.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

def run_analysis(user_id, start_date, end_date):
    """Run analysis via API call"""
    with st.spinner("Analyzing transactions..."):
        try:
            # Prepare parameters
            params = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            # Make API call
            response = requests.get(
                f"{API_BASE_URL}/summary/{user_id}",
                params=params,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Display results
                st.success("Analysis completed!")
                
                # Show results in expandable sections
                with st.expander("📊 Analysis Results", expanded=True):
                    st.json(data)
                
            
                
            elif response.status_code == 404:
                st.warning(f" No transactions found for User ID {user_id} in the specified date range.")
                
            else:
                st.error(f"Analysis failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to API server. Please ensure the backend is running.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

def main():
    st.markdown('<h1 class="main-header">Challenge</h1>', unsafe_allow_html=True)

    # Initialize session state
    if 'data_uploaded' not in st.session_state:
        st.session_state.data_uploaded = False
    
    # section1: File Upload
    st.markdown('<h2 class="section-header">Upload Transaction Data</h2>', unsafe_allow_html=True)
    
    # Show upload status
    if st.session_state.data_uploaded:
        st.success("Data has been uploaded successfully!")
        if st.button("Upload New Data", type="secondary"):
            st.session_state.data_uploaded = False
            st.rerun()
    else:
        st.markdown("""
        <div class="upload-section">
            <h3>Upload your CSV file containing e-commerce transactions</h3>
            <p><strong>Expected format:</strong> transaction_id, user_id, product_id, timestamp, transaction_amount</p>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with transaction data (max 200MB)"
        )
        
        if uploaded_file is not None:
            # Show file details
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / (1024*1024):.2f} MB",
                "File type": uploaded_file.type
            }
            
            st.subheader("📋 File Information")
            col1, col2 = st.columns(2)
            
            with col1:
                for key, value in file_details.items():
                    st.info(f"**{key}**: {value}")
            
        
            # Upload button
            if uploaded_file is not None:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Upload and Process Data", type="primary", use_container_width=True):
                        upload_data(uploaded_file)
    
    # section2: Analysis
    if st.session_state.data_uploaded:
        st.markdown('<h2 class="section-header">Transaction Analysis</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="analysis-section">
            <h3>🔍 Configure Your Analysis</h3>
            <p>Set parameters below to analyze the uploaded transaction data.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User input section
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.number_input(
                "User ID",
                min_value=1,
                max_value=10000,
                value=1,
                help="Enter the User ID to analyze"
            )
        
       
        
        # Date range selection
        st.subheader("Date Range (Optional)")
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365),
                help="Leave as default to include all dates"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now(),
                help="Leave as default to include all dates"
            )
        
        # Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔬 Run Analysis", type="primary", use_container_width=True):
                run_analysis(user_id, start_date, end_date)
    
    else:
        # Show placeholder for analysis section
        st.markdown('<h2 class="section-header">Transaction Analysis</h2>', unsafe_allow_html=True)
        st.info("Upload transaction data above to enable analysis features.")
    
   

if __name__ == "__main__":
    main()