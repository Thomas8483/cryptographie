import smtplib
import ssl

# Set up email variables
sender_email = 'test13@mailfence.com'
receiver_email = 'test14@mailfence.com'

# Set up the SMTP server
smtp_server = 'smtp.mailfence.com'
smtp_port = 465
smtp_username = 'test13'
smtp_password = 'suwtov-zuFza6-mokhus'

# Create a secure SSL context
context = ssl.create_default_context()

# Create the email message
subject = "Test Email"
body = "Hello, this is a test email."
message = f"Subject: {subject}\nFrom: {sender_email}\nTo: {receiver_email}\n\n{body}"


server = smtplib.SMTP_SSL(smtp_server, smtp_port, context=context)
server.login(smtp_username, smtp_password)
server.sendmail(sender_email, receiver_email, message)
server.quit()
