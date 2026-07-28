from typing import Self

from pydantic import model_validator

from src.modules.billing_address.constants import BillingAddressTypesEnum
from src.utils.base_schema import BaseSchema


class BillingAddressBaseSchema(BaseSchema):
    type: BillingAddressTypesEnum
    name: str
    country: str
    state: str | None = None
    city: str
    zip_code: str
    address: str
    tax_number: str | None = None
    user_id: int

    @model_validator(mode="after")
    def check_tax_number_for_company(self) -> Self:
        if self.type == BillingAddressTypesEnum.COMPANY and not self.tax_number:
            raise ValueError("tax_number is required for company billing addresses")
        return self
