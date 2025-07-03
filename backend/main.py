import os
import smtplib
import pandas as pd
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def read_file(file_path: str):
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        return pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format")

@app.post("/send-bulk")
async def send_bulk_emails(
    file: UploadFile,
    email: str = Form(...),
    password: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...),
    smtp_server: Optional[str] = Form("smtp.gmail.com"),
    smtp_port: Optional[int] = Form(587),
):
    try:
        file_location = f"{UPLOAD_DIR}/{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        df = read_file(file_location)

        if 'Email' not in df.columns or 'name' not in df.columns:
            return {"error": "File must contain 'Email' and 'name' columns"}

        # Connect to SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)

        for _, row in df.iterrows():
            to_email = row['Email']
            name = row['name']
            personalized_body = body.replace('$name', name)

            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(personalized_body, 'plain'))

            server.send_message(msg)

        server.quit()
        return {"message": "Emails sent successfully!"}
    except Exception as e:
        return {"error": str(e)}
