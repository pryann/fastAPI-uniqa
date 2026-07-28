from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.pg_database import get_session
from src.exceptions.custom_exceptions import NotFoundError
from src.modules.user.repository import BillingAddressRepository
from src.modules.user.schemas import UserReadSchema
from src.modules.user.service import UserService


def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    user_repository = BillingAddressRepository(session)
    return UserService(user_repository)


async def get_existing_user_by_id(
    user_id: int, user_service: UserService = Depends(get_user_service)
) -> UserReadSchema:
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise NotFoundError()
    return user
