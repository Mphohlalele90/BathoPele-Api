import os
from datetime import datetime
from models import Reminder
from extensions import db

# Use Twilio only if this is True, otherwise simulate sending
USE_TWILIO = False  # Set True to enable actual sending

if USE_TWILIO:
    from twilio.rest import Client

    TWILIO_SID = os.getenv('TWILIO_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE = os.getenv('TWILIO_PHONE')

    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
else:
    # Mock Twilio phone for simulation
    TWILIO_PHONE = "+1234567890"


def send_reminder(reminder: Reminder):
    appointment = reminder.appointment
    patient = appointment.patient
    doctor = appointment.doctor
    appointment_time_str = appointment.appointment_date.strftime('%Y-%m-%d %H:%M')

    message_body = (
        f"Reminder: You have an appointment with Dr. {doctor.name} on {appointment_time_str}."
    )

    if USE_TWILIO:
        try:
            if reminder.channel == 'sms':
                message = client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE,
                    to=patient.phone
                )
            elif reminder.channel == 'whatsapp':
                message = client.messages.create(
                    body=message_body,
                    from_='whatsapp:' + TWILIO_PHONE,
                    to='whatsapp:' + patient.phone
                )
            else:
                print(f"Unknown channel {reminder.channel}, skipping message")
                return False

            reminder.sent = True
            db.session.commit()
            print(f"Sent reminder {reminder.id} to {patient.phone}")
            return True

        except Exception as e:
            print(f"Error sending reminder {reminder.id}: {e}")
            return False

    else:
        # Simulate sending SMS or WhatsApp message
        print(f"[SIMULATION] Sending reminder to {patient.phone} via {reminder.channel.upper()}")
        print(f"Message: {message_body}")

        # Mark reminder as sent in DB to simulate success
        reminder.sent = True
        db.session.commit()
        print(f"[SIMULATION] Marked reminder {reminder.id} as sent")
        return True


def process_due_reminders():
    now = datetime.utcnow()
    due_reminders = Reminder.query.filter(
        Reminder.sent == False,
        Reminder.reminder_time <= now
    ).all()

    for reminder in due_reminders:
        send_reminder(reminder)