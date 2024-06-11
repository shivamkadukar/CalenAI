import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import openai
import json

load_dotenv()

with open('gpt_prompts/classify_meetings_prompt.json', 'r') as file:
    config = json.load(file)

openai.api_key = os.getenv("OPENAI_KEY")
openai_model = config['openai_model']

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE_PATH = 'auth/token.json'
CREDENTIALS_FILE_PATH = 'auth/oauth_credentials.json'

internal_email_domains = tuple(config['internal_email_domains'])
calendar_ids = []


def get_external_attendees(year, month, calendar_ids):
    '''returns list of external attendees in all events'''
    external_emails = []
    calendar_events = get_events(year, month, calendar_ids)
    for events in calendar_events.values():
        for event in events:
            if 'attendees' in event.keys():
                for attendee in event['attendees']:
                    email = attendee['email']
                    if (
                        not email.endswith(internal_email_domains) and
                        email not in external_emails
                    ):
                        external_emails.append(email)

    return {'external_emails': external_emails}


def get_events(year, month, calendar_ids):
    events = {}
    creds = None
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE_PATH, 'w') as token:
            token.write(creds.to_json())

    try:
        start_date = datetime.datetime(int(year), int(month), 1)
        end_date = start_date + datetime.timedelta(days=31)
        service = build('calendar', 'v3', credentials=creds)

        for calendar_id in calendar_ids:
            events_result = service.events().list(calendarId=calendar_id,
                                                  timeMin=start_date.strftime(
                                                      '%Y-%m-%dT%H:%M:%S' + 'Z'),
                                                  timeMax=end_date.strftime('%Y-%m-%dT%H:%M:%S' + 'Z'), singleEvents=True,
                                                  orderBy='startTime').execute()
            events[calendar_id] = events_result.get('items', [])

        return events

    except Exception as error:
        print('An error occurred: %s' % error)


def get_filtering_response_from_gpt(events):
    query_data = json.dumps(
        [{'meeting_summary': x['meeting_summary'], 'attendees': x['attendees']} for x in events])
    chat = [
        {"role": "system", "content": config['prompts']['event_filter']},
        {"role": "user", "content": query_data}
    ]
    function = [
        {
            "name": "accept_client_meetings_on_calendar",
            "description": "accepts meeting on calendar which are identified as client meetings",
            "parameters": {
                "type": "object",
                "properties": {
                    "meeting_summary_list": {
                        "type": "object",
                        "description": "list of meeting summaries"
                    }
                },
                "required": ["meeting_summary_list"]
            }}
    ]
    response = openai.ChatCompletion.create(
        request_timeout=180,
        response_format={"type": "json_object"},
        model=openai_model,
        messages=chat,
        # functions=function
    )
    return response


def get_events_with_external_attendees(year, month, calendar_ids):
    '''returns events with external attendees and list of internal emails'''
    internal_emails = []
    external_calendar_events = dict()
    calendar_events = get_events(year, month, calendar_ids)
    for calendar_id, events in calendar_events.items():
        external_events = []
        for event in events:
            if 'attendees' in event.keys():
                internal_emails.extend([attendee['email'] for attendee in event['attendees']
                                       if attendee['email'].endswith(internal_email_domains)])

                if not all(attendee['email'].endswith(internal_email_domains) for attendee in event['attendees']):
                    external_events.append({
                        'meeting_summary': event['summary'],
                        'attendees': [attendee['email'] for attendee in event['attendees']],
                        'organizer': event['organizer']['email'],
                        'datetime': f***REMOVED***event['start']['dateTime']} {event['start']['timeZone'] "sample token.json"
                    })

        external_calendar_events[calendar_id] = external_events

    internal_emails = list(set(internal_emails))

    return {'external_calendar_events': external_calendar_events, 'internal_emails': internal_emails}


def get_client_meetings(year, month, calendar_ids):
    external_client_meetings = dict()
    external_events = get_events_with_external_attendees(
        year, month, calendar_ids)
    for calendar_id, events in external_events['external_calendar_events'].items():
        response = get_filtering_response_from_gpt(events)

        response_message = response.choices[0].message.content
        response_json = json.loads(response_message)
        client_meetings = [x for i, x in enumerate(
            events) if i in response_json['new_customer_meetings']]
        external_client_meetings[calendar_id] = client_meetings
    return external_client_meetings


def get_unique_client_meetings(year, month, calendar_ids):
    unique_client_meetings = []
    external_client_meetings = get_client_meetings(year, month, calendar_ids)

    for events in external_client_meetings.values():
        for event in events:
            if event not in unique_client_meetings:
                unique_client_meetings.append(event)

    return {'unique_client_meetings': unique_client_meetings}
