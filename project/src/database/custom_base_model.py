import uuid

from humps import camel
from sqlalchemy import DateTime, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, registry


def to_camel(string):
    return camel.case(string)


mapper_registry = registry()
Base = mapper_registry.generate_base()


class CustomBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=False,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
