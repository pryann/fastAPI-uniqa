from typing import List

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.custom_base_model import CustomBase
from src.modules.billing_address.models import BillingAddress
from src.modules.user.constants import UserRoleEnum, UserStatusEnum


class User(CustomBase):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(191), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    fullname: Mapped[str] = mapped_column(String(191))
    terms_accepted: Mapped[bool] = mapped_column(Boolean)
    newsletter_subscription: Mapped[bool] = mapped_column(Boolean)
    password: Mapped[str] = mapped_column(String(191))
    role: Mapped[UserRoleEnum] = mapped_column(
        Enum(UserRoleEnum),
        default=UserRoleEnum.USER.value,
    )
    status: Mapped[UserStatusEnum] = mapped_column(
        Enum(UserStatusEnum),
        default=UserStatusEnum.VERIFIED.value,
    )

    billing_address: Mapped[List["BillingAddress"]] = relationship(lazy="selectin")
