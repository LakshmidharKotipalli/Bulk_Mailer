import pandas as pd
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-emails/")
async def send_bulk_emails(
    file: UploadFile,
    smtp_server: str = Form(...),
    smtp_port: int = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    subject: str = Form(...),
    body: str = Form(...)
):
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Read Excel or CSV
    if file.filename.endswith(".csv"):
        df = pd.read_csv(temp_path)
    elif file.filename.endswith(".json"):
        df = pd.read_json(temp_path)
    else:
        df = pd.read_excel(temp_path)

    # Open connection
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email, password)
    except Exception as e:
        return {"error": f"SMTP login failed: {e}"}

    # Send mails with custom names
    for _, row in df.iterrows():
        recipient = row['Email']
        name = row['name'] if 'name' in row and pd.notnull(row['name']) else ""
        customized_body = body.replace("$name", name)

        message = MIMEText(customized_body, "plain")
        message["From"] = email
        message["To"] = recipient
        message["Subject"] = subject

        try:
            server.sendmail(email, recipient, message.as_string())
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")

    server.quit()
    os.remove(temp_path)

    return {"message": "Emails sent successfully"}
