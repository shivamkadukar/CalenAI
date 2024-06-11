# code to operate on google calendar
import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

internal_email_domains = ['internal_email1.com', 'internal_email2.in']


def check_email_domain(email):
    domain = email.split('@')[-1]
    if domain not in internal_email_domains:
        return True
    return False


def is_ext_event(event):
    for attendee in event['attendees']:
        email = attendee['email']
        if check_email_domain(email):
            return True

    return False


def get_external_events(events):
    external_events = []
    for event in events:
        if 'attendees' in event.keys():
            if is_ext_event(event):
                external_events.append(event)
    return external_events


def main(year, month):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(r'token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        start_date = datetime.datetime(year, month, 1)
        end_date = start_date + datetime.timedelta(days=31)
        service = build('calendar', 'v3', credentials=creds)

        events_result = service.events().list(calendarId='my_email_id@gmail.com,
                                              timeMin=start_date.strftime(
                                                  '%Y-%m-%dT%H:%M:%S'+'Z'),
                                              timeMax=end_date.strftime('%Y-%m-%dT%H:%M:%S' + 'Z'), singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return
        else:
            ext_events = get_external_events(events)

            # Prints the start and name of the next 10 events
            print('\nClient Meetings:')
            for event in ext_events:
                start = event['start'].get(
                    'dateTime', event['start'].get('date'))
                print('    ', start, '    ', event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main(2023, 7)
