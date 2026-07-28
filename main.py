from datetime import datetime, timezone
from typing import Annotated
from pathlib import Path

import uvicorn
from fastapi import (
    FastAPI,
    File,
    Form,
    Query,
    status,
    Header,
    Response,
    Body,
    UploadFile,
    Cookie,
)
from fastapi.staticfiles import StaticFiles

from database import items
from schemas import BaseItem, FilterParams, Item, PartialItem, Registration
from utils import find_item_or_raise, generate_new_id


app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root(accept_language: Annotated[str | None, Header()] = None):
    lang = accept_language.split(",")[0][:2] if accept_language else "en"
    massage = {"en": "hi", "hu": "hello"}
    return {"message": massage.get(lang, "hi")}


# not a real login, no pass, no validation, just a simple example for creating a cookie
@app.post("/login")
async def login(response: Response, username: Annotated[str, Body(embed=True)]):
    response.set_cookie(
        key="session_id",
        value=f"session_{username}_{datetime.now(tz=timezone.utc).timestamp()}",
        max_age=3600,
        httponly=True,
    )
    return {"message": "logged in successfully"}


@app.get("/profile")
async def profile(session_id: Annotated[str | None, Cookie()] = None):
    if not session_id:
        return {"message": "not logged in"}
    return {"message": "user profile"}


# open("text.txt", "r", encoding="utf-8")
# GET http://localhost:8000/items?offset=0&limit=10&order_by=quantity&order_direction=asc
@app.get("/items", response_model=list[Item])
async def get_items(query: Annotated[FilterParams, Query()]):
    # def sort_by(item):
    #     return getattr(item, query.order_by)
    sorted_items = sorted(
        items,
        key=lambda item: getattr(item, query.order_by),
        reverse=query.order_direction == "desc",
    )
    return sorted_items[query.offset : query.offset + query.limit]


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


@app.get("/companies/{company_id}/items", response_model=list[Item])
def get_items_by_company(company_id: int):
    return [item for item in items if item.company_id == company_id]


@app.get("/companies/{company_id}/items/{item_id}", response_model=Item)
def get_item_by_company_and_id(company_id: int, item_id: int):
    find_item_or_raise(item_id, items)
    return [i for i in items if i.company_id == company_id and i.id == item_id]


@app.post("/upload")
def upload_and_save(uploaded_file: UploadFile):
    self_filename = Path(uploaded_file.filename).name
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / self_filename
    with open(file_path, "wb") as f:
        content = uploaded_file.file.read()
        f.write(content)
    return {"filename": self_filename, "path": str(file_path)}


@app.post("/registration")
async def registration(form_data: Annotated[Registration, Form()]):
    return {
        "message": "Registration successful",
        "data": form_data.model_dump(exclude={"password"}),
    }


if __name__ == "__main__":
    # ez a kódrész csak akkor fut le ha ezt a filet futtatjuk direktben, és nem importáljuk
    # amennyiben importáljuk, nem fut le ez a kódrész
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
