# main.py - FastAPI application entry point
from fastapi import FastAPI, HTTPException
from database import get_database_connection, init_database

# Create FastAPI application instance
app = FastAPI(
    title="Time Deposit API",
    description="REST API for managing time deposits and calculating interest",
    version="1.0.0"
)

# Basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Time Deposit API is running!"}

# Our two required endpoints (placeholder for now)
@app.put("/time-deposits/balances")
async def update_all_balances():
    """Update balances for ALL time deposits in database"""
    try:
        # Test database connection
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM timeDeposits")
        count = cursor.fetchone()[0]
        conn.close()
        
        return {"message": "Update balances endpoint - TODO", "updatedCount": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/time-deposits")
async def get_all_deposits():
    """Get all time deposits with withdrawals"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Fetch all deposits
        cursor.execute("SELECT id, planType, balance, days FROM timeDeposits ORDER BY id")
        deposits = cursor.fetchall()
        
        result = []
        for deposit in deposits:
            deposit_id = deposit[0]
            
            # Fetch withdrawals for this deposit
            cursor.execute("""
                SELECT id, amount, date 
                FROM withdrawals 
                WHERE timeDepositId = ? 
                ORDER BY date
            """, (deposit_id,))
            withdrawals_data = cursor.fetchall()
            
            # Format withdrawals according to the required schema
            withdrawals = []
            for withdrawal in withdrawals_data:
                withdrawals.append({
                    "id": withdrawal[0],
                    "amount": float(withdrawal[1]),
                    "date": withdrawal[2]
                })
            
            # Build the deposit object with withdrawals
            result.append({
                "id": deposit[0],
                "planType": deposit[1],
                "balance": float(deposit[2]),
                "days": deposit[3],
                "withdrawals": withdrawals
            })
        
        conn.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Run the app when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    
    # Initialize database before starting server
    if not init_database():
        print("Warning: Database not initialized. Some endpoints may fail.")
    else:
        print("Database connection verified.")
        
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
