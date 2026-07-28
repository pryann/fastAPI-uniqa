import subprocess  # nosec
import sys

import uvicorn

# import psutil
from src.config import get_settings

settings = get_settings()

base_server_settings = {
    "host": settings.SERVER_HOST,
    "port": settings.SERVER_PORT,
    "log_level": settings.SERVER_LOG_LEVEL,
    "timeout_keep_alive": settings.SERVER_TTL,
}


def safe_run(command):
    if isinstance(command, list) and all(isinstance(arg, str) for arg in command):
        subprocess.run(command, check=True)  # nosec
    else:
        raise ValueError("Invalid command format")


# def kill_process_on_port(port):
#     for proc in psutil.process_iter():
#         for conns in proc.connections(kind="inet"):
#             if conns.laddr.port == port:
#                 proc.send_signal(signal.SIGTERM)


def dev():
    # kill_process_on_port(8000)
    # command = ["hypercorn", "src.main:app", "--reload"]
    command = ["fastapi", "dev", "src/main.py"]
    # command = ["hypercorn", "src.main:app", "--worker-class", "trio"]
    safe_run(command)


def prod():
    # kill_process_on_port(settings.SERVER_PORT)
    prod_settings = {
        "ssl_keyfile": settings.SSL_KEYFILE,
        "ssl_certfile": settings.SSL_CERTFILE,
        "reload": False,
    }
    combined_settings = {**base_server_settings, **prod_settings}
    uvicorn.run("src.main:app", **combined_settings)


def alembic_init():
    command = ["alembic", "init", "alembic"]
    safe_run(command)


def alembic_revision():
    message = sys.argv[1]
    command = ["alembic", "revision", "--autogenerate", "-m", message]
    safe_run(command)


def alembic_upgrade():
    command = ["alembic", "upgrade", "head"]
    safe_run(command)


def alembic_downgrade():
    command = ["alembic", "downgrade", "base"]
    safe_run(command)


def pre_commit_all():
    command = ["pre-commit", "run", "--all-files"]
    safe_run(command)
