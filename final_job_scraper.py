import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ------------------ CONFIG ------------------ #
KEYWORDS = [
    "mechatronics", "simulation", "r&d", "robotics", "automation",
    "hardware", "system engineer", "test engineer", "development", "validation"
]
EXCLUDE = ["kfz", "ausbildung", "werkstudent", "praktikum", "intern", "trainee"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ------------------ SCRAPERS ------------------ #

def selenium_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=options)

def scrape_stepstone():
    print("🔎 StepStone")
    jobs = []
    try:
        url = "https://www.stepstone.de/en/jobs/mechatronics/"
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True).lower()
            link = "https://www.stepstone.de" + a["href"]
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print(f"❌ StepStone error: {e}")
    return jobs

def scrape_monster():
    print("🔎 Monster")
    jobs = []
    try:
        url = "https://www.monster.de/jobs/suche?q=mechatronik&where=Deutschland"
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
        for a in soup.select("a.card-link"):
            title = a.get_text(strip=True).lower()
            link = a["href"]
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print(f"❌ Monster error: {e}")
    return jobs

def scrape_jobtensor():
    print("🔎 Jobtensor")
    jobs = []
    try:
        url = "https://www.jobtensor.com/Mechatronics-Jobs-Germany"
        soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
        for a in soup.select("a.card-title"):
            title = a.get_text(strip=True).lower()
            link = "https://www.jobtensor.com" + a.get("href")
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print(f"❌ Jobtensor error: {e}")
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

def scrape_bundesagentur():
    print("🔎 Bundesagentur")
    jobs = []
    try:
        driver = selenium_driver()
        driver.get("https://jobboerse.arbeitsagentur.de/vamJB/startseite.html")
        time.sleep(5)
        jobs.append(("Bundesagentur Start Page", driver.current_url))
        driver.quit()
    except Exception as e:
        print(f"❌ Bundesagentur error: {e}")
    return jobs

# ------------------ EMAIL ------------------ #

def format_email(jobs_by_source):
    html = "<h2>🔍 Matched Jobs – Germany (Full-Time)</h2><ul>"
    for source, jobs in jobs_by_source.items():
        if jobs:
            html += f"<h3>{source}</h3>"
            for title, link in jobs:
                html += f"<li><a href='{link}'>{title}</a></li>"
    html += "</ul><p>This is an automated alert based on your profile.</p>"
    return html

def send_email(subject, html_content):
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")
    receiver = os.getenv("RECEIVER_EMAIL")

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

    response = requests.post(url, json=payload, headers=headers)
    print("📤 Email response:", response.status_code)
    print(response.text)
    if response.status_code == 201:
        print("✅ Email sent.")
    else:
        print("❌ Email failed.")

# ------------------ MAIN ------------------ #

def run():
    print("🚀 Running Selenium-based job scraper...")

    job_data = {
        "StepStone": scrape_stepstone(),
        "Monster": scrape_monster(),
        "Jobtensor": scrape_jobtensor(),
        "LinkedIn": scrape_linkedin(),
        "Bundesagentur": scrape_bundesagentur()
    }

    html = format_email(job_data)
    send_email("🔔 Daily Germany Job Alerts – Profile Matched", html)

if __name__ == "__main__":
    run()
