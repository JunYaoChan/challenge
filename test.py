import pytest
import pandas as pd
import io
from fastapi.testclient import TestClient
from unittest.mock import patch
import time 
import tempfile
import os
from backend import app, uploaded_data

# Create test client
client = TestClient(app)


class TestTransactionAPI:
    
    def setup_method(self):
        """Reset uploaded_data before each test"""
        global uploaded_data
        uploaded_data = None
        
    def create_test_csv_content(self, data=None):
        """Helper method to create test CSV content"""
        if data is None:
            data = {
                'transaction_id': [1, 2, 3, 4, 5],
                'user_id': [101, 102, 101, 103, 102],
                'product_id': [1001, 1002, 1003, 1001, 1002],
                'timestamp': ['2024-01-01 10:00:00', '2024-01-02 11:00:00', 
                             '2024-01-03 12:00:00', '2024-01-04 13:00:00', 
                             '2024-01-05 14:00:00'],
                'transaction_amount': [100.50, 250.75, 75.25, 300.00, 150.50]
            }
        
        df = pd.DataFrame(data)
        csv_content = df.to_csv(index=False)
        return csv_content.encode('utf-8')

    def create_test_file(self, content, filename="test.csv"):
        """Helper method to create test file object"""
        return ("file", (filename, io.BytesIO(content), "text/csv"))

class TestUploadEndpoint(TestTransactionAPI):
    
    def test_upload_valid_csv(self):
        """Test uploading a valid CSV file"""
        csv_content = self.create_test_csv_content()
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        response = client.post("/upload", files=files)
        assert response.status_code == 200
        
        summary_response = client.get("/summary/101")
        assert summary_response.status_code == 200  

    def test_upload_invalid_file_extension(self):
        """Test uploading file with invalid extension"""
        csv_content = self.create_test_csv_content()
        files = {"file": ("test.txt", io.BytesIO(csv_content), "text/plain")}
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 400
        assert "Only CSV files are accepted" in response.json()["detail"]

    def test_upload_corrupted_csv(self):
        """Test uploading corrupted CSV file"""
        corrupted_content = b"This is not a valid CSV content"
        files = {"file": ("test.csv", io.BytesIO(corrupted_content), "text/csv")}
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 400
        assert "Error reading CSV file" in response.json()["detail"]

    def test_upload_empty_csv(self):
        """Test uploading empty CSV file"""
        empty_content = b""
        files = {"file": ("test.csv", io.BytesIO(empty_content), "text/csv")}
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 400
        assert "Error reading CSV file" in response.json()["detail"]


    def test_upload_missing_required_columns(self):
        """Test uploading CSV with missing required columns"""
        data = {
            'transaction_id': [1, 2, 3],
            'product_id': [1001, 1002, 1003],
            'timestamp': ['2024-01-01 10:00:00', '2024-01-02 11:00:00', '2024-01-03 12:00:00'],
        }
        csv_content = self.create_test_csv_content(data)
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        
        response = client.post("/upload", files=files)
        
        # Upload should succeed, but summary endpoint should fail
        assert response.status_code == 200

