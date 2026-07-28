from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import getcwd, path

from aiosmtplib import send
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config import get_settings


async def send_email(
    to: str,
    subject: str,
    template_name: str,
    cc: str | list[str] = None,
    bcc: str | list[str] = None,
    attachments: list[str] = None,
    **kwargs,
):
    env = Environment(
        loader=FileSystemLoader(path.join(getcwd(), "src", "templates")),
        autoescape=select_autoescape(["html", "xml"]),
    )
    settings = get_settings()

    template = env.get_template(template_name)
    html_content = template.render(**kwargs)
    part = MIMEText(html_content, "html")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_USERNAME
    msg["To"] = to
    msg.attach(part)

    if cc:
        msg["Cc"] = ", ".join(cc) if isinstance(cc, list) else cc
    if bcc:
        msg["Bcc"] = ", ".join(bcc) if isinstance(bcc, list) else bcc

    if attachments:
        for file_path in attachments:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(open(file_path, "rb").read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={path.basename(file_path)}",
            )
            msg.attach(part)

    await send(
        msg,
        hostname=settings.EMAIL_HOST,
        start_tls=True,
        username=settings.EMAIL_USERNAME,
        password=settings.EMAIL_PASSWORD,
    )
