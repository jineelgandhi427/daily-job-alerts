import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os

# Sample jobs from StepStone and Indeed (simulate scraping results)
job_data = [
    {
        "title": "Mechatronics Test Engineer",
        "company": "Bosch GmbH",
        "location": "Stuttgart, Germany",
        "date_posted": "Today",
        "link": "https://www.stepstone.de/job/mechatronics-test-engineer-bosch"
    },
    {
        "title": "Simulation Engineer for Autonomous Systems",
        "company": "BMW Group",
        "location": "Munich, Germany",
        "date_posted": "Yesterday",
        "link": "https://www.indeed.de/viewjob?jk=simulation-engineer-bmw"
    },
    {
        "title": "Frontend Developer",
        "company": "Unknown",
        "location": "Berlin, Germany",
        "date_posted": "Today",
        "link": "https://irrelevant-job.de"
    }
]

keywords = [
    "mechatronics", "simulation", "test engineer", "sensor", "cad", "fusion 360", "solidworks", "reliability testing",
    "system integration", "angle sensor", "test bench", "digital twin", "robotics", "python", "unity", "ros"
]

def matches_profile(job_title):
    title = job_title.lower()
    return any(keyword in title for keyword in keywords)

filtered_jobs = [job for job in job_data if matches_profile(job['title'])]

def format_email_body(jobs):
    if not jobs:
        return "No matching jobs found today."

    body = "🛠️ <b>Daily Job Opportunities in Germany</b><br><br>"
    body += f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}<br><br>"
    body += "Here are your latest matching job openings:<br><br>"
    for i, job in enumerate(jobs, start=1):
        body += f"<b>{i}. {job['title']}</b><br>"
        body += f"{job['company']} – {job['location']}<br>"
        body += f"<i>Posted:</i> {job['date_posted']}<br>"
        body += f"<a href='{job['link']}'>Apply Now</a><br><br>"
    body += "<br>Good luck!<br><br>– Your Job Bot 🤖"
    return body

sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("APP_PASSWORD")
subject = "🔔 Daily Germany Job Alerts – Mechatronics & Simulation"

msg = MIMEMultipart("alternative")
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
body = format_email_body(filtered_jobs)
msg.attach(MIMEText(body, "html"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Error sending email:", str(e))