class TestSummaryEndpoint(TestTransactionAPI):
    
    def setup_method(self):
        """Setup test data for summary tests"""
        super().setup_method()
        # Upload test data first
        csv_content = self.create_test_csv_content()
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        client.post("/upload", files=files)

    def test_get_summary_valid_user(self):
        """Test getting summary for existing user"""
        response = client.get("/summary/101")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == 101
        assert data["count"] == 2  # User 101 has 2 transactions
        assert data["max_transaction_amount"] == 100.50
        assert data["min_transaction_amount"] == 75.25
        assert abs(data["mean_transaction_amount"] - 87.875) < 0.001

    def test_get_summary_nonexistent_user(self):
        """Test getting summary for non-existent user"""
        response = client.get("/summary/999")
        
        assert response.status_code == 404
        assert "No transactions found" in response.json()["detail"]

    def test_get_summary_with_date_range(self):
        """Test getting summary with date filtering"""
        response = client.get("/summary/101?start_date=2024-01-01&end_date=2024-01-02")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == 101
        assert data["count"] == 1  

    def test_get_summary_start_date_only(self):
        """Test getting summary with only start date"""
        response = client.get("/summary/101?start_date=2024-01-02")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == 101
        assert data["count"] == 1  

    def test_get_summary_end_date_only(self):
        """Test getting summary with only end date"""
        response = client.get("/summary/101?end_date=2024-01-02")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["user_id"] == 101
        assert data["count"] == 1 

    
    def test_get_summary_missing_required_columns(self):
        """Test summary with CSV missing required columns"""
        # Upload CSV without required columns
        data = {
            'transaction_id': [1, 2, 3],
            'product_id': [1001, 1002, 1003],
            'timestamp': ['2024-01-01 10:00:00', '2024-01-02 11:00:00', '2024-01-03 12:00:00'],
        }
        csv_content = self.create_test_csv_content(data)
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        client.post("/upload", files=files)
        
        response = client.get("/summary/101")
        
        assert response.status_code == 400
        assert "CSV must contain 'user_id' and 'transaction_amount' columns" in response.json()["detail"]

    def test_get_summary_missing_timestamp_column_with_dates(self):
        """Test summary with date filtering when timestamp column is missing"""
        # Upload CSV without timestamp column
        data = {
            'user_id': [101, 102, 101],
            'transaction_amount': [100.50, 250.75, 75.25],
            'product_id': [1001, 1002, 1003],
        }
        csv_content = self.create_test_csv_content(data)
        files = {"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
        client.post("/upload", files=files)
        
        response = client.get("/summary/101?start_date=2024-01-01")
        
        assert response.status_code == 400
        assert "CSV must contain 'timestamp' column for date filtering" in response.json()["detail"]

    def test_get_summary_invalid_date_format(self):
        """Test summary with invalid date format"""
        response = client.get("/summary/101?start_date=invalid-date")
        
        # This should still work as pandas will handle the error
        # The API should handle pandas datetime parsing errors
        assert response.status_code in [400, 500]  # Depends on how you handle pandas errors

    def test_get_summary_date_range_no_results(self):
        """Test summary with date range that returns no results"""
        response = client.get("/summary/101?start_date=2025-01-01&end_date=2025-12-31")
        
        assert response.status_code == 404
        assert "No transactions found" in response.json()["detail"]


class TestConcurrency(TestTransactionAPI):
    
    def test_multiple_uploads_override(self):
        """Test that multiple uploads override previous data"""
        # First upload
        csv_content1 = self.create_test_csv_content()
        files1 = {"file": ("test1.csv", io.BytesIO(csv_content1), "text/csv")}
        response1 = client.post("/upload", files=files1)
        assert response1.status_code == 200
        
        # Check first data
        response_summary1 = client.get("/summary/101")
        assert response_summary1.status_code == 200
        count1 = response_summary1.json()["count"]
        
        # Second upload with different data
        data2 = {
            'transaction_id': [10, 11],
            'user_id': [201, 202],
            'product_id': [2001, 2002],
            'timestamp': ['2024-02-01 10:00:00', '2024-02-02 11:00:00'],
            'transaction_amount': [500.00, 600.00]
        }
        csv_content2 = self.create_test_csv_content(data2)
        files2 = {"file": ("test2.csv", io.BytesIO(csv_content2), "text/csv")}
        response2 = client.post("/upload", files=files2)
        assert response2.status_code == 200
        
        # Check that old user doesn't exist anymore
        response_old_user = client.get("/summary/101")
        assert response_old_user.status_code == 404
        
        # Check new user exists
        response_new_user = client.get("/summary/201")
        assert response_new_user.status_code == 200


# Performance test 
def test_upload_performance():
    """Basic performance test for upload endpoint"""
    import time
    
    # Create larger dataset for performance testing
    data = {
        'transaction_id': list(range(1000)),
        'user_id': [i % 100 for i in range(1000)], 
        'product_id': [i % 50 for i in range(1000)],  
        'timestamp': ['2024-01-01 10:00:00'] * 1000,
        'transaction_amount': [100.0 + (i % 100) for i in range(1000)]
    }
    
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False).encode('utf-8')
    files = {"file": ("large_test.csv", io.BytesIO(csv_content), "text/csv")}
    
    start_time = time.time()
    response = client.post("/upload", files=files)
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 5  # Should complete within 5 seconds
    
    # Test summary performance
    start_time = time.time()
    response = client.get("/summary/1")
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 1  # Should complete within 1 second

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])