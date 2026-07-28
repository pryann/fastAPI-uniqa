from sqlalchemy import Enum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.custom_base_model import CustomBase
from src.modules.billing_address.constants import BillingAddressTypesEnum


class BillingAddress(CustomBase):
    __tablename__ = "billing_address"

    name: Mapped[str] = mapped_column(String(191))
    country: Mapped[str] = mapped_column(String(191))
    state: Mapped[str] = mapped_column(String(191))
    city: Mapped[str] = mapped_column(String(191))
    zip_code: Mapped[str] = mapped_column(String(10))
    address: Mapped[str] = mapped_column(String(191))
    type: Mapped[BillingAddressTypesEnum] = mapped_column(
        Enum(BillingAddressTypesEnum),
        default=BillingAddressTypesEnum.INDIVIDUAL.value,
    )
    tax_number: Mapped[str | None] = mapped_column(String(10), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
