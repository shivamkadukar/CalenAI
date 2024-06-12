import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

token_file_path = os.getenv("TOKEN_FILE_PATH")
scopes = os.getenv("SCOPES")
credentials_file_path = os.getenv("CREDENTIALS_FILE_PATH")

if os.path.exists(token_file_path):
    creds = Credentials.from_authorized_user_file(token_file_path, scopes)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file_path, scopes)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_file_path, 'w') as token:
        token.write(creds.to_json())
