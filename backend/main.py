from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from string import Template
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-bulk-emails")
async def send_bulk_emails(
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    subject: str = Form(...),
    body_template: str = Form(...),
    file: UploadFile = Form(...)
):
    # Save uploaded file locally
    file_ext = os.path.splitext(file.filename)[1].lower()
    upload_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    # Read uploaded file
    if file_ext == ".csv":
        df = pd.read_csv(upload_path)
    elif file_ext in [".xls", ".xlsx"]:
        df = pd.read_excel(upload_path)
    elif file_ext == ".json":
        df = pd.read_json(upload_path)
    else:
        return {"status": "Unsupported file type"}

    # Ensure required columns exist
    if "Email" not in df.columns or "name" not in df.columns:
        return {"status": "Missing required columns: Email and name"}

    template = Template(body_template)
    sent = 0
    failed = 0

    for index, row in df.iterrows():
        to_email = row.get("Email")
        name = row.get("name", "").strip()

        try:
            # Fill name into template
            message_body = template.safe_substitute(name=name)

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message_body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, to_email, msg.as_string())

            sent += 1

        except Exception as e:
            print(f"Failed to send to {to_email}: {e}")
            failed += 1

    return {
        "status": "Completed",
        "sent": sent,
        "failed": failed
    }
