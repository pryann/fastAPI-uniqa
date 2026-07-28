from enum import Enum
from typing import Annotated

from pydantic import constr

from src.config import get_settings


class UserStatusEnum(str, Enum):
    VERIFIED = "VERIFIED"
    BANNED = "BANNED"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"


class UserRoleEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


settings = get_settings()
PasswordType = Annotated[str, constr(pattern=rf"{settings.PASSWORD_REGEX}")]
