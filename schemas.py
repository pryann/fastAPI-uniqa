from pydantic import BaseModel, EmailStr, Field

from typing import Literal


class BaseItem(BaseModel):
    name: str
    quantity: int
    company_id: int


class Item(BaseItem):
    id: int


class PartialItem(BaseModel):
    name: str | None = None
    quantity: int | None = None
    company_id: int | None = None


class FilterParams(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    order_by: Literal["id", "quantity"] = "id"
    order_direction: Literal["asc", "desc"] = "asc"


class Registration(BaseModel):
    username: str
    password: str
    email: EmailStr
