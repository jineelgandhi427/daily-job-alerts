# full_selenium_job_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests
import os

# --------------- CONFIG ------------------
KEYWORDS = ["mechatronics", "simulation", "test", "development", "r&d", "robotics", "automation"]
EXCLUDE = ["ausbildung", "praktikum", "werkstudent", "kfz"]
HEADLESS = True

# --------------- SELENIUM SETUP ----------
def create_driver():
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=chrome_options)

# --------------- SCRAPERS ----------------
def scrape_stepstone(driver):
    print("🔎 StepStone")
    jobs = []
    try:
        driver.get("https://www.stepstone.de/en/jobs/mechatronics/")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True).lower()
            link = "https://www.stepstone.de" + a['href']
            if any(k in title for k in KEYWORDS) and not any(x in title for x in EXCLUDE):
                jobs.append((title.title(), link))
    except Exception as e:
        print("❌ StepStone error:", e)
    return jobs

def scrape_linkedin():
    print("🔎 LinkedIn (Public filtered URLs)")
    return [("LinkedIn – Mechatronics/Simulation", "https://www.linkedin.com/jobs/search/?keywords=Mechatronics&location=Germany&f_TP=1&f_WT=2&sortBy=DD")]

# --------------- EMAIL -------------------
def format_email(jobs_by_source):
    html = "<h2>🔍 Matched Jobs – Germany (Full-Time)</h2><ul>"
    for source, jobs in jobs_by_source.items():
        if not jobs:
            continue
        html += f"<h3>{source}</h3>"
        for title, link in jobs:
            html += f"<li><a href='{link}'>{title}</a></li>"
    html += "</ul><p>This is an automated alert based on your profile.</p>"
    return html

def send_email(subject, html_content):
    api_key = os.getenv("BREVO_API_KEY")
    receiver = os.getenv("RECEIVER_EMAIL")
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Daily JobBot", "email": "jineelgandhi426@gmail.com"},
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
    print("📤 Email response:", res.status_code)
    print(res.text)

# --------------- MAIN --------------------
def run():
    print("🚀 Running Selenium-based job scraper...")
    driver = create_driver()
    jobs = {
        "StepStone": scrape_stepstone(driver),
        "LinkedIn": scrape_linkedin()
    }
    driver.quit()

    html = format_email(jobs)
    send_email("🔔 Daily Germany Job Alerts – Profile Matched", html)

if __name__ == "__main__":
    run()
