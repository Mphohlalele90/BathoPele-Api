from flask import request, jsonify
from extensions import db
from models import Doctor, Patient, Appointment, Reminder
from datetime import datetime, timedelta
import os
from twilio.rest import Client

TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def send_sms(to, body):
    message = twilio_client.messages.create(
        body=body,
        from_=TWILIO_PHONE,
        to=to
    )
    return message.sid

def setup_routes(app):

    @app.route('/reminders/schedule', methods=['POST'])
    def schedule_reminder():
        data = request.json
        appointment_id = data['appointment_id']
        minutes_before = data.get('minutes_before', 60)
        channel = data.get('channel', 'sms')

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        reminder_time = appointment.appointment_date - timedelta(minutes=minutes_before)

        reminder = Reminder(
            appointment_id=appointment_id,
            reminder_time=reminder_time,
            channel=channel
        )
        db.session.add(reminder)
        db.session.commit()
        return jsonify({'message': 'Reminder scheduled', 'id': reminder.id})

    @app.route('/reminders', methods=['GET'])
    def get_reminders():
        reminders = Reminder.query.all()
        result = []
        for r in reminders:
            result.append({
                'id': r.id,
                'appointment_id': r.appointment_id,
                'reminder_time': r.reminder_time.strftime('%Y-%m-%d %H:%M'),
                'sent': r.sent,
                'channel': r.channel,
                'doctor': r.appointment.doctor.name,
                'patient': r.appointment.patient.name,
                'appointment_date': r.appointment.appointment_date.strftime('%Y-%m-%d %H:%M')
            })
        return jsonify(result)

    @app.route('/reminders/send/<int:reminder_id>', methods=['POST'])
    def send_reminder_route(reminder_id):
        reminder = Reminder.query.get(reminder_id)
        if not reminder:
            return jsonify({'error': 'Reminder not found'}), 404

        appointment = reminder.appointment
        patient_phone = appointment.patient.phone

        message_body = (
            f"Hi {appointment.patient.name}, "
            f"this is a reminder for your appointment with {appointment.doctor.name} "
            f"on {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')}."
        )

        try:
            sid = send_sms(patient_phone, message_body)
            reminder.sent = True
            db.session.commit()
            return jsonify({'message': 'Reminder sent', 'sid': sid})
        except Exception as e:
            return jsonify({'error': str(e)}), 500