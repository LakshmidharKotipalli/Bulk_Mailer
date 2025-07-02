from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from email_utils import send_email  # your SMTP handler
from typing import List

app = FastAPI()

# Enable CORS so your frontend can access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/send-emails/")
def send_emails(
    subject: str = Form(...),
    body: str = Form(...),
    emails: List[str] = Form(...)
):
    results = []
    for email in emails:
        try:
            send_email(email, subject, body)
            results.append({"email": email, "status": "Sent"})
        except Exception as e:
            results.append({"email": email, "status": f"Failed: {str(e)}"})
    return { "results": results }
