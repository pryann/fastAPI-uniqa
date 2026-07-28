from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import get_settings
from src.modules.auth.dependencies import (
    get_auth_service,
    match_user_id_from_params_and_token,
)
from src.modules.auth.schemas import (
    EmailSchema,
    LoginSchema,
    OTPVerificationSchema,
    ResetPasswordSchema,
    UserCreatedSchema,
    UserCreateSchema,
    UserUpdatePasswordSchema,
)
from src.modules.auth.service import AuthService
from src.modules.user.schemas import UserReadSchema
from src.utils.send_mail import send_email

settings = get_settings()

router = APIRouter(prefix="/api/auth", tags=["Auth"])

auth_limiter = Limiter(
    key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_HARD_LIMIT]
)


# Get the current user
@router.get(
    "/me",
    response_model=UserReadSchema,
    dependencies=[Depends(match_user_id_from_params_and_token)],
)
async def me(auth_service: AuthService = Depends(get_auth_service)):
    user_form_token = await auth_service.get_current_user_from_access_token()
    return user_form_token.id


@router.post(
    "/register", response_model=UserCreatedSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreateSchema,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service),
):
    new_user = await auth_service.create_user(user)
    otp_code = auth_service.generate_otp_code(user.otp_secret)
    background_tasks.add_task(
        send_email,
        to=user.email,
        subject="Registration",
        template_name="registration_email_template.html",
        fullname=user.fullname,
        otp_code=otp_code,
    )
    return new_user


@router.post("/login", status_code=status.HTTP_204_NO_CONTENT)
async def login(
    request: Request,
    response: Response,
    user: LoginSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.login(user)
    response.set_cookie(
        key="access_token", value=tokens["access_token"], httponly=True, secure=True
    )
    response.set_cookie(
        key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=True
    )


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")


@router.get("/refresh-tokens", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_tokens(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    tokens = await auth_service.regenerate_auth_tokens(refresh_token)
    response.set_cookie(
        key="access_token", value=tokens["access_token"], httponly=True, secure=True
    )
    response.set_cookie(
        key="refresh_token", value=tokens["refresh_token"], httponly=True, secure=True
    )
    return {}


@router.post("/password/change", status_code=status.HTTP_204_NO_CONTENT)
async def password_change(
    request: Request,
    password_data: UserUpdatePasswordSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token = request.cookies.get("access_token")
    await auth_service.change_password(access_token, password_data)
    return {}
