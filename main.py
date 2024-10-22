from flask import Flask, request, jsonify
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import re
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

scope = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name("test.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Test").sheet1


def validate_data(dat):
    errors = []

    if 'name' not in dat or dat['name'] == "":
        errors.append("error: Name is required")
    elif not re.match(r"^[a-zA-Zа-яА-Я]+$", dat['name']):
        errors.append("error: Some symbols are not required")

    if 'phone_number' not in dat or dat['phone_number'] == "":
        errors.append("error: Phone Number is required")
    elif not re.match(r"^380\d{9}$", dat['phone_number']):
        errors.append("error: Phone number format is not right")

    try:
        validate_email(dat['email'])
    except EmailNotValidError:
        errors.append("error: Email is not valid")

    return errors


@app.route('/submit', methods=['POST'])  # GET, POST, PATCH, PUT
def submit_form():
    data = request.json

    validate_errors = validate_data(data)

    if validate_errors:
        return jsonify({"errors": validate_errors}), 400

    try:
        sheet.append_row([
            data['name'],
            data['email'],
            data['phone_number']
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Data was saved to Google Sheets"}), 201


if __name__ == "__main__":
    app.run(debug=True)
