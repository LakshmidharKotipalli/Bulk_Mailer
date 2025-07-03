from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from pydantic import BaseModel
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_smtp_settings(email: str):
    domain = email.split("@")[-1].lower()

    if domain == "gmail.com":
        return "smtp.gmail.com", 587, False
    elif domain == "ganait.com":
        return "mail.gandi.net", 465, True
    else:
        raise ValueError("Unsupported email domain.")

def send_email(sender, password, recipient, subject, body):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    smtp_server, port, use_ssl = get_smtp_settings(sender)

    if use_ssl:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
    else:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())

@app.post("/send")
async def send_bulk_emails(
    file: UploadFile = File(...),
    subject: str = Form(...),
    body: str = Form(...),
    sender: str = Form(...),
    password: str = Form(...)
):
    contents = await file.read()
    filename = file.filename.lower()

    # Parse file
    if filename.endswith(".csv"):
        df = pd.read_csv(pd.io.common.BytesIO(contents))
    elif filename.endswith(".json"):
        df = pd.read_json(pd.io.common.BytesIO(contents))
    elif filename.endswith((".xls", ".xlsx")):
        df = pd.read_excel(pd.io.common.BytesIO(contents))
    else:
        return {"error": "Unsupported file type. Use .csv, .json, or .xlsx"}

    if "Email" not in df.columns or "name" not in df.columns:
        return {"error": "File must contain 'Email' and 'name' columns."}

    for _, row in df.iterrows():
        recipient = row["Email"]
        name = row["name"]
        personalized_body = body.replace("$name", name)
        personalized_subject = subject.replace("$name", name)

        try:
            send_email(sender, password, recipient, personalized_subject, personalized_body)
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")

    return {"status": "Emails processed."}
