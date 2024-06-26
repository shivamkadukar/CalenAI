# CalenAI

Self hosted calendar assistant designed to streamline your meeting management by leveraging the power of AI.
Integrating seamlessly with Google Calendar, CalenAI identifies and categorizes potential client meetings, providing users with comprehensive insights and reports.


## Setup
Create a python virtual environment
```bash
python -m venv venv
```

Install dependencies
```bash
pip install -r CalenAI-backend\requirements.txt
```
in linux distros, you may require to use `pip3` instead of `pip`

## Connecting Google Calendar to CalenAI
Follow the quick startup steps in the google developer docs at [Calendar API Quickstart](https://developers.google.com/calendar/api/quickstart/python)
Finally output of following this steps would be generation of a oauth_credentials json file.

### Generate Google Calendar access token
> this step is common to all type of hosting

Store the downloaded oauth credentials files to `CalenAI-backend\auth\oauth_credentials.json`

Run token generation setup - 
```bash
python google_calendar_token_generation.py
```

Give the necessary access to download `token.json` file. 
Store the downloaded file to `CalenAI-backend\auth\token.json`

<!-- ## Local Run/Debug
Open `index.html` in `CalenAI-frontend`. Start a live server using vscode extension.

Run and Debug `CalenAI-backend`. 
For local run, CORS policy has for backend has been set to allow requests from http://127.0.0.1:5500/ -->
with the changes made for hosting via docker it is no longer supported to run locally. I will be adding it into a separate branch or will work on resolving the local run issue. Read section below for docker hosting.

## Local Hosting with Docker
Run the following docker compose command to build the frontend and backend containers.
```bash
docker compose up --build
```

This will create the docker images and start the CalenAI container service with a frontend and backend container and run this container.

## Hosting on AWS
Work in progress

### Project Roadmap
- [x] Added Support for run the applicatin locally in debug mode
- [x] Added Support for getting meeting insights from google calendar
- [x] Local Hosting with Docker
- [ ] Hosting on AWS
