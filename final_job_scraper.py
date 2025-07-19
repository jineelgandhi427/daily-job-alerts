# full_job_scraper.py

import requests
from bs4 import BeautifulSoup
import re
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# --- CONFIG ---
KEYWORDS = ["mechatronics", "simulation", "r&d", "test engineer", "development", "automation"]
EXCLUDE = ["kfz", "ausbildung", "praktikum", "werkstudent", "techniker"]
TARGET_COUNTRY = "Germany"

# StepStone scraper (with timeout handling)
def scrape_stepstone():
    print("🔎 Scraping StepStone...")
    url = "https://www.stepstone.de/en/jobs/mechatronics/"
    jobs = []

    try:
        resp = requests.get(url, timeout=20)
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True)
            link = "https://www.stepstone.de" + a["href"]

            if any(k in title.lower() for k in KEYWORDS) and not any(x in title.lower() for x in EXCLUDE):
                jobs.append((title, link))
    except requests.exceptions.RequestException as e:
        print(f"⚠️ StepStone scrape failed: {e}")
    return jobs

# Jobtensor scraper
def scrape_jobtensor():
    print("🔎 Scraping Jobtensor...")
    url = "https://www.jobtensor.com/Mechatronics-Jobs-Germany"
    jobs = []

    try:
        resp = requests.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        for div in soup.select("div.job-offer"):
            a = div.find("a", href=True)
            if not a:
                continue
            title = a.get_text(strip=True)
            link = "https://www.jobtensor.com" + a["href"]

            if any(k in title.lower() for k in KEYWORDS) and not any(x in title.lower() for x in EXCLUDE):
                jobs.append((title, link))
    except Exception as e:
        print(f"⚠️ Jobtensor scrape failed: {e}")
    return jobs

# Monster scraper
def scrape_monster():
    print("🔎 Scraping Monster...")
    url = "https://www.monster.de/jobs/suche?q=mechatronik&where=Deutschland"
    jobs = []

    try:
        resp = requests.get(url, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.select("a.card-link"):
            title = a.get_text(strip=True)
            link = a["href"]

            if any(k in title.lower() for k in KEYWORDS) and not any(x in title.lower() for x in EXCLUDE):
                jobs.append((title, link))
    except Exception as e:
        print(f"⚠️ Monster scrape failed: {e}")
    return jobs

# Format email body
def format_email(jobs_by_source):
    html = "<h2>🔍 Matched Jobs – Germany (Full-Time)</h2><ul>"
    for source, jobs in jobs_by_source.items():
        if not jobs:
            continue
        html += f"<h3>{source}</h3>"
        for title, link in jobs:
            html += f"<li><a href='{link}'>{title}</a></li>"
    html += "</ul><p>This is an automated job alert based on your Mechatronics profile.</p>"
    return html

# Send email via Brevo
def send_email(subject, html_content):
    api_key = os.getenv("BREVO_API_KEY")
    receiver = os.getenv("RECEIVER_EMAIL")

    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Daily JobBot", "email": "daily@jobbot.ai"},
        "to": [{"email": receiver}],
        "subject": subject,
        "htmlContent": html_content
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 201:
        print("✅ Email sent successfully.")
    else:
        print(f"❌ Failed to send email: {res.status_code}", res.text)

# Run all scrapers
def run():
    all_jobs = {
        "StepStone": scrape_stepstone(),
        "Jobtensor": scrape_jobtensor(),
        "Monster": scrape_monster()
    }

    total = sum(len(jobs) for jobs in all_jobs.values())
    print(f"\n✅ Found {total} matching jobs across all platforms.\n")

    html = format_email(all_jobs)
    send_email("🔔 Daily Germany Job Alerts – Profile Matched", html)

if __name__ == "__main__":
    run()
