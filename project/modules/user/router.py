from fastapi import APIRouter, Depends, status

from src.modules.auth.dependencies import match_user_id_from_params_and_token
from src.modules.user.dependencies import get_existing_user_by_id, get_user_service
from src.modules.user.schemas import UserBaseSchema, UserReadSchema
from src.modules.user.service import UserService

router = APIRouter(prefix="/api/users", tags=["Users"])


# Get all users
# @router.get("/", response_model=List[UserReadSchema], dependencies=[Depends(require_role([UserRoleEnum.ADMIN]))])
@router.get("/", response_model=list[UserReadSchema])
async def list_users(user_service: UserService = Depends(get_user_service)):
    return await user_service.get_users()


# Find user by ID
@router.get(
    "/{user_id}",
    response_model=UserReadSchema,
    dependencies=[Depends(match_user_id_from_params_and_token)],
)
async def find_user(user: UserReadSchema = Depends(get_existing_user_by_id)):
    return user


# UPDATE user by ID
@router.put(
    "/{user_id}",
    response_model=UserReadSchema,
    dependencies=[Depends(match_user_id_from_params_and_token)],
)
async def update_user(
    user_id: int,
    user: UserBaseSchema,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(user_id, user)


# DELETE user by ID
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(user_id)
