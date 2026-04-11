import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Use Indian Standard Time since the app time is India
TIMEZONE = "Asia/Kolkata"

def get_calendar_service():
    """Authenticate and return the Google Calendar service using OAuth flow."""
    creds = None
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    client_secrets_path = os.path.join(os.path.dirname(__file__), 'oauth_client.json')

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, handle refresh or fail.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Google expired token...")
            try:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
            except Exception as e:
                print("Failed to refresh token:", e)
                creds = None
        
        if not creds:
            print("[CALENDAR ERROR] No valid token.json found. Please run 'python authenticate_calendar.py' once manually.")
            return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to build calendar service: {e}")
        return None

def check_availability(service, interviewer_email, dt_str, duration_minutes=60):
    """
    Check if the interviewer has any conflicting events.
    """
    if not service:
        # If no service, assume available
        return True
        
    try:
        start_dt = datetime.strptime(dt_str, "%B %d, %Y at %I:%M %p")
        local_tz = pytz.timezone(TIMEZONE)
        start_dt = local_tz.localize(start_dt)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        events_result = service.events().list(
            calendarId='primary',  # Checking the user's own calendar for conflicts
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        return len(events) == 0
    except Exception as e:
        print(f"Calendar auth/read check failed: {e}. Assuming available.")
        return True

def create_interview_event(service, candidate_name, candidate_email, interviewer_name, interviewer_email, dt_str):
    if not service:
        return None
        
    try:
        start_dt = datetime.strptime(dt_str, "%B %d, %Y at %I:%M %p")
        local_tz = pytz.timezone(TIMEZONE)
        start_dt = local_tz.localize(start_dt)
        end_dt = start_dt + timedelta(hours=1)
        
        event = {
            'summary': f'Interview: {candidate_name} & {interviewer_name}',
            'description': f'Interview scheduled via Interview Scheduler.\\nCandidate: {candidate_name}\\nInterviewer: {interviewer_name}',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': TIMEZONE,
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"{candidate_name.replace(' ', '')}-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        # We insert into the authenticated user's primary calendar
        created_event = service.events().insert(
            calendarId='primary', 
            body=event, 
            conferenceDataVersion=1,
            sendUpdates='none'
        ).execute()
        
        hangout_link = created_event.get('hangoutLink', '')
        print(f"Event created. Meet Link: {hangout_link}")
        return created_event.get('id'), hangout_link
    except Exception as e:
        print(f"Failed to create event: {e}")
        return None, ""

def delete_event(service, event_id):
    if not service or not event_id:
        return
    try:
        service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates='all'
        ).execute()
        print(f"Event {event_id} deleted.")
    except Exception as e:
        print(f"Failed to delete event: {e}")


# ── Extra functions used by main.py's intent routing ──

def check_schedule_conflict(service, interviewer_name: str, dt_str: str) -> bool:
    """
    Returns True if a calendar event at dt_str exists whose title contains
    the interviewer's name (meaning they already have an interview then).
    Returns False if no conflict found (they are free).
    """
    if not service:
        return False
    try:
        start_dt = datetime.strptime(dt_str.strip(), "%B %d, %Y at %I:%M %p")
        local_tz = pytz.timezone(TIMEZONE)
        start_dt = local_tz.localize(start_dt)
        end_dt = start_dt + timedelta(hours=1)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        for event in events_result.get('items', []):
            summary = event.get('summary', '')
            if interviewer_name.strip().lower() in summary.lower():
                print(f"[Calendar] Conflict found for {interviewer_name}: '{summary}'")
                return True
        return False
    except Exception as e:
        print(f"[Calendar] check_schedule_conflict error: {e}")
        return False  # Fail open — don't block if calendar is unreachable


def check_personal_busy(service, interviewer_email: str, dt_str: str) -> bool:
    """
    Uses Freebusy API to check if the interviewer's personal calendar is busy.
    Returns True if busy, False if free or on error.
    """
    if not service:
        return False
    try:
        start_dt = datetime.strptime(dt_str.strip(), "%B %d, %Y at %I:%M %p")
        local_tz = pytz.timezone(TIMEZONE)
        start_dt = local_tz.localize(start_dt)
        end_dt = start_dt + timedelta(hours=1)

        body = {
            "timeMin": start_dt.isoformat(),
            "timeMax": end_dt.isoformat(),
            "timeZone": TIMEZONE,
            "items": [{"id": interviewer_email}],
        }
        result = service.freebusy().query(body=body).execute()
        busy_slots = result.get("calendars", {}).get(interviewer_email, {}).get("busy", [])
        return len(busy_slots) > 0
    except Exception as e:
        print(f"[Calendar] check_personal_busy error: {e}")
        return False  # Fail open


def delete_interview_event(service, candidate_name: str, interviewer_name: str) -> bool:
    """
    Searches for an event titled 'Interview: candidate & interviewer' and deletes it.
    """
    if not service:
        return False
    try:
        events_result = service.events().list(
            calendarId='primary',
            q=f"Interview: {candidate_name}",
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        for event in events_result.get('items', []):
            summary = event.get('summary', '').lower()
            if candidate_name.lower() in summary and interviewer_name.lower() in summary:
                service.events().delete(
                    calendarId='primary',
                    eventId=event['id'],
                    sendUpdates='none'
                ).execute()
                print(f"[Calendar] Deleted event: '{event.get('summary')}'")
                return True
        return False
    except Exception as e:
        print(f"[Calendar] delete_interview_event error: {e}")
        return False


def reschedule_interview_event(service, candidate_name, candidate_email,
                                interviewer_name, interviewer_email, new_dt_str):
    """Delete old event and create a new one at the new time."""
    delete_interview_event(service, candidate_name, interviewer_name)
    return create_interview_event(service, candidate_name, candidate_email,
                                   interviewer_name, interviewer_email, new_dt_str)

