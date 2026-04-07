import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_confirmation(
    candidate_name: str,
    candidate_email: str,
    interviewer_name: str,
    interviewer_email: str,
    interview_time: str,
    interview_date: str
) -> bool:
    try:
        EMAIL_USER = os.getenv("EMAIL_USER")
        EMAIL_PASS = os.getenv("EMAIL_PASS")

        # ── MOCK MODE: if no real credentials, just print and return True ──
        if not EMAIL_USER or not EMAIL_PASS:
            print("── MOCK EMAIL (no credentials found) ──")
            print(f"To Candidate  : {candidate_email}")
            print(f"To Interviewer: {interviewer_email}")
            print(f"Details       : {candidate_name} + {interviewer_name}")
            print(f"Time          : {interview_date} at {interview_time}")
            print("── Email would be sent here in production ──")
            return True

        # ── REAL MODE: runs when actual credentials exist ──
        def build_email(to_email, to_name):
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Interview Confirmation"
            msg["From"] = EMAIL_USER
            msg["To"] = to_email
            body = f"""
Hi {to_name},

Your interview has been confirmed.

Candidate   : {candidate_name}
Interviewer : {interviewer_name}
Date        : {interview_date}
Time        : {interview_time}

Regards,
ScheduleAI
            """
            msg.attach(MIMEText(body, "plain"))
            return msg

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, candidate_email,
                build_email(candidate_email, candidate_name).as_string())
            server.sendmail(EMAIL_USER, interviewer_email,
                build_email(interviewer_email, interviewer_name).as_string())
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False
    
