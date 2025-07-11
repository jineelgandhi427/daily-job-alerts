
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

KEYWORDS = [
    "mechatronics", "simulation", "sensor", "test engineer", "digital twin",
    "solidworks", "fusion 360", "robotics", "python", "ros", "unity", "test bench"
]

SEARCH_TERMS = [
    "mechatronics engineer",
    "sensor test engineer",
    "simulation engineer",
    "robotics developer",
    "digital twin engineer",
    "test development"
]

SEARCH_URLS = {
    "LinkedIn - Mechatronics (24h)": "https://www.linkedin.com/jobs/search/?keywords=Mechatronics%20Engineer&location=Germany&f_TP=1&sortBy=DD",
    "LinkedIn - Simulation (24h)": "https://www.linkedin.com/jobs/search/?keywords=Simulation%20Engineer&location=Germany&f_TP=1&sortBy=DD",
    "Indeed": "https://de.indeed.com/jobs?q={query}&l=Germany&fromage=1",
    "StepStone": "https://www.stepstone.de/en/jobs/{query}/germany/",
    "Jobtensor": "https://jobtensor.com/Jobs?q={query}&l=germany"
}

def fetch_links_from_site(query, url_template, site_name):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = url_template.format(query=query.replace(" ", "+"))
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True).lower()
            href = link["href"]
            if any(k in title for k in KEYWORDS) and "ausbildung" not in title:
                full_link = href if href.startswith("http") else f"https://{site_name.lower()}.de{href}"
                jobs.append((title.title(), site_name, full_link))
    except Exception:
        pass
    return jobs

def collect_jobs():
    all_jobs = []
    for term in SEARCH_TERMS:
        all_jobs += fetch_links_from_site(term, SEARCH_URLS["Indeed"], "Indeed")
        all_jobs += fetch_links_from_site(term, SEARCH_URLS["StepStone"], "StepStone")
        all_jobs += fetch_links_from_site(term, SEARCH_URLS["Jobtensor"], "Jobtensor")

    for label, link in SEARCH_URLS.items():
        if "LinkedIn" in label:
            all_jobs.append((label, "LinkedIn", link))
    return all_jobs

def format_email(jobs):
    if not jobs:
        return "No matching jobs found today."
    html = f"<h3>🔍 Matched Jobs – {datetime.now().strftime('%d %B %Y')}</h3><ul>"
    for title, source, link in jobs:
        html += f"<li><b>{title}</b> – <i>{source}</i><br><a href='{link}'>Apply Now</a></li><br>"
    html += "</ul><br><i>This is an automated message based on your resume profile.</i>"
    return html

sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("APP_PASSWORD")

message = MIMEMultipart("alternative")
message["Subject"] = "🔔 Daily Germany Job Alerts – Profile Matched"
message["From"] = sender_email
message["To"] = receiver_email

jobs = collect_jobs()
email_body = format_email(jobs)
message.attach(MIMEText(email_body, "html"))

try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(message)
        print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Error sending email:", str(e))
