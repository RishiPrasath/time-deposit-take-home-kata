# main.py - FastAPI application entry point
from fastapi import FastAPI

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
@app.post("/deposits/update-balances")
async def update_all_balances():
    return {"message": "Update balances endpoint - TODO", "updatedCount": 0}

@app.get("/deposits")
async def get_all_deposits():
    return {"message": "Get deposits endpoint - TODO", "deposits": []}

# Run the app when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
