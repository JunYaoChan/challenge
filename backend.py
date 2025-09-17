from fastapi import FastAPI, APIRouter, HTTPException, File, UploadFile, Query
import pandas as pd
from typing import Optional
import io
import uvicorn

app = FastAPI(
    title="Challenge",
    version="1.0.0",
)

router = APIRouter()

# Global variable to store uploaded data
uploaded_data = None  

# Endpoint to upload CSV file
@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    global uploaded_data
    
    # Check file extension
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")
    
    try:
        # Read file content
        content = await file.read()
        
        # Check if file is empty
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Error reading CSV file: Empty file")
        
        # Convert bytes to string and then to StringIO for pandas
        content_str = content.decode('utf-8')
        csv_buffer = io.StringIO(content_str)
        
        # Read CSV with pandas
        df = pd.read_csv(csv_buffer)
        
        # Check if DataFrame is empty
        if df.empty:
            raise HTTPException(status_code=400, detail="Error reading CSV file: No data found")
        
        uploaded_data = df
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error reading CSV file: Invalid file encoding")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Error reading CSV file: Empty CSV file")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV file: {str(e)}")
    
    return {"message": "File uploaded successfully", "filename": file.filename}

# Endpoint to get user transaction summary
@router.get('/summary/{user_id}')
async def get_user_summary(
    user_id: int,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format")
):
    global uploaded_data
    
    # Check if data is uploaded
    if uploaded_data is None:
        raise HTTPException(status_code=400, detail="No data uploaded yet.")
    
    df = uploaded_data.copy()  # Work with a copy to avoid modifying original
    
    # Check required columns
    if 'user_id' not in df.columns or 'transaction_amount' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain 'user_id' and 'transaction_amount' columns.")
    
    # Filter by user_id
    user_df = df[df['user_id'] == user_id]
    
    # Filter by date range if requested
    if start_date or end_date:
        if 'timestamp' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'timestamp' column for date filtering.")
        
        try:
            # Convert timestamp column to datetime
            user_df = user_df.copy()  # Avoid SettingWithCopyWarning
            user_df['timestamp'] = pd.to_datetime(user_df['timestamp'])
            
            if start_date:
                try:
                    start_dt = pd.to_datetime(start_date)
                    user_df = user_df[user_df['timestamp'] >= start_dt]
                except (ValueError, pd.errors.ParserError):
                    raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")
            
            if end_date:
                try:
                    end_dt = pd.to_datetime(end_date)
                    user_df = user_df[user_df['timestamp'] <= end_dt]
                except (ValueError, pd.errors.ParserError):
                    raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")
                    
        except (ValueError, pd.errors.ParserError) as e:
            raise HTTPException(status_code=400, detail=f"Error parsing timestamp column: {str(e)}")
    
    # Check if any transactions found
    if user_df.empty:
        raise HTTPException(status_code=404, detail="No transactions found for this user and date range.")
    
    # Calculate statistics
    max_amt = float(user_df['transaction_amount'].max())
    min_amt = float(user_df['transaction_amount'].min())
    mean_amt = float(user_df['transaction_amount'].mean())
    
    return {
        "user_id": user_id,
        "max_transaction_amount": max_amt,
        "min_transaction_amount": min_amt,
        "mean_transaction_amount": mean_amt,
        "count": len(user_df)
    }

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)