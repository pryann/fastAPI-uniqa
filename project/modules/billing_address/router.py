from fastapi import APIRouter, Depends, status

from src.modules.auth.dependencies import match_user_id_from_params_and_token
from src.modules.billing_address.dependencies import get_billing_address_service
from src.modules.billing_address.schemas import BillingAddressBaseSchema
from src.modules.billing_address.service import BillingAddressService

router = APIRouter(
    prefix="/api/users", tags=["BillingAddress"], dependencies=[Depends(match_user_id_from_params_and_token)]
)


@router.get(
    "/{user_id}/billing-addresses",
    response_model=list[BillingAddressBaseSchema],
)
async def get_all_user_billing_address(
    user_id: int,
    billing_address_service: BillingAddressService = Depends(get_billing_address_service),
):
    billing_address = await billing_address_service.get_all_user_billing_address(user_id)
    return billing_address


# READ ALL billing address from a user
@router.get(
    "/{user_id}/billing-addresses/{billing_address_id}",
    response_model=BillingAddressBaseSchema,
)
async def find_billing_address(
    billing_address_id: int,
    billing_address_service: BillingAddressService = Depends(get_billing_address_service),
):
    billing_address = await billing_address_service.get_billing_address_by_id(billing_address_id)
    return billing_address


# Get a user billing addresses
@router.post("/{user_id}/billing-addresses", response_model=BillingAddressBaseSchema)
async def add_billing_address(
    user_id: int,
    billing_address: BillingAddressBaseSchema,
    billing_address_service: BillingAddressService = Depends(get_billing_address_service),
):
    return await billing_address_service.add_billing_address(billing_address, user_id)


# CREATE billing addresses
@router.put("/{user_id}/billing-addresses/{billing_address_id}", response_model=BillingAddressBaseSchema)
async def update_billing_address(
    billing_address_id: int,
    billing_address_data: BillingAddressBaseSchema,
    billing_address_service: BillingAddressService = Depends(get_billing_address_service),
):
    return await billing_address_service.update_billing_address(billing_address_id, billing_address_data)


@router.delete("/{user_id}/billing-addresses/{billing_address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_billing_address(
    billing_address_id: int,
    billing_address_service: BillingAddressService = Depends(get_billing_address_service),
):
    await billing_address_service.delete_billing_address(billing_address_id)
