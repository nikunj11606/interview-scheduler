import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar.events', 'https://www.googleapis.com/auth/calendar.readonly']

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
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Google expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print("Failed to refresh token, prompting login:", e)
                creds = None
        
        if not creds:
            if not os.path.exists(client_secrets_path):
                print(f"Warning: OAuth Client secrets file not found at {client_secrets_path}")
                return None
            print("Starting OAuth flow. Check your browser to authenticate!")
            # This opens a browser automatically for the user to log in
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

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
