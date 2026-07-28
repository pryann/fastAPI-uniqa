from src.exceptions.custom_exceptions import NotFoundError
from src.modules.user.constants import UserStatusEnum
from src.modules.user.repository import BillingAddressRepository
from src.modules.user.schemas import UserBaseSchema, UserReadSchema


class UserService:
    def __init__(self, user_repository: BillingAddressRepository):
        self.user_repository = user_repository

    async def get_users(self) -> list[UserReadSchema]:
        return await self.user_repository.get_all()

    async def get_user_by_id(self, user_id: int) -> UserReadSchema:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def update_user(
        self, user_id: int, user_data: UserBaseSchema
    ) -> UserReadSchema:
        existing_user = await self.user_repository.get_by_id(user_id)
        update_data = user_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(existing_user, key, value)

        updated_user = await self.user_repository.update(user_id, existing_user)

        return updated_user

    async def delete_user(self, user_id: int) -> None:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        user.status = UserStatusEnum.DELETED.value
        await self.user_repository.update(user)
        return None
