import logging
from fastapi import FastAPI, HTTPException, status, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import uvicorn
import json
import os
import uuid

from data_model import Expense


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

data_dir = 'data'
expenses_data_file = os.path.join(data_dir, 'expenses.json')
attachments_dir = os.path.join(data_dir, 'attachments')

def ensure_data_file():
    # Ensure data directory and files exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(attachments_dir):
        os.makedirs(attachments_dir)

    if not os.path.exists(expenses_data_file):
        with open(expenses_data_file, 'w') as file:
            json.dump([], file)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    ensure_data_file()
    logger.info("Application startup: Data directory and files ensured.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown.")

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


@app.get("/expenses/", response_model=List[Expense], status_code=status.HTTP_200_OK)
async def query_expenses(
    tag: Optional[str] = Query(None, description="Filter by tag"),
    category: Optional[str] = Query(None, description="Filter by category"),
    currency: Optional[str] = Query(None, description="Filter by currency")
    ) -> List[Expense]:
    try:
        with open(expenses_data_file, 'r') as file:
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
        with open(expenses_data_file, 'r') as file:
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

        # Create a directory for attachments
        expense_attachment_dir = os.path.join(attachments_dir, expense_id)
        os.makedirs(expense_attachment_dir, exist_ok=True)

        with open(expenses_data_file, 'r') as file:
            expenses = json.load(file)
        expenses.append(expense.model_dump())
        with open(expenses_data_file, 'w') as file:
            json.dump(expenses, file, indent=4)

        logger.info(f"Added expense: {expense}")
        return expense
    except Exception as e:
        logger.error(f"Error adding expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.put("/expenses/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
async def update_expense(expense_id: str, updated_expense: Expense) -> Expense:
    try:
        with open(expenses_data_file, 'r') as file:
            expenses = json.load(file)

        for idx, exp in enumerate(expenses):
            if exp['id'] == expense_id:
                updated_expense.id = expense_id
                expenses[idx] = updated_expense.model_dump()

                with open(expenses_data_file, 'w') as file:
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
        with open(expenses_data_file, 'r') as file:
            expenses = json.load(file)

        for idx, exp in enumerate(expenses):
            if exp['id'] == expense_id:
                # Delete all attachments
                expense_attachment_dir = os.path.join(attachments_dir, expense_id)
                for attachment in exp.get('attachments', []):
                    file_path = os.path.join(expense_attachment_dir, attachment)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                if os.path.exists(expense_attachment_dir):
                    os.rmdir(expense_attachment_dir)

                del expenses[idx]
                
                with open(expenses_data_file, 'w') as file:
                    json.dump(expenses, file, indent=4)

                logger.info(f"Deleted expense with ID {expense_id}")
                return {"status": "Deleted"}

        logger.warning(f"Expense with ID {expense_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    except Exception as e:
        logger.error(f"Error deleting expense: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/expenses/{expense_id}/attachments", status_code=status.HTTP_201_CREATED)
async def add_attachment(expense_id: str, files: List[UploadFile] = File([])) -> dict:
    try:
        with open(expenses_data_file, 'r') as file:
            expenses = json.load(file)

        for exp in expenses:
            if exp['id'] == expense_id:
                file_paths = exp.get('attachments', [])
                expense_attachment_dir = os.path.join(attachments_dir, expense_id)
                os.makedirs(expense_attachment_dir, exist_ok=True)
                for file in files:
                    file_path = os.path.join(expense_attachment_dir, file.filename)
                    with open(file_path, "wb") as f:
                        f.write(file.file.read())
                    file_paths.append(file.filename)
                exp['attachments'] = file_paths

                with open(expenses_data_file, 'w') as file:
                    json.dump(expenses, file, indent=4)

                logger.info(f"Added attachments to expense with ID {expense_id}")
                return {"status": "Attachments added"}

        logger.warning(f"Expense with ID {expense_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    except Exception as e:
        logger.error(f"Error adding attachments: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete("/expenses/{expense_id}/attachments", status_code=status.HTTP_200_OK)
async def delete_attachment(expense_id: str, file_name: str) -> dict:
    try:
        with open(expenses_data_file, 'r') as file:
            expenses = json.load(file)

        for exp in expenses:
            if exp['id'] == expense_id:
                expense_attachment_dir = os.path.join(attachments_dir, expense_id)
                file_path = os.path.join(expense_attachment_dir, file_name)
                if file_name in exp.get('attachments', []):
                    exp['attachments'].remove(file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if not os.listdir(expense_attachment_dir):
                        os.rmdir(expense_attachment_dir)

                    with open(expenses_data_file, 'w') as file:
                        json.dump(expenses, file, indent=4)

                    logger.info(f"Deleted attachment from expense with ID {expense_id}")
                    return {"status": "Attachment deleted"}

                logger.warning(f"Attachment not found in expense with ID {expense_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

        logger.warning(f"Expense with ID {expense_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    except Exception as e:
        logger.error(f"Error deleting attachment: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/expenses/{expense_id}/attachments/download", response_class=FileResponse)
async def download_attachment(expense_id: str, file_name: str) -> FileResponse:
    try:
        with open(expenses_data_file, 'r') as file:
            expenses = json.load(file)

        for exp in expenses:
            if exp['id'] == expense_id:
                expense_attachment_dir = os.path.join(attachments_dir, expense_id)
                file_path = os.path.join(expense_attachment_dir, file_name)
                if file_name in exp.get('attachments', []):
                    if os.path.exists(file_path):
                        return FileResponse(file_path, filename=file_name)

                logger.warning(f"Attachment not found in expense with ID {expense_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

        logger.warning(f"Expense with ID {expense_id} not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    except Exception as e:
        logger.error(f"Error downloading attachment: {str(e)}")
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
