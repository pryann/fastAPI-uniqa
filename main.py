import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class BaseItem(BaseModel):
    name: str
    quantity: int


class Item(BaseItem):
    id: int


class PartialItem(BaseModel):
    name: str | None = None
    quantity: int | None = None


items = [
    Item(id=1, name="Item 1", quantity=10),
    Item(id=2, name="Item 2", quantity=20),
    Item(id=3, name="Item 3", quantity=30),
]


@app.get("/")
async def root():
    return {"message": "Hello fastAPI"}


# CRUD operations: Create, Read, Update, Delete


def find_item_or_raise(item_id: int) -> Item:
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


# open("text.txt", "r", endcoding="utf-8")
# GET http://localhost:8000/items
@app.get("/items", response_model=list[Item])
async def get_items():
    return items


# GET http://localhost:8000/items/1
@app.get("/items/{item_id}", response_model=Item)
async def find_item(item_id: int):
    return find_item_or_raise(item_id)


# {"name": "item 4", "quantity": 40}
# POST http://localhost:8000/items
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(create_item_payload: BaseItem):
    new_id = max([item.id for item in items], default=0) + 1
    # items.append(Item(id=new_id, name=item.name, quantity=item.quantity))
    # A ** dict-en értelmezhető, kicsomagolja az objektumot
    # de mivel BaseItem tpusú adat van a model_dump() metódus visszaadja a dict-et, így a **-al kicsomagoljuk az adatokat
    items.append(Item(id=new_id, **create_item_payload.model_dump()))
    return items[-1]


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, update_item_payload: BaseItem):
    item = find_item_or_raise(item_id)
    for key, value in update_item_payload.model_dump().items():
        setattr(item, key, value)
    return item


# item = { id=1, name="item 1", quantity=10 }
# update_item_payload = { name="item 1 updated", quantity=10 }
# item["name"] = "item 1 updated"
# item["quantity"] = 10


@app.patch("/items/{item_id}", response_model=Item)
async def partial_update_item(item_id: int, update_item_payload: PartialItem):
    for item in items:
        if item.id == item_id:
            for key, value in update_item_payload.model_dump(
                exclude_unset=True
            ).items():
                setattr(item, key, value)
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(item_id: int):
    for index, item in enumerate(items):
        if item.id == item_id:
            items.pop(index)
            return
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    # ez a kódrész csak akkor fut le ha ezt a filet futtatjuk direktben, és nem importáljuk
    # amennyiben importáljuk, nem fut le ez a kódrész
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
