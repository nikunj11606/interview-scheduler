import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the names and ids of the first 10 calendars the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_client.json', SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API to verify access
        print('Connection successful!')
        print('Shared calendars found:')
        calendar_list = service.calendarList().list().execute()
        for calendar_list_entry in calendar_list.get('items', []):
            print(f"- {calendar_list_entry['summary']} ({calendar_list_entry['id']})")
        print("\nSUCCESS: 'token.json' has been created.")

    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    main()
