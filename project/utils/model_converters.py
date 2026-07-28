from typing import Type

from pydantic import BaseModel
from sqlalchemy.inspection import inspect


def convert_sqlalchemy_to_pydantic(
    sqlalchemy_instance, pydantic_model: Type[BaseModel], include_relationships: bool = False
):
    pydantic_fields = set(pydantic_model.__annotations__.keys())
    sqlalchemy_data = {
        column.name: getattr(sqlalchemy_instance, column.name) for column in sqlalchemy_instance.__table__.columns
    }
    filtered_data = {key: value for key, value in sqlalchemy_data.items() if key in pydantic_fields}
    if include_relationships:
        for relationship in inspect(sqlalchemy_instance).mapper.relationships:
            related_instance = getattr(sqlalchemy_instance, relationship.key)
            if related_instance is not None:
                if isinstance(related_instance, list):
                    related_data = [convert_sqlalchemy_to_pydantic(item, pydantic_model) for item in related_instance]
                else:
                    related_data = convert_sqlalchemy_to_pydantic(related_instance, pydantic_model)
                filtered_data[relationship.key] = related_data

    return pydantic_model(**filtered_data)


def convert_pydantic_to_sqlalchemy(pydantic_instance, sqlalchemy_model: Type[BaseModel]):
    sqlalchemy_fields = set(sqlalchemy_model.__table__.columns.keys())
    pydantic_dict = pydantic_instance.module_dump()
    filtered_data = {key: value for key, value in pydantic_dict.items() if key in sqlalchemy_fields}
    return sqlalchemy_model(**filtered_data)
