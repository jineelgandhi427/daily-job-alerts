import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os

# Job links (edit or replace with live scraped links)
job_links = [
    "https://www.linkedin.com/jobs/search?keywords=Mechatronics%20Engineer&location=Germany",
    "https://www.indeed.com/q-mechatronics-engineer-germany-jobs.html",
    "https://www.stepstone.de/en/jobs/mechatronics/"
]

def format_email_body(links):
    body = "🛠️ *Daily Job Opportunities in Germany*\n\n"
    body += f"Date: {datetime.now().strftime('%d %B %Y')}\n\n"
    body += "Here are your latest job openings:\n\n"
    for i, link in enumerate(links, start=1):
        body += f"{i}. {link}\n"
    body += "\nBest of luck!\n\n– Your Job Bot 🤖"
    return body

# Use environment variables for security
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("APP_PASSWORD")

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = "🔔 Daily Germany Job Alerts – Mechatronics & Simulation"
msg.attach(MIMEText(format_email_body(job_links), 'plain'))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Error sending email:", str(e))
