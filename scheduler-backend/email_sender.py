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
    action: str = "SCHEDULED",  # 'SCHEDULED' or 'CANCELED'
    meet_link: str = ""
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

            meet_text = f"- Google Meet: {meet_link}\n" if meet_link and action != "CANCELED" else ""
            
            # 1. Plain text fallback
            text_body = f"""Hi {to_name},

{p_text}

Details:
- Candidate: {candidate_name}
- Interviewer: {interviewer_name}
- Date & Time: {interview_datetime}
{meet_text}
Regards,
ScheduleAI System
"""

            meet_html = ""
            meet_button_html = ""
            if meet_link and action != "CANCELED":
                meet_button_html = f"""
                <table width="100%" cellpadding="0" cellspacing="0" style="margin-top: 24px;">
                  <tr>
                    <td align="center">
                      <a href="{meet_link}"
                         style="display: inline-block; background: linear-gradient(135deg, #6366f1, #4f46e5);
                                color: #ffffff; padding: 14px 36px; border-radius: 8px;
                                text-decoration: none; font-size: 15px; font-weight: 600;
                                letter-spacing: 0.5px; font-family: 'Segoe UI', Arial, sans-serif;
                                mso-padding-alt: 0; width: 100%; box-sizing: border-box; text-align: center;">
                        Join Google Meet
                      </a>
                    </td>
                  </tr>
                </table>"""

            html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>{subject}</title>
  <style>
    /* Reset */
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
    img {{ border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
    body {{ margin: 0 !important; padding: 0 !important; background-color: #f1f5f9; }}

    /* Mobile Responsive */
    @media only screen and (max-width: 600px) {{
      .email-container {{ width: 100% !important; margin: 0 !important; border-radius: 0 !important; }}
      .header-cell {{ padding: 24px 20px !important; }}
      .header-cell h1 {{ font-size: 20px !important; }}
      .content-cell {{ padding: 24px 20px !important; }}
      .detail-label {{ font-size: 11px !important; padding-bottom: 2px !important; display: block; }}
      .detail-value {{ font-size: 15px !important; }}
      .footer-cell {{ padding: 16px 20px !important; font-size: 12px !important; }}
      .meet-btn {{ width: 100% !important; padding: 14px 20px !important; font-size: 15px !important; }}
    }}
  </style>
</head>
<body>
  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:#f1f5f9; padding: 24px 0;">
    <tr>
      <td align="center" valign="top">

        <!-- Email Card -->
        <table class="email-container" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px; width:100%; background:#ffffff;
                      border-radius:12px; overflow:hidden;
                      box-shadow:0 4px 20px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td class="header-cell" align="center"
                style="background:{header_color}; padding:32px 40px;">
              <h1 style="margin:0; color:#ffffff; font-size:22px; font-weight:700;
                          font-family:'Segoe UI',Arial,sans-serif; letter-spacing:0.3px;">
                {header_text}
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td class="content-cell" style="padding:32px 40px; color:#334155;
                        font-family:'Segoe UI',Arial,sans-serif;">

              <p style="margin:0 0 8px 0; font-size:16px; line-height:1.5;">
                Hi <strong>{to_name}</strong>,
              </p>
              <p style="margin:0 0 24px 0; font-size:15px; line-height:1.6; color:#475569;">
                {p_text}
              </p>

              <!-- Details Card -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="background:#f8fafc; border:1px solid #e2e8f0;
                            border-radius:8px; padding:0; margin-bottom:24px;">

                <!-- Date & Time -->
                <tr>
                  <td style="padding:18px 20px; border-bottom:1px solid #e2e8f0;">
                    <span class="detail-label"
                          style="display:block; font-size:11px; font-weight:700;
                                 text-transform:uppercase; letter-spacing:1px;
                                 color:#64748b; margin-bottom:4px;">
                      Date &amp; Time
                    </span>
                    <span class="detail-value"
                          style="font-size:16px; font-weight:600; color:#4f46e5;">
                      {interview_datetime}
                    </span>
                  </td>
                </tr>

                <!-- Candidate -->
                <tr>
                  <td style="padding:18px 20px; border-bottom:1px solid #e2e8f0;">
                    <span class="detail-label"
                          style="display:block; font-size:11px; font-weight:700;
                                 text-transform:uppercase; letter-spacing:1px;
                                 color:#64748b; margin-bottom:4px;">
                      Candidate
                    </span>
                    <span class="detail-value"
                          style="font-size:16px; font-weight:500; color:#0f172a;">
                      {candidate_name}
                    </span>
                  </td>
                </tr>

                <!-- Interviewer -->
                <tr>
                  <td style="padding:18px 20px;">
                    <span class="detail-label"
                          style="display:block; font-size:11px; font-weight:700;
                                 text-transform:uppercase; letter-spacing:1px;
                                 color:#64748b; margin-bottom:4px;">
                      Interviewer
                    </span>
                    <span class="detail-value"
                          style="font-size:16px; font-weight:500; color:#0f172a;">
                      {interviewer_name}
                    </span>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 0 0; font-size:14px; color:#64748b; line-height:1.5;">
                You are receiving this email as the <strong style="color:#334155;">{role_title}</strong>
                for this interview session.
              </p>

              {meet_button_html}

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td class="footer-cell"
                style="background:#f8fafc; padding:20px 40px; text-align:center;
                        font-size:13px; color:#94a3b8;
                        border-top:1px solid #e2e8f0;
                        font-family:'Segoe UI',Arial,sans-serif;">
              &copy; 2026 ScheduleAI &mdash; Automated Interview System
            </td>
          </tr>

        </table>
        <!-- / Email Card -->

      </td>
    </tr>
  </table>
</body>
</html>"""
            
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
    
