# full_job_scraper.py

import requests
from bs4 import BeautifulSoup
import re
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import time

# ---------------- CONFIG ---------------- #
KEYWORDS = [
    "mechatronics", "simulation", "test", "development", "r&d", "robotics",
    "automation", "system engineer", "embedded", "validation", "hardware"
]
EXCLUDE = ["ausbildung", "praktikum", "werkstudent", "kfz", "trainee", "intern"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---------------- SCRAPERS ---------------- #

def scrape_stepstone():
    print("🔎 StepStone")
    jobs = []
    try:
        url = "https://www.stepstone.de/en/jobs/mechatronics/"
        res = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True).lower()
            link = "https://www.stepstone.de" + a["href"]
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print(f"❌ StepStone failed: {e}")
    return jobs

def scrape_monster():
    print("🔎 Monster")
    jobs = []
    try:
        url = "https://www.monster.de/jobs/suche?q=mechatronik&where=Deutschland"
        res = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a.card-link"):
            title = a.get_text(strip=True).lower()
            link = a["href"]
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print(f"❌ Monster failed: {e}")
    return jobs

def scrape_jobtensor():
    print("🔎 Jobtensor")
    jobs = []
    try:
        url = "https://www.jobtensor.com/Mechatronics-Jobs-Germany"
        res = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a.card-title"):
            title = a.get_text(strip=True).lower()
            link = "https://www.jobtensor.com" + a.get("href")
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print(f"❌ Jobtensor failed: {e}")
    return jobs

def scrape_linkedin():
    print("🔎 LinkedIn (filtered public)")
    jobs = []
    urls = [
        "https://www.linkedin.com/jobs/search/?keywords=Mechatronics&location=Germany&f_TP=1&f_WT=2&sortBy=DD",
        "https://www.linkedin.com/jobs/search/?keywords=Simulation&location=Germany&f_TP=1&f_WT=2&sortBy=DD"
    ]
    for url in urls:
        jobs.append(("LinkedIn – Mechatronics/Simulation", url))
    return jobs

# (Optional future scrapers would follow same pattern)

# ---------------- EMAIL ---------------- #

def format_email(jobs_by_source):
    html = "<h2>🔍 Matched Jobs – Germany (Full-Time)</h2><ul>"
    for source, jobs in jobs_by_source.items():
        if not jobs:
            continue
        html += f"<h3>{source}</h3>"
        for title, link in jobs:
            html += f"<li><a href='{link}'>{title}</a></li>"
    html += "</ul><p>This is an automated message.</p>"
    return html

def send_email(subject, html_content):
    api_key = os.getenv("BREVO_API_KEY")
    receiver = os.getenv("RECEIVER_EMAIL")

    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Daily JobBot", "email": "jineelgandhi426@gmail.com"},
        "to": [{"email": receiver}],
        "subject": subject,
        "htmlContent": html_content or "<p>No jobs found today.</p>"  # fallback
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers)
    print("📤 Brevo response:", res.status_code)
    print(res.text)

    if res.status_code == 201:
        print("✅ Email sent.")
    else:
        print("❌ Email failed:", res.status_code, res.text)

# ---------------- MAIN ---------------- #

def run():
    print("🚀 Running job scraper...")

    job_data = {
        "StepStone": scrape_stepstone(),
        "Monster": scrape_monster(),
        "Jobtensor": scrape_jobtensor(),
        "LinkedIn": scrape_linkedin()
    }

    html = format_email(job_data)
    send_email("🔔 Daily Germany Job Alerts – Profile Matched", html)

if __name__ == "__main__":
    run()

