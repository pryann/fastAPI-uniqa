from pydantic import BaseModel


class BaseItem(BaseModel):
    name: str
    quantity: int


class Item(BaseItem):
    id: int


class PartialItem(BaseModel):
    name: str | None = None
    quantity: int | None = None
