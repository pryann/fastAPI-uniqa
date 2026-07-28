from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from src.database.base_repository import BaseRepository
from src.modules.user.models import User


class BillingAddressRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        return user

    async def get_otp_secret_by_email(self, email: str) -> str | None:
        stmt = select(User.otp_secret).where(User.email == email)
        result = await self.session.execute(stmt)
        otp_secret = result.scalars().first()
        return otp_secret
