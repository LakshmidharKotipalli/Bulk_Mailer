from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from string import Template
import pandas as pd
import smtplib
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/send-emails/")
async def send_emails(
    file: UploadFile = File(...),
    subject: str = Form(...),
    body_template: str = Form(...),
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    smtp_host: str = Form(default="smtp.gmail.com"),
    smtp_port: int = Form(default=465),
    use_tls: bool = Form(default=False)
):
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    ext = file.filename.split('.')[-1].lower()
    if ext == "csv":
        df = pd.read_csv(filepath)
    elif ext == "xlsx":
        df = pd.read_excel(filepath)
    elif ext == "json":
        with open(filepath, "r") as f:
            df = pd.DataFrame(json.load(f))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if 'name' not in df.columns or 'email' not in df.columns:
        raise HTTPException(status_code=400, detail="File must contain 'name' and 'email' columns")

    template = Template(body_template)
    sent, failed = 0, 0

    for _, row in df.iterrows():
        full_name = str(row.get("name", "")).strip()
        first_name = full_name.split()[0] if full_name else "there"
        recipient_email = str(row.get("email", "")).strip()

        try:
            personalized_body = template.safe_substitute(name=full_name, first_name=first_name)
            print(f"Sending to {recipient_email} with body:\n{personalized_body}\n")

            send_email(
                sender_email,
                sender_password,
                recipient_email,
                subject,
                personalized_body,
                smtp_host,
                smtp_port,
                use_tls
            )
            sent += 1
        except Exception as e:
            print(f"❌ Failed for {recipient_email}: {e}")
            failed += 1

    return {"sent": sent, "failed": failed, "total": len(df)}

def send_email(sender, password, recipient, subject, body, smtp_host, smtp_port, use_tls):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if use_tls:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
