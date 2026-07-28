from src.exceptions.custom_exceptions import NotFoundError
from src.modules.billing_address.repository import BillingAddressRepository
from src.modules.billing_address.schemas import BillingAddressBaseSchema


class BillingAddressService:
    def __init__(self, billing_address_repository: BillingAddressRepository):
        self.billing_address_repository = billing_address_repository

    async def get_all_user_billing_address(self, user_id: int) -> list[BillingAddressBaseSchema]:
        return await self.billing_address_repository.get_all_user_billing_address(user_id)

    async def get_billing_address_by_id(self, billing_address_id: int) -> BillingAddressBaseSchema:
        billing_address = await self.billing_address_repository.get_by_id(billing_address_id)
        if billing_address is None:
            raise NotFoundError("BillingAddress not found")
        return billing_address

    async def add_billing_address(self, billing_address: BillingAddressBaseSchema) -> BillingAddressBaseSchema:
        return await self.billing_address_repository.create(billing_address)

    async def update_billing_address(
        self, billing_address_id: int, billing_address_data: BillingAddressBaseSchema
    ) -> BillingAddressBaseSchema:
        return await self.billing_address_repository.update(billing_address_id, billing_address_data)

    async def delete_billing_address(self, billing_address_id: int) -> None:
        await self.billing_address_repository.delete(billing_address_id)
        return
