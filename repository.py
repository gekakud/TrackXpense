from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi import UploadFile
from data_model import Expense


class ExpenseRepository(ABC):
    '''Expense repository interface'''
    @abstractmethod
    async def get_expenses(self, tag: Optional[str], category: Optional[str], currency: Optional[str]) -> List[Expense]:
        pass

    @abstractmethod
    async def get_all_expenses(self) -> List[Expense]:
        pass

    @abstractmethod
    async def add_expense(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def update_expense(self, expense_id: str, updated_expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def delete_expense(self, expense_id: str) -> dict:
        pass

    @abstractmethod
    async def add_attachment(self, expense_id: str, files: List[UploadFile]) -> dict:
        pass

    @abstractmethod
    async def delete_attachment(self, expense_id: str, file_name: str) -> dict:
        pass

    @abstractmethod
    async def download_attachment(self, expense_id: str, file_name: str) -> Optional[str]:
        pass
