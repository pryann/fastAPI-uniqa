from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.pg_database import get_session
from src.modules.billing_address.repository import BillingAddressRepository
from src.modules.billing_address.service import BillingAddressService


def get_billing_address_service(session: AsyncSession = Depends(get_session)) -> BillingAddressService:
    billing_address_repository = BillingAddressRepository(session)
    return BillingAddressService(billing_address_repository)
