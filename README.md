# FastAPI


## Telepítés
- Virtuális környezet létrehozása: `python -m venv venv`
- .gitignore file-ba a venv mappa felvétele
- Virtuális környezet aktiválása: `.\venv\Scipts\Activate.ps1`
- Ha cmd-t használtok akkor a bat file kell
- Függőség telepítése: `pip install "fastapi[standard]"`
- Függőségek file-ba írása: `pip freeze > requirements.txt`
- Függőségek telepítése fileból: `pip install -r requirements.txt` (előtte venv aktiválása)

## Típusok

### Alap típusok
- int
- float
- bool
- str
- list: list[int]
- tuple: tuple[str, str, int]
- dict: dict[str, int]
- set: set[bytes]

### Egyéb típusok:
- UUID
- datetime.datetime
- datetime.date
- datetime.time
- datetime.timedelta
- frozenset
- bytes
- Decimal
- .....


### Különleges típusok
- union: str | int
- default: str | None = None
- class:
  ```python
  class Person:
    def __init__(self, name:str):
      self.name = name
  ```
- Annotated: 
```python
from typing import Annotated

def greetings(name: Annotated[str, "this is a metadata"]) -> str:
  return f"Hi {name}"
```

## Pydantic