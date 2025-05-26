USE_TWILIO = False  # Change to True when ready to send real SMS

def send_sms(doctor_name, patient_name, phone):
    """
    Sends a personalized SMS reminder to the patient about their appointment.

    Args:
        doctor_name (str): Doctor's name
        patient_name (str): Patient's name
        phone (str): Patient's phone number in E.164 format (e.g. +27123456789)

    Returns:
        dict: Status of the SMS send attempt
    """
    message_text = f"Dear {patient_name}, this is a reminder from Dr. {doctor_name} about your upcoming appointment. Please confirm."

    if USE_TWILIO:
        # Twilio real send logic
        from twilio.rest import Client

        # TODO: Replace with your actual Twilio credentials
        account_sid = "YOUR_TWILIO_ACCOUNT_SID"
        auth_token = "YOUR_TWILIO_AUTH_TOKEN"
        twilio_phone_number = "+YourTwilioNumber"

        client = Client(account_sid, auth_token)
        try:
            message = client.messages.create(
                body=message_text,
                from_=twilio_phone_number,
                to=phone
            )
            return {
                "name": patient_name,
                "phone": phone,
                "status": "Sent",
                "sid": message.sid
            }
        except Exception as e:
            return {
                "name": patient_name,
                "phone": phone,
                "status": "Failed",
                "error": str(e)
            }
    else:
        # Simulated send for testing without Twilio
        print(f"Simulated SMS to {patient_name} ({phone}): {message_text}")
        return {
            "name": patient_name,
            "phone": phone,
            "status": "Simulated reminder sent"
        }