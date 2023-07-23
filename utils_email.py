from email.message import EmailMessage
import ssl
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def send_verify_email(email_receiver, v_link ):
    email_sender = os.getenv("email_sender")
    email_password =  os.getenv("email_password")
    # print(email_sender, email_password)
    
    subject = "Please Verify your email "
    
    body = f"""

    Hello,

    This is just a verification mail.

    verify link 
    {v_link}

    Regards,
    Rakib
    """

    context = ssl.create_default_context()
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

