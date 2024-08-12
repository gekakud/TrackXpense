import logging
from fastapi import FastAPI, HTTPException, status, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Optional
import uvicorn

from data_model import Expense
from fs_expense_repository import FileExpenseRepository

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
data_dir = 'data'

# Initialize singleton repository
expense_repository = FileExpenseRepository(data_dir)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    expense_repository.ensure_data_file()
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
    return await expense_repository.get_expenses(tag, category, currency)

@app.get("/expenses/all", response_model=List[Expense], status_code=status.HTTP_200_OK)
async def get_all_expenses() -> List[Expense]:
    return await expense_repository.get_all_expenses()

@app.post("/expenses/", response_model=Expense, status_code=status.HTTP_201_CREATED)
async def add_expense(expense: Expense) -> Expense:
    return await expense_repository.add_expense(expense)

@app.put("/expenses/{expense_id}", response_model=Expense, status_code=status.HTTP_200_OK)
async def update_expense(expense_id: str, updated_expense: Expense) -> Expense:
    return await expense_repository.update_expense(expense_id, updated_expense)

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def delete_expense(expense_id: str) -> dict:
    return await expense_repository.delete_expense(expense_id)

@app.post("/expenses/{expense_id}/attachments", status_code=status.HTTP_201_CREATED)
async def add_attachment(expense_id: str, files: List[UploadFile] = File([])) -> dict:
    return await expense_repository.add_attachment(expense_id, files)

@app.delete("/expenses/{expense_id}/attachments", status_code=status.HTTP_200_OK)
async def delete_attachment(expense_id: str, file_name: str) -> dict:
    return await expense_repository.delete_attachment(expense_id, file_name)

@app.get("/expenses/{expense_id}/attachments/download", response_class=FileResponse)
async def download_attachment(expense_id: str, file_name: str) -> FileResponse:
    file_path = await expense_repository.download_attachment(expense_id, file_name)
    if file_path:
        return FileResponse(file_path, filename=file_name)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

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
    # return await get_all_expenses()

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_server()
