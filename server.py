import logging
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import List, Optional
import uvicorn
import json
import os
import uuid

from data_model import Expense


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_dir = 'data'
data_file = os.path.join(data_dir, 'expenses.json')
attachments_dir = os.path.join(data_dir, 'attachments')

def ensure_data_file():
    if not os.path.exists(attachments_dir):
        os.makedirs(attachments_dir)

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(data_file):
        with open(data_file, 'w') as file:
            json.dump([], file)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # run startup event
    ensure_data_file()
    logger.info("Application startup: Data directory and files ensured.")
    yield
    # run shutdown event
    logger.info("Application shutdown: Exiting.")

@app.get("/expenses/", response_model=List[Expense], status_code=status.HTTP_200_OK)
async def query_expenses(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    category: Optional[str] = Query(None, description="Filter by category"),
    currency: Optional[str] = Query(None, description="Filter by currency")
    ) -> List[Expense]:
    try:
        with open(data_file, 'r') as file:
            expenses = json.load(file)

        if tag:
            expenses = [expense for expense in expenses if expense['tag'] == tag]

        if category:
            expenses = [expense for expense in expenses if expense['category'] == category]

        if currency:
            expenses = [expense for expense in expenses if expense['currency'] == currency]
        
        logger.info("Retrieved expenses data.")
        return expenses
    except Exception as e:
        logger.error(f"Error retrieving expenses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/expenses/all", response_model=List[Expense], status_code=status.HTTP_200_OK)
async def gell_all_expenses() -> List[Expense]:
    try:
        with open(data_file, 'r') as file:
            expenses = json.load(file)

        logger.info("Retrieved expenses data.")
        return expenses
    except Exception as e:
        logger.error(f"Error retrieving expenses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/expenses/", response_model=Expense, status_code=status.HTTP_201_CREATED)
async def add_expense(expense: Expense) -> Expense:
    try:
        expense_id = str(uuid.uuid4())
        expense.id = expense_id

        with open(data_file, 'r') as file:
            expenses = json.load(file)
        expenses.append(expense.model_dump())
        with open(data_file, 'w') as file:
            json.dump(expenses, file, indent=4)

        logger.info(f"Added expense: {expense}")
        return expense
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.put("/expenses/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
async def update_expense(expense_id: str, updated_expense: Expense) -> Expense:
    try:
        with open(data_file, 'r') as file:
            expenses = json.load(file)

        for idx, exp in enumerate(expenses):
            if exp['id'] == expense_id:
                updated_expense.id = expense_id
                expenses[idx] = updated_expense.model_dump()

                with open(data_file, 'w') as file:
                    json.dump(expenses, file, indent=4)

                logger.info(f"Updated expense: {updated_expense}")
                return updated_expense

        logger.warning(f"Expense with ID {expense_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    except Exception as e:
        logger.error(f"Error updating expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def delete_expense(expense_id: str) -> dict:
    try:
        with open(data_file, 'r') as file:
            expenses = json.load(file)

        for idx, exp in enumerate(expenses):
            if exp['id'] == expense_id:
                del expenses[idx]
                
                with open(data_file, 'w') as file:
                    json.dump(expenses, file, indent=4)

                logger.info(f"Deleted expense with ID {expense_id}")
                return {"status": "Deleted"}

        logger.warning(f"Expense with ID {expense_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    except Exception as e:
        logger.error(f"Error deleting expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/")
async def root(response_class=HTMLResponse) -> HTMLResponse:
    logger.info("Root endpoint accessed.")
    # return basic html page
    html_content = """
    <html>
        <head>
            <title>Expense track???</title>
        </head>
        <body>
            <h1>Welcome to expense tracker...</h1>
            <p>Access the <a href="/docs">API documentation</a> for more information.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
    # return await gell_all_expenses()

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_server()
