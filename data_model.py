from pydantic import BaseModel
from typing import Optional, Literal
from typing import get_args



CURRENCY_LIST = Literal['USD', 'EUR', 'ILS']
CATEGORY_LIST = Literal['', 'Food', 'Bills', 'Transport', 'Car', 'Other']
TAG_LIST = Literal['', 'Work', 'Home', 'Travel', 'Vacation', 'Holiday', 'Weekend']

class Expense(BaseModel):
    """Expense data model"""
    id: Optional[str] = None
    name: Optional[str] = "No name expense"
    category: Optional[CATEGORY_LIST] = ""
    amount: Optional[float] = 0.0
    currency: Optional[CURRENCY_LIST] = "USD"
    tag: Optional[TAG_LIST] = ""
    notes: Optional[str] = ""


# Extract regular lists from Literal types
CURRENCY_LIST_REGULAR = list(get_args(CURRENCY_LIST))
CATEGORY_LIST_REGULAR = list(get_args(CATEGORY_LIST))
TAG_LIST_REGULAR = list(get_args(TAG_LIST))