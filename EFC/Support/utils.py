from django.core.mail import send_mail

def send_email_notification(subject, message, to_email):
    # send_mail(subject, message, 'no-reply@yourapp.com', [to_email])
    print(f"Sending SMS to {to_email}: {message}")

def send_sms_notification(phone_number, message):
    # Example with print; replace with real SMS API like Twilio
    print(f"Sending SMS to {phone_number}: {message}")