# Architecture Description

## 1. Client (PyQt)
**Role:** Interacts with the FastAPI server for CRUD operations on expenses and attachments.

**Components:**
- **Expense List**
- **Expense Details**
- **Expense Form**
- **Attachment Management**

## 2. FastAPI Server
**Role:** Provides RESTful API endpoints to manage expenses and attachments.

**Components:**

**Endpoints:**
- `/expenses/` (GET): Retrieve expenses with optional filtering.
- `/expenses/all` (GET): Retrieve all expenses.
- `/expenses/` (POST): Add a new expense.
- `/expenses/{expense_id}` (PUT): Update an existing expense.
- `/expenses/{expense_id}` (DELETE): Delete an existing expense.
- `/expenses/{expense_id}/attachments` (POST): Add attachments to an expense.
- `/expenses/{expense_id}/attachments` (DELETE): Delete an attachment from an expense.
- `/expenses/{expense_id}/attachments/download` (GET): Download an attachment.

## 3. Repository
**Role:** Abstracts data management operations, enabling the use of different storage mechanisms.

**Components:**
- **Interface (ExpenseRepository):** Defines methods for data management.
- **Implementation (FileExpenseRepository):** Manages data using local file storage.

## 4. Local File Storage
**Role:** Stores expense data and attachments.

**Components:**

**Data Files:**
- `expenses.json`: Stores expense data.
  
**Attachment Files:**
- `/attachments/{expense_id}/`: Stores attachment files for each expense.
