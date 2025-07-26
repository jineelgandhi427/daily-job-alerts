# final_job_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import os
import json
import time

# -------------------- CONFIG -------------------- #
KEYWORDS = ["mechatronics", "simulation", "development", "test", "r&d", "robotics", "automation"]
EXCLUDE = ["ausbildung", "praktikum", "werkstudent", "intern", "kfz", "trainee"]
HEADLESS = True

EMAIL_TO = os.getenv("RECEIVER_EMAIL")
BREVO_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = "jineelgandhi426@gmail.com"

# -------------------- SCRAPERS -------------------- #

def start_browser():
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def filter_job(title):
    title = title.lower()
    return any(k in title for k in KEYWORDS) and not any(e in title for e in EXCLUDE)

def scrape_stepstone(driver):
    print("🔎 StepStone...")
    jobs = []
    try:
        driver.get("https://www.stepstone.de/en/jobs/mechatronics/")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True)
            link = "https://www.stepstone.de" + a["href"]
            if filter_job(title):
                jobs.append((title, link))
    except Exception as e:
        print("❌ StepStone error:", e)
    return jobs

def scrape_linkedin():
    print("🔎 LinkedIn (filtered)...")
    return [("LinkedIn – Mechatronics/Simulation", "https://www.linkedin.com/jobs/search/?keywords=Mechatronics&location=Germany&f_TP=1&sortBy=DD")]

def scrape_bundesagentur(driver):
    print("🔎 Bundesagentur...")
    jobs = []
    try:
        driver.get("https://jobboerse.arbeitsagentur.de/vamJB/startseite.html")
        time.sleep(6)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if filter_job(text) and "jobdetails" in link["href"]:
                jobs.append((text, "https://jobboerse.arbeitsagentur.de" + link["href"]))
    except Exception as e:
        print("❌ Bundesagentur error:", e)
    return jobs

# -------------------- EMAIL -------------------- #

def format_email(data):
    html = "<h2>🔍 Matched Jobs – Germany (Full-Time)</h2>"
    for source, jobs in data.items():
        html += f"<h3>{source}</h3><ul>"
        if not jobs:
            html += "<li>No jobs found.</li>"
        else:
            for title, link in jobs:
                html += f"<li><a href='{link}'>{title}</a></li>"
        html += "</ul>"
    html += "<p>This is an automated alert based on your profile.</p>"
    return html

def send_email(html):
    print("📤 Sending email...")
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Daily JobBot", "email": SENDER_EMAIL},
        "to": [{"email": EMAIL_TO}],
        "subject": "🔔 Daily Germany Job Alerts – Profile Matched",
        "htmlContent": html
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_KEY,
        "content-type": "application/json"
    }
    res = requests.post(url, headers=headers, json=payload)
    print("✅ Email response:", res.status_code, res.text)

# -------------------- MAIN -------------------- #

def run():
    print("🚀 Running Selenium-based job scraper...")
    driver = start_browser()

    jobs_by_site = {
        "StepStone": scrape_stepstone(driver),
        "LinkedIn": scrape_linkedin(),
        "Bundesagentur": scrape_bundesagentur(driver)
    }

    driver.quit()
    html = format_email(jobs_by_site)
    send_email(html)

if __name__ == "__main__":
    run()
