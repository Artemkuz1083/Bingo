from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    balance: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None


class BalanceUpdateRequest(BaseModel):
    amount: Decimal = Field(gt=0)
