import os
import json
import uuid
from typing import List, Optional
from fastapi import HTTPException, status, UploadFile
from data_model import Expense
from repository import ExpenseRepository

class FileExpenseRepository(ExpenseRepository):
    _instance = None

    def __new__(cls, data_dir: str):
        if cls._instance is None:
            cls._instance = super(FileExpenseRepository, cls).__new__(cls)
            cls._instance.init(data_dir)
        return cls._instance

    def init(self, data_dir: str):
        self.data_dir = data_dir
        self.expenses_data_file = os.path.join(data_dir, 'expenses.json')
        self.attachments_dir = os.path.join(data_dir, 'attachments')
        self.ensure_data_file()

    def ensure_data_file(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        if not os.path.exists(self.attachments_dir):
            os.makedirs(self.attachments_dir)

        if not os.path.exists(self.expenses_data_file):
            with open(self.expenses_data_file, 'w') as file:
                json.dump([], file)

    async def get_expenses(self, tag: Optional[str], category: Optional[str], currency: Optional[str]) -> List[Expense]:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)

            if tag:
                expenses = [expense for expense in expenses if expense['tag'] == tag]

            if category:
                expenses = [expense for expense in expenses if expense['category'] == category]

            if currency:
                expenses = [expense for expense in expenses if expense['currency'] == currency]

            return [Expense(**expense) for expense in expenses]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_all_expenses(self) -> List[Expense]:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)
            return [Expense(**expense) for expense in expenses]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def add_expense(self, expense: Expense) -> Expense:
        try:
            expense_id = str(uuid.uuid4())
            expense.id = expense_id

            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)
            expenses.append(expense.dict())
            with open(self.expenses_data_file, 'w') as file:
                json.dump(expenses, file, indent=4)

            return expense
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def update_expense(self, expense_id: str, updated_expense: Expense) -> Expense:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)

            for idx, exp in enumerate(expenses):
                if exp['id'] == expense_id:
                    updated_expense.id = expense_id
                    expenses[idx] = updated_expense.dict()

                    with open(self.expenses_data_file, 'w') as file:
                        json.dump(expenses, file, indent=4)

                    return updated_expense

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def delete_expense(self, expense_id: str) -> dict:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)

            for idx, exp in enumerate(expenses):
                if exp['id'] == expense_id:
                    expense_attachment_dir = os.path.join(self.attachments_dir, expense_id)
                    for attachment in exp.get('attachments', []):
                        file_path = os.path.join(expense_attachment_dir, attachment)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    if os.path.exists(expense_attachment_dir):
                        os.rmdir(expense_attachment_dir)

                    del expenses[idx]

                    with open(self.expenses_data_file, 'w') as file:
                        json.dump(expenses, file, indent=4)

                    return {"status": "Deleted"}

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def add_attachment(self, expense_id: str, files: List[UploadFile]) -> dict:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)

            for exp in expenses:
                if exp['id'] == expense_id:
                    file_paths = exp.get('attachments', [])
                    expense_attachment_dir = os.path.join(self.attachments_dir, expense_id)
                    os.makedirs(expense_attachment_dir, exist_ok=True)
                    for file in files:
                        file_path = os.path.join(expense_attachment_dir, file.filename)
                        with open(file_path, "wb") as f:
                            f.write(file.file.read())
                        file_paths.append(file.filename)
                    exp['attachments'] = file_paths

                    with open(self.expenses_data_file, 'w') as file:
                        json.dump(expenses, file, indent=4)

                    return {"status": "Attachments added"}

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def delete_attachment(self, expense_id: str, file_name: str) -> dict:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)

            for exp in expenses:
                if exp['id'] == expense_id:
                    expense_attachment_dir = os.path.join(self.attachments_dir, expense_id)
                    file_path = os.path.join(expense_attachment_dir, file_name)
                    if file_name in exp.get('attachments', []):
                        exp['attachments'].remove(file_name)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        if not os.listdir(expense_attachment_dir):
                            os.rmdir(expense_attachment_dir)

                        with open(self.expenses_data_file, 'w') as file:
                            json.dump(expenses, file, indent=4)

                        return {"status": "Attachment deleted"}

                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def download_attachment(self, expense_id: str, file_name: str) -> Optional[str]:
        try:
            with open(self.expenses_data_file, 'r') as file:
                expenses = json.load(file)

            for exp in expenses:
                if exp['id'] == expense_id:
                    expense_attachment_dir = os.path.join(self.attachments_dir, expense_id)
                    file_path = os.path.join(expense_attachment_dir, file_name)
                    if file_name in exp.get('attachments', []):
                        if os.path.exists(file_path):
                            return file_path

                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
