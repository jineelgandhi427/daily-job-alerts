
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

# Job filtering keywords (based on resume)
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

def fetch_links(query, url_template, site_name):
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
    results = []
    for term in SEARCH_TERMS:
        results += fetch_links(term, SEARCH_URLS["Indeed"], "Indeed")
        results += fetch_links(term, SEARCH_URLS["StepStone"], "StepStone")
        results += fetch_links(term, SEARCH_URLS["Jobtensor"], "Jobtensor")
    for label, link in SEARCH_URLS.items():
        if "LinkedIn" in label:
            results.append((label, "LinkedIn", link))
    return results

def format_email_body(jobs):
    date = datetime.now().strftime('%d %B %Y')
    if not jobs:
        return f"<p><b>No matching jobs found today.</b></p>"
    html = f"<h3>🔍 Matched Jobs – {date}</h3><ul>"
    for title, site, link in jobs:
        html += f"<li><b>{title}</b> – <i>{site}</i><br><a href='{link}'>Apply Now</a></li><br>"
    html += "</ul><br><i>This is an automated message.</i>"
    return html

# Environment variables from GitHub secrets
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SENDER_EMAIL = SMTP_LOGIN

# Prepare email
jobs = collect_jobs()
body = format_email_body(jobs)

msg = MIMEMultipart("alternative")
msg["Subject"] = "🔔 Daily Germany Job Alerts – Profile Matched"
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg.attach(MIMEText(body, "html"))

# Send email via Brevo SMTP
try:
    server = smtplib.SMTP()
    server.connect(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_LOGIN, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Error sending email:", str(e))
