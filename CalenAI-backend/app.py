import os
from tabulate import tabulate
import pandas as pd
from flask import Flask, request, send_from_directory, jsonify, render_template
from flask_cors import CORS
from calendar_utils.google_calendar_utils import get_unique_client_meetings

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})


def print_results(unique_client_meetings):
    print('Total Client Meetings:', len(
        unique_client_meetings['unique_client_meetings']), '\n')

    print_data = [['Summary', 'Attendees']]
    for x in unique_client_meetings['unique_client_meetings']:
        attendees_new = []
        for attendee in x['attendees']:
            attendee_new = attendee
            if 'internal_email1.com' in attendee:
                attendee_new = attendee.split('@')[0]
            attendees_new.append(attendee_new)

        print_data.append([x['meeting_summary'], attendees_new])
    print(tabulate(print_data, headers="firstrow", tablefmt="grid"))


def save_results(year, month, calendar_ids, unique_client_meetings):
    unique_client_meetings_processed = [
        x for x in unique_client_meetings['unique_client_meetings']]
    for x in unique_client_meetings_processed:
        x['attendees'] = ','.join(x['attendees'])

    df = pd.DataFrame(unique_client_meetings_processed)

    calendar_ids_processed = sorted([x.split('@')[0] for x in calendar_ids])
    meetings_file_path = f'results/{year}_{month}_{",".join(calendar_ids_processed)}.csv'
    df.to_csv(meetings_file_path, index=False)
    return meetings_file_path


@app.route('/generate-file', methods=['POST'])
def generate_file():
    # Extract data from the AJAX request
    date = request.json['month']
    selected_year, selected_month = date.split('-')
    email_ids = request.json['emailIds']

    # Create the required format for the arguments
    formatted_arguments = [
        str(selected_year),
        str(selected_month),
        email_ids
    ]

    # Call the function with formatted arguments
    unique_client_meetings = get_unique_client_meetings(
        formatted_arguments[0], formatted_arguments[1], formatted_arguments[2])

    # Save the file and return the path
    meetings_file_path = save_results(
        formatted_arguments[0], formatted_arguments[1], formatted_arguments[2], unique_client_meetings)
    return jsonify({"filePath": meetings_file_path})


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/download')
def download_file():
    file_path = request.args.get('file')
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    return send_from_directory(directory, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
