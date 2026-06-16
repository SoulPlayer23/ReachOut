import base64
import os
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from config import settings
from models import OutreachLog, User
from routers.gmail import get_valid_credentials


def send_email(
    db: Session,
    user: User,
    to_email: str,
    subject: str,
    body: str,
    company: str,
    role: str,
    recruiter_name: str | None = None,
) -> dict:
    """
    Send a cold email via the user's Gmail account with resume attached.
    Writes an OutreachLog entry on success.
    Returns {"success": bool, "message_id": str | None}.
    """
    creds = get_valid_credentials(db, user)
    service = build("gmail", "v1", credentials=creds)

    message = _build_mime(
        sender=user.email,
        to=to_email,
        subject=subject,
        body=body,
    )

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    message_id = result.get("id")

    log = OutreachLog(
        user_id=user.id,
        company=company,
        role=role,
        recruiter_name=recruiter_name,
        recruiter_email=to_email,
        email_subject=subject,
        email_body=body,
        status="sent",
        sent_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()

    return {"success": True, "message_id": message_id}


def _build_mime(sender: str, to: str, subject: str, body: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if os.path.isfile(settings.resume_path):
        with open(settings.resume_path, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="pdf")
        filename = os.path.basename(settings.resume_path)
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attachment)

    return msg
