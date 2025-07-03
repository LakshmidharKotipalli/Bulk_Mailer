from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import pandas as pd
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/send-emails/")
async def send_bulk_emails(
    file: UploadFile = File(...),
    subject: str = Form(...),
    body_template: str = Form(...),  # contains {{name}}
    sender_email: str = Form(...),
    sender_password: str = Form(...)
):
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Read file into DataFrame
    if ext == "xlsx":
        df = pd.read_excel(filepath)
    elif ext == "csv":
        df = pd.read_csv(filepath)
    elif ext == "json":
        with open(filepath, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    if 'name' not in df.columns or 'email' not in df.columns:
        raise HTTPException(status_code=400, detail="File must have 'name' and 'email' columns")

    # Email sending loop
    for _, row in df.iterrows():
        name = row["name"]
        recipient_email = row["email"]
        personalized_body = body_template.replace("{{name}}", name)

        try:
            send_email(
                sender_email,
                sender_password,
                recipient_email,
                subject,
                personalized_body
            )
        except Exception as e:
            print(f"Failed to send to {recipient_email}: {e}")

    return {"message": f"Emails sent to {len(df)} recipients."}

def send_email(sender_email, password, recipient, subject, body):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient, message.as_string())
