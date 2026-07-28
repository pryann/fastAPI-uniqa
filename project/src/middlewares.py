import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from src.config import Settings


# class middlewares
def setup_cors_middleware(app: FastAPI, settings: Settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS_LIST,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_disable_cache_middleware(app: FastAPI):
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        response.headers.update(
            {"Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate", "Pragma": "no-cache"}
        )
        return response


# function middlewares
def setup_security_headers_middleware(app: FastAPI):
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)

        # Base security headers
        headers = {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "same-origin",
            "X-XSS-Protection": "1; mode=block",
        }

        # Adjust CSP for /docs path
        if request.url.path == "/docs":
            headers.update(
                {
                    "Content-Security-Policy": (
                        "default-src 'self'; "
                        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
                    ),
                }
            )
        else:
            headers.update(
                {
                    "Content-Security-Policy": "default-src 'self'",
                }
            )

        response.headers.update(headers)
        return response


# def setup_process_time_log_middleware(app: FastAPI, logger):
#     @app.middleware("http")
#     async def process_time_log_middleware(request: Request, call_next):
#         start_time = time.time()
#         response: Response = await call_next(request)
#         process_time = str(round(time.time() - start_time, 3))
#         response.headers["X-Process-Time"] = process_time
#         logger.info("ProcessTime=%s", process_time)
#         return response
#


def setup_global_rate_limit_middleware(app: FastAPI):
    app.state.limiter = Limiter(key_func=lambda request: request.client.host, default_limits=["100/minute"])
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)


def setup_request_log_middleware(app: FastAPI, logger):
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        request_info = f"{request.method} {request.url.path}"
        status_code = response.status_code
        client_host = request.client.host
        content_length = response.headers.get("content-length")

        logger.info(
            f"Request: {request_info} | "
            f"Status: {status_code} | "
            f"Duration: {duration:.2f}s | "
            f"Client: {client_host} | "
            f"Content-Length: {content_length}"
        )

        return response


def register_middlewares(app: FastAPI, logger, settings: Settings):
    # functions
    setup_cors_middleware(app, settings)
    setup_security_headers_middleware(app)
    setup_global_rate_limit_middleware(app)
    setup_disable_cache_middleware(app)
    setup_request_log_middleware(app, logger)

    # classes
    app.add_middleware(GZipMiddleware)
