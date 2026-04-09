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
    interview_datetime: str,
    action: str = "SCHEDULED"  # 'SCHEDULED' or 'CANCELED'
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
            print(f"Time          : {interview_datetime}")
            print(f"Action        : {action}")
            print("── Email would be sent here in production ──")
            return True

        # ── REAL MODE: runs when actual credentials exist ──
        def build_email(to_email, to_name, role_title):
            msg = MIMEMultipart("alternative")
            
            if action == "CANCELED":
                subject = f"Interview Canceled: {candidate_name}"
                header_text = "Interview Canceled"
                header_color = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
                p_text = "An interview has been canceled. Please see the details below."
            elif action == "RESCHEDULED":
                subject = f"Interview Rescheduled: {candidate_name}"
                header_text = "Interview Rescheduled"
                header_color = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
                p_text = "The time for this interview has been updated. Please review the new details below."
            else:
                subject = f"Interview Scheduled: {candidate_name}"
                header_text = "Interview Scheduled"
                header_color = "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)"
                p_text = "An interview has been successfully scheduled. Please review the details below to ensure you are prepared."

            msg["Subject"] = subject
            msg["From"] = f"ScheduleAI <{EMAIL_USER}>"
            msg["To"] = to_email

            # 1. Plain text fallback
            text_body = f"""Hi {to_name},

{p_text}

Details:
- Candidate: {candidate_name}
- Interviewer: {interviewer_name}
- Date & Time: {interview_datetime}

Regards,
ScheduleAI System
"""

            # 2. Premium HTML Template
            html_body = f"""
            <html>
              <head>
                <style>
                  body {{ font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; margin: 0; padding: 0; }}
                  .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
                  .header {{ background: {header_color}; padding: 30px 40px; color: white; text-align: center; }}
                  .header h2 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 0.5px; }}
                  .content {{ padding: 40px; color: #334155; }}
                  .content p {{ font-size: 16px; line-height: 1.6; margin-top: 0; }}
                  .card {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 25px; margin: 30px 0; }}
                  .row {{ display: flex; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 15px; }}
                  .row:last-child {{ margin-bottom: 0; border-bottom: none; padding-bottom: 0; }}
                  .label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; font-weight: 600; width: 120px; }}
                  .value {{ font-size: 16px; color: #0f172a; font-weight: 500; }}
                  .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; font-size: 13px; color: #64748b; border-top: 1px solid #e2e8f0; }}
                </style>
              </head>
              <body>
                <div class="container">
                  <div class="header">
                    <h2>{header_text}</h2>
                  </div>
                  <div class="content">
                    <p>Hi <strong>{to_name}</strong>,</p>
                    <p>{p_text}</p>
                    
                    <div class="card">
                      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 15px;">
                        <tr>
                            <td class="label">Date & Time</td>
                            <td class="value" style="color: #4f46e5;">{interview_datetime}</td>
                        </tr>
                      </table>
                      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 15px;">
                        <tr>
                            <td class="label">Candidate</td>
                            <td class="value">{candidate_name}</td>
                        </tr>
                      </table>
                      <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td class="label">Interviewer</td>
                            <td class="value">{interviewer_name}</td>
                        </tr>
                      </table>
                    </div>
                    
                    <p>You are receiving this email as the <strong>{role_title}</strong> for this session.</p>
                  </div>
                  <div class="footer">
                    &copy; 2026 ScheduleAI. Automated Interview System.
                  </div>
                </div>
              </body>
            </html>
            """
            
            # Attach both versions (email clients will prefer the HTML one if supported)
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            return msg

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            
            # Send to candidate
            server.sendmail(EMAIL_USER, candidate_email,
                build_email(candidate_email, candidate_name, "Candidate").as_string())
            
            # Send to interviewer
            server.sendmail(EMAIL_USER, interviewer_email,
                build_email(interviewer_email, interviewer_name, "Interviewer").as_string())
            
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False
    
