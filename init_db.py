from datetime import datetime, timedelta
from extensions import db
from models import Patient, Doctor, Appointment, Reminder

def init_db():
    db.drop_all()
    db.create_all()

    # Create doctors
    doctor1 = Doctor(name="Dr. Thabo Dlamini")
    doctor2 = Doctor(name="Dr. Naledi Molefe")

    # Create patients
    patient1 = Patient(name="Sipho Ndlovu", phone="+27123456789")
    patient2 = Patient(name="Zanele Khumalo", phone="+27987654321")

    # Add to session
    db.session.add_all([doctor1, doctor2, patient1, patient2])
    db.session.commit()

    # Create appointments
    appt1 = Appointment(
        doctor_id=doctor1.id,
        patient_id=patient1.id,
        appointment_date=datetime.utcnow() + timedelta(minutes=1)  # upcoming appointment
    )
    appt2 = Appointment(
        doctor_id=doctor2.id,
        patient_id=patient2.id,
        appointment_date=datetime.utcnow() + timedelta(minutes=2)
    )
    db.session.add_all([appt1, appt2])
    db.session.commit()

    # Create reminders for these appointments
    reminder1 = Reminder(
        appointment_id=appt1.id,
        reminder_time=datetime.utcnow(),  # due now
        channel='sms',
        sent=False
    )
    reminder2 = Reminder(
        appointment_id=appt2.id,
        reminder_time=datetime.utcnow(),  # due now
        channel='sms',
        sent=False
    )
    db.session.add_all([reminder1, reminder2])
    db.session.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized with mock data.")