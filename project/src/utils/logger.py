import logging
import sys

import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.loguru import LoggingLevels

from src.config import Settings


def init_sentry(settings):
    sentry_logging = LoggingIntegration(
        level=LoggingLevels[settings.SENTRY_LEVEL].value,
        event_level=LoggingLevels[settings.SENTRY_EVENT_LEVEL].value,
    )
    sentry_sdk.init(
        dsn=settings.SENTRY_DNS,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        integrations=[sentry_logging],
    )


class InterceptHandler(logging.Handler):
    def emit(self, record):
        loguru_logger = logger.opt(depth=6, exception=record.exc_info)
        loguru_logger.log(record.levelname, record.getMessage())


def setup_logging_and_sentry(settings: Settings) -> None:
    log_level = settings.LOGURU_LOG_LEVEL.upper()
    logger.remove()
    logger.add(sys.stdout, level=log_level)

    logging.basicConfig(handlers=[InterceptHandler()], level=log_level)

    if settings.APP_ENV == "prod":
        init_sentry(settings)
