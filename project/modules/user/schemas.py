from pydantic import EmailStr

from src.modules.user.constants import UserRoleEnum, UserStatusEnum
from src.utils.base_schema import BaseSchema


class UserBaseSchema(BaseSchema):
    username: str
    fullname: str
    newsletter_subscription: bool


class UserReadSchema(UserBaseSchema):
    id: int
    email: EmailStr
    status: UserStatusEnum
    role: UserRoleEnum
