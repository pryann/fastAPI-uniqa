import uvicorn
from fastapi import FastAPI, status
from schemas import BaseItem, Item, PartialItem
from database import items
from utils import find_item_or_raise, generate_new_id


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello fastAPI"}


# open("text.txt", "r", endcoding="utf-8")
# GET http://localhost:8000/items
@app.get("/items", response_model=list[Item])
async def get_items():
    return items


# GET http://localhost:8000/items/1
@app.get("/items/{item_id}", response_model=Item)
async def find_item(item_id: int):
    return find_item_or_raise(item_id, items)


# {"name": "item 4", "quantity": 40}
# POST http://localhost:8000/items
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(create_item_payload: BaseItem):
    new_id = generate_new_id(items)
    # items.append(Item(id=new_id, name=item.name, quantity=item.quantity))
    # A ** dict-en értelmezhető, kicsomagolja az objektumot
    # de mivel BaseItem tpusú adat van a model_dump() metódus visszaadja a dict-et, így a **-al kicsomagoljuk az adatokat
    items.append(Item(id=new_id, **create_item_payload.model_dump()))
    return items[-1]


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, update_item_payload: BaseItem):
    item = find_item_or_raise(item_id, items)
    for key, value in update_item_payload.model_dump().items():
        setattr(item, key, value)
    return item


# item = { id=1, name="item 1", quantity=10 }
# update_item_payload = { name="item 1 updated", quantity=10 }
# item["name"] = "item 1 updated"
# item["quantity"] = 10


@app.patch("/items/{item_id}", response_model=Item)
async def partial_update_item(item_id: int, update_item_payload: PartialItem):
    item = find_item_or_raise(item_id, items)
    for key, value in update_item_payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    return item


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(item_id: int):
    item = find_item_or_raise(item_id, items)
    items.remove(item)
    # itemsből az itemet törljétek ki


if __name__ == "__main__":
    # ez a kódrész csak akkor fut le ha ezt a filet futtatjuk direktben, és nem importáljuk
    # amennyiben importáljuk, nem fut le ez a kódrész
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
