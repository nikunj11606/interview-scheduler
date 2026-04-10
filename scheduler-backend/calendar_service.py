import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# ── Constants ──
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = Path(__file__).resolve().parent / "token.json"
CLIENT_SECRET_FILE = Path(__file__).resolve().parent / "oauth_client.json"
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
TIMEZONE = "Asia/Kolkata"
INTERVIEW_DURATION_HOURS = 1


# ── Function 1: Authenticate and return a Google Calendar service object ──
def get_calendar_service():
    """Uses token.json (OAuth2) and returns an authenticated Google Calendar API client."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, we failure here.
    # The user should run authenticate_calendar.py first.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_authorized_user_json())
            except Exception as e:
                print(f"[CalendarService] Token refresh error: {e}")
                return None
        else:
            print("[CalendarService] No valid token.json found. Please run 'python authenticate_calendar.py' once.")
            return None

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except Exception as e:
        print(f"[CalendarService] Auth error: {e}")
        return None


# ── Helper: Convert "April 10, 2026 at 3:00 PM" → datetime object ──
def _parse_datetime(datetime_str: str) -> datetime | None:
    formats = [
        "%B %d, %Y at %I:%M %p",
        "%B %d, %Y at %I %p",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(datetime_str.strip(), fmt)
        except ValueError:
            continue
    print(f"[CalendarService] Could not parse datetime: '{datetime_str}'")
    return None


# ── Helper: Convert datetime to ISO 8601 format for Google API ──
def _to_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


# ── Function 2: Check if interviewer has a conflict in OUR Master Calendar ──
def check_schedule_conflict(service, interviewer_name: str, datetime_str: str) -> bool:
    """
    Searches Master Calendar for existing events in the time window
    whose title contains the interviewer's name.
    """
    start_dt = _parse_datetime(datetime_str)
    if not start_dt:
        return False

    end_dt = start_dt + timedelta(hours=INTERVIEW_DURATION_HOURS)

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=_to_iso(start_dt) + "+05:30",
            timeMax=_to_iso(end_dt) + "+05:30",
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        for event in events:
            summary = event.get("summary", "")
            if interviewer_name.strip().lower() in summary.lower():
                print(f"[CalendarService] Conflict found for {interviewer_name}: '{summary}'")
                return True

        return False

    except Exception as e:
        print(f"[CalendarService] Conflict check error: {e}")
        return False


# ── Function 3: Check interviewer's personal calendar via Freebusy API ──
def check_personal_busy(service, interviewer_email: str, datetime_str: str) -> bool:
    """
    Uses Google's Freebusy API to check if the interviewer is busy.
    """
    start_dt = _parse_datetime(datetime_str)
    if not start_dt:
        return False

    end_dt = start_dt + timedelta(hours=INTERVIEW_DURATION_HOURS)

    try:
        body = {
            "timeMin": _to_iso(start_dt) + "+05:30",
            "timeMax": _to_iso(end_dt) + "+05:30",
            "timeZone": TIMEZONE,
            "items": [{"id": interviewer_email}],
        }

        result = service.freebusy().query(body=body).execute()
        busy_slots = result.get("calendars", {}).get(interviewer_email, {}).get("busy", [])

        if busy_slots:
            print(f"[CalendarService] {interviewer_email} is personally busy at {datetime_str}")
            return True

        return False

    except Exception as e:
        print(f"[CalendarService] Freebusy check error: {e}")
        return False


# ── Function 4: Create the interview event silently and get Meet link ──
def create_interview_event(
    service,
    candidate_name: str,
    candidate_email: str,
    interviewer_name: str,
    interviewer_email: str,
    datetime_str: str,
) -> str | None:
    """
    Creates a Google Calendar event.
    """
    start_dt = _parse_datetime(datetime_str)
    if not start_dt:
        return None

    end_dt = start_dt + timedelta(hours=INTERVIEW_DURATION_HOURS)

    event_body = {
        "summary": f"Interview: {candidate_name} & {interviewer_name}",
        "description": (
            f"Automated interview scheduled via SchedulerAI.\n\n"
            f"Candidate: {candidate_name} ({candidate_email})\n"
            f"Interviewer: {interviewer_name} ({interviewer_email})"
        ),
        "start": {
            "dateTime": _to_iso(start_dt),
            "timeZone": TIMEZONE,
        },
        "end": {
            "dateTime": _to_iso(end_dt),
            "timeZone": TIMEZONE,
        },
        "attendees": [
            {"email": candidate_email},
            {"email": interviewer_email},
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    try:
        created_event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates="none",
        ).execute()

        conference_data = created_event.get("conferenceData", {})
        entry_points = conference_data.get("entryPoints", [])
        meet_link = next(
            (ep.get("uri") for ep in entry_points if ep.get("entryPointType") == "video"),
            None,
        )

        print(f"[CalendarService] Event created. Meet link: {meet_link}")
        return meet_link

    except Exception as e:
        print(f"[CalendarService] Event creation error: {e}")
        return None


# ── Function 5: Delete an interview event ──
def delete_interview_event(service, candidate_name: str, interviewer_name: str) -> bool:
    search_title = f"Interview: {candidate_name} & {interviewer_name}".lower()

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            q=f"Interview: {candidate_name}",
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        for event in events:
            summary = event.get("summary", "").lower()
            if search_title in summary or (
                candidate_name.lower() in summary and interviewer_name.lower() in summary
            ):
                service.events().delete(
                    calendarId=CALENDAR_ID,
                    eventId=event["id"],
                    sendUpdates="none",
                ).execute()
                print(f"[CalendarService] Deleted event: '{event.get('summary')}'")
                return True
        return False

    except Exception as e:
        print(f"[CalendarService] Delete error: {e}")
        return False


# ── Function 6: Reschedule ──
def reschedule_interview_event(
    service,
    candidate_name: str,
    candidate_email: str,
    interviewer_name: str,
    interviewer_email: str,
    new_datetime_str: str,
) -> str | None:
    delete_interview_event(service, candidate_name, interviewer_name)
    return create_interview_event(
        service,
        candidate_name,
        candidate_email,
        interviewer_name,
        interviewer_email,
        new_datetime_str,
    )
