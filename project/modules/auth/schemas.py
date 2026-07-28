from pydantic import EmailStr, Field, model_validator, ConfigDict
from typing_extensions import Self

from src.modules.user.constants import PasswordType, UserRoleEnum, UserStatusEnum
from src.modules.user.schemas import UserBaseSchema
from src.utils.base_schema import BaseSchema


def check_passwords_match(password: str, confirm_password: str) -> bool:
    if password != confirm_password:
        raise ValueError("Passwords do not match")
    return True


class LoginSchema(BaseSchema):
    email: EmailStr
    password: str


class TokenPayloadSchema(BaseSchema):
    id: int
    email: EmailStr
    role: UserRoleEnum

    model_config = ConfigDict(extra="allow")


class OTPVerificationSchema(BaseSchema):
    email: str
    otp_code: str


class UserUpdateEmailSchema(BaseSchema):
    email: EmailStr
    password: PasswordType


class UserUpdatePasswordSchema(BaseSchema):
    old_password: PasswordType
    new_password: PasswordType
    confirm_new_password: PasswordType

    @model_validator(mode="after")
    def validate_passwords_match(self) -> Self:
        check_passwords_match(self.new_password, self.confirm_new_password)
        return self


class ResetPasswordSchema(BaseSchema):
    new_password: PasswordType
    confirm_new_password: PasswordType

    @model_validator(mode="after")
    def validate_passwords_match(self) -> Self:
        check_passwords_match(self.new_password, self.confirm_new_password)
        return self


class UserCreateSchema(UserBaseSchema):
    email: EmailStr
    password: PasswordType
    terms_accepted: bool = Field(
        ..., description="Terms and conditions must be accepted"
    )

    @model_validator(mode="after")
    def validate_terms_accepted(self) -> Self:
        if not self.terms_accepted:
            raise ValueError("Terms and conditions must be accepted")
        return self


class UserCreatedSchema(UserBaseSchema):
    id: int
    email: EmailStr
    role: UserRoleEnum
    status: UserStatusEnum


class EmailSchema(BaseSchema):
    email: EmailStr
