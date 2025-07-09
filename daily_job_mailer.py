
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

# Keywords extracted from resume (Mechatronics, Sensors, Simulation, CAD, Python, etc.)
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

# Target job boards (static URLs and scraped)
SEARCH_URLS = {
    "LinkedIn - Mechatronics (24h)": "https://www.linkedin.com/jobs/search/?keywords=Mechatronics%20Engineer&location=Germany&f_TP=1&sortBy=DD",
    "LinkedIn - Simulation (24h)": "https://www.linkedin.com/jobs/search/?keywords=Simulation%20Engineer&location=Germany&f_TP=1&sortBy=DD",
    "Indeed": "https://de.indeed.com/jobs?q={query}&l=Germany&fromage=1",
    "StepStone": "https://www.stepstone.de/en/jobs/{query}/germany/",
    "Jobtensor": "https://jobtensor.com/Jobs?q={query}&l=germany"
}

def fetch_indeed_jobs(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = SEARCH_URLS["Indeed"].format(query=query.replace(" ", "+"))
    jobs = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for div in soup.find_all("a", href=True):
            title = div.get_text(strip=True)
            link = div["href"]
            if any(k in title.lower() for k in KEYWORDS) and "pagead" not in link:
                jobs.append((title, "Indeed", "https://de.indeed.com" + link))
    except:
        pass
    return jobs

def fetch_stepstone_jobs(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = SEARCH_URLS["StepStone"].format(query=query.replace(" ", "-"))
    jobs = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True)
            href = link["href"]
            if "job" in href and any(k in title.lower() for k in KEYWORDS):
                jobs.append((title, "StepStone", href if href.startswith("http") else "https://www.stepstone.de" + href))
    except:
        pass
    return jobs

def fetch_jobtensor_links(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = SEARCH_URLS["Jobtensor"].format(query=query.replace(" ", "+"))
    jobs = []
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            href = a["href"]
            if any(k in title.lower() for k in KEYWORDS) and href.startswith("/Job"):
                jobs.append((title, "Jobtensor", "https://jobtensor.com" + href))
    except:
        pass
    return jobs

def collect_jobs():
    jobs = []
    for query in SEARCH_TERMS:
        jobs += fetch_indeed_jobs(query)
        jobs += fetch_stepstone_jobs(query)
        jobs += fetch_jobtensor_links(query)
    for label, link in SEARCH_URLS.items():
        if "LinkedIn" in label:
            jobs.append((label, "LinkedIn", link))
    return jobs

def format_email(jobs):
    if not jobs:
        return "No matching jobs found today."
    html = f"<h3>🔍 Matched Jobs – {datetime.now().strftime('%d %B %Y')}</h3><ul>"
    for title, source, link in jobs:
        html += f"<li><b>{title}</b> – <i>{source}</i><br><a href='{link}'>Apply Now</a></li><br>"
    html += "</ul><br><i>This is an automated message.</i>"
    return html

sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("APP_PASSWORD")

message = MIMEMultipart("alternative")
message["Subject"] = "🔔 Daily Germany Job Alerts – AI Filtered"
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
