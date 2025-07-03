from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "Bulk Mail Backend is live 🚀"}

@app.post("/send-emails/")
async def send_bulk_emails(
    file: UploadFile = File(...),
    subject: str = Form(...),
    body_template: str = Form(...),
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    smtp_host: str = Form(default="smtp.gmail.com"),
    smtp_port: int = Form(default=465),
    use_tls: bool = Form(default=False)
):
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save uploaded file
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # Load into DataFrame
    try:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File read error: {str(e)}")

    if 'name' not in df.columns or 'email' not in df.columns:
        raise HTTPException(status_code=400, detail="File must have 'name' and 'email' columns")

    sent = 0
    failed = 0

    for _, row in df.iterrows():
        full_name = str(row["name"]).strip()
        first_name = full_name.split()[0]
        recipient_email = row["email"]

        personalized_body = (
            body_template
            .replace("{{name}}", full_name)
            .replace("{{first_name}}", first_name)
        )

        try:
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
            print(f"✅ Sent to {recipient_email} as {first_name}")
            sent += 1
        except Exception as e:
            print(f"❌ Failed to send to {recipient_email}: {e}")
            failed += 1

    return {
        "message": f"✅ Sent: {sent} | ❌ Failed: {failed}",
        "total": len(df)
    }

def send_email(sender_email, password, recipient, subject, body, smtp_host, smtp_port, use_tls):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    if use_tls:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient, message.as_string())
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient, message.as_string())
