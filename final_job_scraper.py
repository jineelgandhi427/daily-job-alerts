# final_job_scraper.py

import requests
from bs4 import BeautifulSoup
import os

# ---------------- CONFIG ---------------- #

KEYWORDS = [
    "mechatronics", "simulation", "test", "r&d", "development",
    "automation", "robotics", "validation", "hardware", "embedded"
]
EXCLUDE = ["ausbildung", "intern", "praktikum", "werkstudent", "kfz"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------- SCRAPERS ---------------- #

def scrape_stepstone():
    print("🔎 StepStone")
    jobs = []
    try:
        url = "https://www.stepstone.de/en/jobs/mechatronics/"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True).lower()
            link = "https://www.stepstone.de" + a["href"]
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print("⚠️ StepStone error:", e)
    return jobs

def scrape_monster():
    print("🔎 Monster")
    jobs = []
    try:
        url = "https://www.monster.de/jobs/suche?q=mechatronik&where=Deutschland"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a.card-link"):
            title = a.get_text(strip=True).lower()
            link = a["href"]
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print("⚠️ Monster error:", e)
    return jobs

def scrape_jobtensor():
    print("🔎 Jobtensor")
    jobs = []
    try:
        url = "https://www.jobtensor.com/Mechatronics-Jobs-Germany"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.select("a.card-title"):
            title = a.get_text(strip=True).lower()
            link = "https://www.jobtensor.com" + a.get("href")
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print("⚠️ Jobtensor error:", e)
    return jobs

def scrape_linkedin():
    print("🔎 LinkedIn")
    jobs = []
    urls = [
        "https://www.linkedin.com/jobs/search/?keywords=Mechatronics&location=Germany&f_TP=1&f_WT=2&sortBy=DD",
        "https://www.linkedin.com/jobs/search/?keywords=Simulation&location=Germany&f_TP=1&f_WT=2&sortBy=DD"
    ]
    for url in urls:
        jobs.append(("LinkedIn – Mechatronics/Simulation", url))
    return jobs

def scrape_xing():
    print("🔎 Xing")
    jobs = []
    try:
        url = "https://www.xing.com/jobs/search?keywords=mechatronik&location=germany"
        res = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            title = a.get_text(strip=True).lower()
            if "/jobs/" in href and any(k in title for k in KEYWORDS):
                full_link = "https://www.xing.com" + href if href.startswith("/") else href
                jobs.append((title.title(), full_link))
    except Exception as e:
        print("⚠️ Xing error:", e)
    return jobs

def scrape_arbeitsagentur():
    print("🔎 Bundesagentur für Arbeit")
    jobs = []
    try:
        url = "https://jobboerse.arbeitsagentur.de/vamJB/startseite.html"
        res = requests.get(url, headers=HEADERS, timeout=20)
        if res.status_code == 200:
            jobs.append(("Bundesagentur Start Page", url))
    except Exception as e:
        print("⚠️ Arbeitsagentur error:", e)
    return jobs

# ---------------- EMAIL ---------------- #

def format_email(jobs_by_source):
    html = "<h2>🔍 Matched Jobs – Germany</h2><ul>"
    for source, jobs in jobs_by_source.items():
        if not jobs:
            continue
        html += f"<h3>{source}</h3>"
        for title, link in jobs:
            html += f"<li><a href='{link}'>{title}</a></li>"
    html += "</ul><p>This is an automated alert based on your resume profile.</p>"
    return html

def send_email(subject, html_content):
    api_key = os.getenv("BREVO_API_KEY")
    receiver = os.getenv("RECEIVER_EMAIL")
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Daily JobBot", "email": "jineelgandhi426@gmail.com"},
        "to": [{"email": receiver}],
        "subject": subject,
        "htmlContent": html_content or "<p>No jobs found today.</p>"
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }
    res = requests.post(url, json=payload, headers=headers)
    print("📤 Brevo:", res.status_code, res.text)

# ---------------- MAIN ---------------- #

def run():
    print("🚀 Running scraper...")
    jobs_by_source = {
        "LinkedIn": scrape_linkedin(),
        "StepStone": scrape_stepstone(),
        "Monster": scrape_monster(),
        "Jobtensor": scrape_jobtensor(),
        "Xing": scrape_xing(),
        "Arbeitsagentur": scrape_arbeitsagentur()
    }
    html = format_email(jobs_by_source)
    send_email("🔔 Daily Germany Job Alerts – Profile Matched", html)

if __name__ == "__main__":
    run()
