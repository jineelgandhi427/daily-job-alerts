
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

# Search configuration
query_terms = [
    "mechatronics engineer", "simulation engineer", "test engineer",
    "sensor testing", "digital twin", "test bench", "robotics engineer"
]
job_sites = {
    "StepStone": "https://www.stepstone.de/en/jobs/{query}/germany/",
    "Indeed": "https://de.indeed.com/jobs?q={query}&l=Germany&fromage=1"
}

def fetch_jobs():
    jobs = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for site, url_template in job_sites.items():
        for term in query_terms:
            query = term.replace(" ", "+")
            url = url_template.format(query=query)
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all("a", href=True)
                found = set()
                for link in links:
                    href = link["href"]
                    if "job" in href and href not in found:
                        found.add(href)
                        jobs.append({
                            "title": term.title(),
                            "site": site,
                            "link": href if href.startswith("http") else "https://" + site.lower() + ".de" + href,
                            "date_posted": "Today"
                        })
            except Exception as e:
                continue
    return jobs

def format_email_body(jobs):
    if not jobs:
        return "No matching jobs found today."

    body = "🛠️ <b>Daily Job Opportunities in Germany</b><br><br>"
    body += f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}<br><br>"
    body += "Here are your latest matching job openings:<br><br>"
    for i, job in enumerate(jobs, start=1):
        body += f"<b>{i}. {job['title']}</b> – via {job['site']}<br>"
        body += f"<i>Posted:</i> {job['date_posted']}<br>"
        body += f"<a href='{job['link']}'>Apply Now</a><br><br>"
    body += "<br>Good luck!<br><br>– Your Job Bot 🤖"
    return body

# Fetch and format job list
job_data = fetch_jobs()
email_body = format_email_body(job_data)

# Email setup
sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("APP_PASSWORD")
subject = "🔔 Daily Germany Job Alerts – Live Matching Jobs"

msg = MIMEMultipart("alternative")
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(email_body, "html"))

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Error sending email:", str(e))
