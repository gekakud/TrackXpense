from abc import ABC, abstractmethod
from typing import List, Optional

from data_model import Expense

class ExpenseRepository(ABC):
    @abstractmethod
    async def get_expenses(self, tag: Optional[str] = None, category: Optional[str] = None, currency: Optional[str] = None) -> List[Expense]:
        pass

    @abstractmethod
    async def get_all_expenses(self) -> List[Expense]:
        pass

    @abstractmethod
    async def add_expense(self, expense: Expense) -> Expense:
        pass

    @abstractmethod
    async def update_expense(self, expense_id: str, updated_expense: Expense) -> Optional[Expense]:
        pass

    @abstractmethod
    async def delete_expense(self, expense_id: str) -> bool:
        pass
