from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.database.pg_database import get_session
from src.exceptions.custom_exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)
from src.modules.auth.schemas import TokenPayloadSchema
from src.modules.auth.service import AuthService
from src.modules.user.constants import UserRoleEnum
from src.modules.user.repository import BillingAddressRepository
from src.utils.token_handler import TokenHandler


def get_auth_service(
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthService:
    user_repository = BillingAddressRepository(session)
    token_service = TokenHandler(settings)
    return AuthService(
        user_repository=user_repository, token_handler=token_service, settings=settings
    )


async def require_auth(
    request: Request, auth_service: AuthService = Depends(get_auth_service)
) -> TokenPayloadSchema:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise AuthenticationError("You need to login in to the system")
    user = await auth_service.get_current_user_from_access_token(access_token)
    if not user:
        raise NotFoundError("User Not fround from token email")
    return user


def require_role(accepted_roles: list[UserRoleEnum]) -> callable:
    async def role_checker(
        request: Request, auth_service: AuthService = Depends(get_auth_service)
    ) -> TokenPayloadSchema:
        user = await require_auth(request, auth_service)
        if user.role not in accepted_roles:
            raise AuthorizationError("User does not have the required role")
        return user

    return role_checker


async def match_user_id_from_params_and_token(
    request: Request, auth_service: AuthService = Depends(get_auth_service)
) -> None:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise AuthenticationError("You need to login in to the system")

    user_from_token = await auth_service.get_current_user_from_access_token(
        access_token
    )

    if user_from_token.id != int(request.path_params.get("user_id")):
        raise AuthorizationError("User ID does not match with the authenticated user")
