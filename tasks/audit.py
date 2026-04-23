import os
import random
import string
import logging
import aiosmtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

# ================= EMAIL =================

def generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_verification_email(to_email: str, code: str):
    msg = MIMEText(
        f"Vaš kod za verifikaciju je: {code}\n\nKod važi 10 minuta.",
        "plain",
        "utf-8",
    )
    msg["Subject"] = "Verifikacija naloga"
    msg["From"] = os.getenv("MAIL_FROM")
    msg["To"] = to_email

    await aiosmtplib.send(
        msg,
        hostname=os.getenv("MAILTRAP_HOST"),
        port=int(os.getenv("MAILTRAP_PORT", "587")),
        username=os.getenv("MAILTRAP_USER"),
        password=os.getenv("MAILTRAP_PASS"),
        start_tls=True,
    )


# ================= LOGGING =================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("audit.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

audit_logger = logging.getLogger("audit")


def log_login(email: str, ip: str, success: bool):
    status = "USPJESAN" if success else "NEUSPJESAN"
    audit_logger.info(f"LOGIN {status} | korisnik={email} | ip={ip}")


def log_student_created(student_id: str, created_by: str):
    audit_logger.info(f"STUDENT_KREIRAN | id={student_id} | kreirao={created_by}")


def log_student_updated(student_id: str, updated_by: str, fields: list):
    audit_logger.info(
        f"STUDENT_IZMIJENJEN | id={student_id} | izmijenio={updated_by} | polja={fields}"
    )


def log_student_deleted(student_id: str, deleted_by: str):
    audit_logger.info(f"STUDENT_OBRISAN | id={student_id} | obrisao={deleted_by}")