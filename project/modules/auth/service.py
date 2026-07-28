from datetime import timedelta

import bcrypt
import pyotp

from src.config import Settings
from src.exceptions.custom_exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    NotFoundError,
)
from src.modules.auth.schemas import (
    LoginSchema,
    TokenPayloadSchema,
    UserCreatedSchema,
    UserCreateSchema,
    UserUpdatePasswordSchema,
)
from src.modules.user.constants import UserStatusEnum
from src.modules.user.models import User
from src.modules.user.repository import BillingAddressRepository
from src.utils.model_converters import convert_sqlalchemy_to_pydantic
from src.utils.token_handler import TokenHandler


class AuthService:
    def __init__(
        self,
        user_repository: BillingAddressRepository,
        token_handler: TokenHandler,
        settings: Settings,
    ):
        self.user_repository = user_repository
        self.token_handler = token_handler
        self.settings = settings

    def __hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        password_bytes = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password=password_bytes, salt=salt)
        return hashed_password.decode("utf-8")

    def __verify_password(self, plain_password: str, hashed_password: str) -> bool:
        plain_password_bytes = plain_password.encode("utf-8")
        hashed_password_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

    async def __verify_registration_otp(self, email: str, otp_code: str):
        otp_secret = await self.user_repository.get_otp_secret_by_email(email)
        totp = pyotp.TOTP(otp_secret)
        is_valid = totp.verify(otp_code, valid_window=2)
        return is_valid

    def __generate_access_token(self, user: TokenPayloadSchema) -> str:
        return self.token_handler.generate_token(
            user,
            timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            self.settings.ACCESS_TOKEN_SECRET_KEY,
            self.settings.ACCESS_TOKEN_ALGORITHM,
        )

    async def __decode_access_token(self, access_token: str) -> dict[str, str]:
        return self.token_handler.decode_token(
            access_token,
            self.settings.ACCESS_TOKEN_SECRET_KEY,
            self.settings.ACCESS_TOKEN_ALGORITHM,
        )

    def __generate_refresh_token(self, user: TokenPayloadSchema) -> str:
        return self.token_handler.generate_token(
            user,
            timedelta(minutes=self.settings.REFRESH_TOKEN_EXPIRE_MINUTES),
            self.settings.REFRESH_TOKEN_SECRET_KEY,
            self.settings.REFRESH_TOKEN_ALGORITHM,
        )

    def __decode_refresh_token(self, refresh_token: str) -> dict[str, str]:
        return self.token_handler.decode_token(
            refresh_token,
            self.settings.REFRESH_TOKEN_SECRET_KEY,
            self.settings.REFRESH_TOKEN_ALGORITHM,
        )

    def __generate_password_reset_token(self, user: TokenPayloadSchema) -> str:
        return self.token_handler.generate_token(
            user,
            timedelta(minutes=self.settings.RESET_TOKEN_EXPIRE_MINUTES),
            self.settings.RESET_TOKEN_SECRET_KEY,
            self.settings.RESET_TOKEN_ALGORITHM,
        )

    async def __decode_password_reset_token(self, password_reset_token: str) -> TokenPayloadSchema:
        decoded_data = self.token_handler.decode_token(
            password_reset_token, self.settings.RESET_TOKEN_SECRET_KEY, self.settings.RESET_TOKEN_ALGORITHM
        )
        return TokenPayloadSchema(**decoded_data)

    async def get_current_user_from_access_token(self, access_token: str) -> TokenPayloadSchema:
        decoded = await self.__decode_access_token(access_token)
        return await self.user_repository.get_user_by_email(decoded["email"])

    async def regenerate_auth_tokens(self, refresh_token: str) -> dict[str, str]:
        if not refresh_token:
            raise AuthenticationError("Refresh token is missing")

        is_blacklisted = await self.token_handler.is_blacklisted_refresh_token(refresh_token)
        if is_blacklisted:
            raise AuthenticationError("Refresh token is invalid")

        decoded = self.__decode_refresh_token(refresh_token)
        db_user = await self.user_repository.get_user_by_email(decoded["email"])
        await self.token_handler.add_refresh_token_to_blacklist(refresh_token)

        token_payload = convert_sqlalchemy_to_pydantic(db_user, TokenPayloadSchema)
        return {
            "access_token": self.__generate_access_token(token_payload),
            "refresh_token": self.__generate_refresh_token(token_payload),
        }

    async def login(self, user: LoginSchema) -> dict[str, str]:
        db_user = await self.user_repository.get_user_by_email(user.email)
        if not db_user:
            raise NotFoundError("User not found")
        if not self.__verify_password(user.password, db_user.password):
            raise AuthenticationError("Incorrect email or password")
        token_payload = convert_sqlalchemy_to_pydantic(db_user, TokenPayloadSchema)
        return {
            "access_token": self.__generate_access_token(token_payload),
            "refresh_token": self.__generate_refresh_token(token_payload),
        }

    async def verify_registration(self, email: str, otp_code: str):
        is_valid = await self.__verify_registration_otp(email, otp_code)
        if not is_valid:
            raise AuthenticationError("Invalid OTP code")
        db_user = await self.user_repository.get_user_by_email(email)
        db_user.status = UserStatusEnum.VERIFIED.value
        updated_user = await self.user_repository.update(db_user.id, db_user)
        return updated_user

    def generate_otp_code(self, otp_secret: str) -> str:
        totp = pyotp.TOTP(otp_secret)
        otp_code = totp.now()
        return otp_code

    async def create_user(self, user_data: UserCreateSchema) -> UserCreatedSchema:
        is_exists_by_email = await self.user_repository.get_user_by_email(user_data.email)

        if is_exists_by_email:
            raise AlreadyExistsError("User already exists with this email")

        user_data.password = self.__hash_password(user_data.password)
        user_data.otp_secret = pyotp.random_base32()

        user_data_dict = user_data.model_dump(exclude={"confirm_password"})
        user_db_model = User(**user_data_dict)
        result = await self.user_repository.create(user_db_model)

        return result

    async def resend_registration_email(self, email: str) -> tuple[User, str]:
        user = await self.user_repository.get_user_by_email(email)
        if user.status != UserStatusEnum.UNVERIFIED.value:
            raise AlreadyExistsError("User registration already verified")

        otp_code = self.generate_otp_code(user.otp_secret)
        return user, otp_code

    async def request_password_reset(self, email: str) -> tuple[User, str]:
        db_user = await self.user_repository.get_user_by_email(email)
        if not db_user:
            raise NotFoundError("User not found")

        token_payload = convert_sqlalchemy_to_pydantic(db_user, TokenPayloadSchema)
        request_token = self.__generate_password_reset_token(token_payload)
        return db_user, request_token

    async def reset_password(self, token: str, new_password: str) -> User:
        user_from_token = await self.__decode_password_reset_token(token)
        db_user = await self.user_repository.get_by_id(user_from_token["id"])
        if not db_user:
            raise NotFoundError("User not found")

        db_user.password = self.__hash_password(new_password)
        updated_user = await self.user_repository.update(db_user.id, db_user)
        return updated_user

    async def change_password(self, access_token: str, password_data: UserUpdatePasswordSchema) -> User:
        user_from_token = await self.__decode_access_token(access_token)
        db_user = await self.user_repository.get_by_id(user_from_token["id"])

        print(password_data.new_password, db_user.password)

        if not db_user:
            raise NotFoundError("User not found")

        if not self.__verify_password(password_data.old_password, db_user.password):
            raise AuthenticationError("Incorrect email or password")

        db_user.password = self.__hash_password(password_data.new_password)
        updated_user = await self.user_repository.update(db_user.id, db_user)
        return updated_user
