from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.billing_address.models import BillingAddress
from src.database.base_repository import BaseRepository
from sqlalchemy.sql import select


class BillingAddressRepository(BaseRepository[BillingAddress]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BillingAddress)

    async def get_all_user_billing_address(self, user_id) -> list[BillingAddress]:
        stmt = select(self.model).where(self.model.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
