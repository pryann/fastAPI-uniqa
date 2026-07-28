from fastapi import FastAPI
from loguru import logger
from src.config import get_settings
from src.exceptions.exception_handlers import register_exception_handlers
from src.middlewares import register_middlewares
from src.modules.auth import router as auth_router
from src.modules.user import router as user_router
from src.modules.billing_address import router as billing_address_router
from src.utils.logger import setup_logging_and_sentry

settings = get_settings()
setup_logging_and_sentry(settings)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.include_router(user_router.router)
app.include_router(auth_router.router)
app.include_router(billing_address_router.router)

register_middlewares(app, logger, settings)
register_exception_handlers(app)
