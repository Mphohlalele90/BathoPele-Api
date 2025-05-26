from flask import Flask, jsonify
#from twilio.rest import Client
from flask_sqlalchemy import SQLAlchemy
import random
from dotenv import load_dotenv
import os

load_dotenv()
print("Working directory:", os.getcwd())

# Load Twilio environment variables
account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_PHONE_NUMBER')  # Make sure your .env uses this exact name

if not all([account_sid, auth_token, twilio_number]):
    raise EnvironmentError("Missing one or more required Twilio environment variables.")

print("SID:", account_sid[:6] + "...")
print("Twilio Number:", twilio_number)
print("All keys:", list(os.environ.keys()))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'  # Change as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    doctor = db.relationship('Doctor', backref='patients')

# If you want to switch between real Twilio and mock easily:
USE_MOCK_SMS = True

if not USE_MOCK_SMS:
    from twilio.rest import Client
    client = Client(account_sid, auth_token)

def mock_send_sms(body, from_, to):
    print(f"[SIMULATED SMS] From: {from_}, To: {to}, Body: {body}")
    # Simulate success/failure based on phone number or randomly
    if to.startswith("+27"):
        # Simulate success
        return {"sid": "SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"}
    else:
        # Simulate failure
        raise Exception("Simulated sending error: Invalid phone number format.")

@app.route('/send-reminders', methods=['GET'])
def send_reminders():
    patients = Patient.query.all()
    appointment_times = ["10:00 AM", "11:30 AM", "2:00 PM", "3:45 PM"]

    # Assign doctors to patients without one, then commit once
    patients_without_doctors = [p for p in patients if not p.doctor]
    for patient in patients_without_doctors:
        random_doctor = Doctor.query.order_by(db.func.random()).first()
        patient.doctor = random_doctor
    if patients_without_doctors:
        db.session.commit()

    results = []

    for patient in patients:
        if not patient.phone:
            print(f"Skipping {patient.name} due to missing phone number.")
            results.append({"name": patient.name, "status": "Skipped", "reason": "No phone number"})
            continue

        appointment_time = random.choice(appointment_times)
        message_body = (
            f"Hi {patient.name}, this is a reminder from Goba Clinic. "
            f"Your appointment with Dr. {patient.doctor.name} is tomorrow at {appointment_time}. "
            f"Please reply YES to confirm or contact the clinic for changes."
        )

        try:
            if USE_MOCK_SMS:
                mock_send_sms(body=message_body, from_=twilio_number, to=patient.phone)
            else:
                client.messages.create(
                    body=message_body,
                    from_=twilio_number,
                    to=patient.phone
                )
            print(f" Sent to {patient.name} ({patient.phone})")
            results.append({"name": patient.name, "phone": patient.phone, "status": "Sent"})
        except Exception as e:
            print(f" Failed for {patient.name}: {e}")
            results.append({"name": patient.name, "phone": patient.phone, "status": "Failed", "error": str(e)})

    return jsonify(results), 200

@app.route('/')
def home():
    return "Welcome to BathoPele API!"

if __name__ == '__main__':
    # Create tables if not exist (optional, for quick testing)
    with app.app_context():
        db.create_all()
    app.run(debug=True)