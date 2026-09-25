from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    customer_ref: str = Field(..., min_length=1, max_length=40)
    name: str = Field(..., min_length=1, max_length=120)


class PaymentCreate(BaseModel):
    customer_ref: str = Field(..., min_length=1, max_length=40)
    amount: Decimal = Field(..., gt=0)
    transaction_ref: Optional[str] = Field(None, max_length=50)
