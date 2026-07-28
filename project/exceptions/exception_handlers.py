from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from src.exceptions.custom_exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
)


def generate_response(status_code: int, message: str):
    if status_code == 500:
        logger.error(f"The message {message} is {status_code}")
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"status_code": status_code, "detail": message}),
    )


def register_exception_handlers(app: FastAPI):
    exception_handlers = {
        NotFoundError: 404,
        AlreadyExistsError: 409,
        AuthenticationError: 401,
        AuthorizationError: 403,
    }

    for exc_class, status in exception_handlers.items():
        app.add_exception_handler(
            exc_class,
            lambda request, exc, status_code=status: generate_response(
                status_code, str(exc)
            ),
        )

    app.add_exception_handler(
        500, lambda request, exc: generate_response(500, "Internal server error")
    )
