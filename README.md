# E-commerce Transaction

A full-stack application for analyzing e-commerce transaction data with CSV file upload capabilities and real-time analysis.

## 🎯 My Approach to This Challenge

For this challenge, I adopted an architecture with distinct backend and frontend layers, utilizing FastAPI for robust data processing and validation, while implementing Streamlit for an intuitive user interface. The application follows a simple two-endpoint design where users first upload CSV transaction data, then query summary statistics for specific users. I chose to use a global variable to store the uploaded data for simplicity.

The upload endpoint handles CSV file ingestion with comprehensive error handling. I implemented several validation layers starting with file extension checking to ensure only CSV files are accepted. The endpoint reads the uploaded file content, handles encoding issues by explicitly decoding as UTF-8, and uses pandas to parse the CSV data. I wrapped the entire process in try-catch blocks to handle various failure scenarios like empty files, encoding errors, or malformed CSV structures, returning appropriate HTTP status codes and error messages for each case.

The summary endpoint provides transaction analytics for individual users with optional date range filtering. I designed it to accept a user ID as a path parameter and optional start and end dates as query parameters. The endpoint first validates that data has been uploaded, then checks for required columns in the dataset. For date filtering, I convert timestamp strings to datetime objects using pandas, which provides robust date parsing capabilities. The business logic calculates key statistics including maximum, minimum, and mean transaction amounts, plus transaction count

Throughout the application, I implemented programming practices by validating inputs at multiple levels and providing specific error messages. For example, I check for empty datasets, missing required columns and invalid date formats, returning 400-level status codes for client errors and 404 when no data matches the query criteria. This approach helps with debugging and provides clear feedback to API consumers. The testing strategy adopts a test-driven mindset with comprehensive coverage for all scenarios, particular emphasis on edge case testing for boundary conditions and performance considerations including benchmarks.

## 🏗️ Architecture Overview

This project consists of three main components:

1. **FastAPI Backend** (`backend.py`) - RESTful API for data processing
2. **Streamlit Frontend** (`challenge.py`) - Interactive web interface
3. **Comprehensive Test Suite** (`test.py`) - Automated testing with pytest

## 🚀 Features

### Backend API

- **File Upload**: Secure CSV file upload with validation
- **Transaction Analysis**: Real-time statistical analysis of user transactions
- **Date Filtering**: Optional date range filtering for targeted analysis
- **Error Handling**: Comprehensive error handling and validation
- **Data Validation**: Automatic validation of required columns and data integrity

### Frontend Interface

- **Drag & Drop Upload**: Intuitive file upload with preview
- **Data Validation**: Real-time validation and file information display
- **Interactive Analysis**: Configure analysis parameters with date range selection
- **Responsive Design**: Modern UI with custom styling

### Key Metrics Provided

- Maximum transaction amount
- Minimum transaction amount
- Mean transaction amount
- Total transaction count
- Date range filtering capabilities

## 📋 Requirements

### Expected CSV Format

Your CSV file should contain the following columns:

- `transaction_id`: Unique identifier for each transaction
- `user_id`: User identifier
- `product_id`: Product identifier
- `timestamp`: Transaction timestamp (YYYY-MM-DD HH:MM:SS format)
- `transaction_amount`: Transaction amount (numeric)

### Dependencies

```
fastapi>=0.104.1
uvicorn>=0.24.0
pandas>=2.1.3
streamlit>=1.28.1
requests>=2.31.0
pytest>=7.4.3
```

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install requirements.txt
```

### 4. Start the Backend Server

```bash
python backend.py
```

The API will be available at `http://localhost:8000`

### 5. Start the Frontend Application

In a new terminal:

```bash
streamlit run challenge.py
```

The web interface will be available at `http://localhost:8501`

## 📖 Usage Guide

### Step 1: Upload Transaction Data

1. Open the Streamlit interface in your browser
2. Upload a CSV file using the file uploader
3. Preview your data to ensure correct format
4. Click "Upload and Process Data"

### Step 2: Configure Analysis

1. Enter the User ID you want to analyze
2. Optionally set date range filters
3. Click "Run Analysis"

### Step 3: View Results

- Review the analysis results displayed in JSON format
- Export or save results as needed

## 🔧 API Endpoints

### POST `/upload`

Upload a CSV file for processing.

**Request:**

- File: CSV file with transaction data

**Response:**

```json
{
  "message": "File uploaded successfully",
  "filename": "transactions.csv"
}
```

### GET `/summary/{user_id}`

Get transaction summary for a specific user.

**Parameters:**

- `user_id` (path): User ID to analyze
- `start_date` (query, optional): Start date (YYYY-MM-DD)
- `end_date` (query, optional): End date (YYYY-MM-DD)

**Response:**

```json
{
  "user_id": 101,
  "max_transaction_amount": 300.0,
  "min_transaction_amount": 75.25,
  "mean_transaction_amount": 175.25,
  "count": 3
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
pytest test.py -v
```

### Test Coverage

- **Upload Endpoint Tests**: File validation, error handling, data integrity
- **Summary Endpoint Tests**: Data analysis, date filtering, edge cases
- **Edge Cases**: Large datasets, invalid inputs, boundary conditions
- **Performance Tests**: Upload and analysis performance benchmarks
- **Concurrency Tests**: Multiple upload scenarios

### Test Categories

1. **Validation Tests**: File format, required columns, data types
2. **Functional Tests**: Core API functionality
3. **Error Handling Tests**: Invalid inputs, missing data, corrupted files
4. **Performance Tests**: Large file handling, response time validation
5. **Edge Case Tests**: Boundary conditions, unusual inputs

**Built with:** FastAPI, Streamlit, Pandas, and Python
