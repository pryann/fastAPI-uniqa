from schemas import Item
from fastapi import HTTPException


# CRUD operations: Create, Read, Update, Delete
def generate_new_id(items: list[Item]) -> int:
    return max([item.id for item in items], default=0) + 1


def find_item_or_raise(item_id: int, items: list[Item]) -> Item:
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")
