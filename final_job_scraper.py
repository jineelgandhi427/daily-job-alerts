# final_job_scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import requests
import os
import time

# -------------------- CONFIG -------------------- #
KEYWORDS = [
    "sensor", "test automation", "validation", "embedded systems", "signal processing",
    "cad", "mechatronics", "PCB design", "hardware", "prototyping", "robotics",
    "FEM", "SolidWorks", "digital twin", "python", "arduino"
]

EXCLUDE = [
    "ausbildung", "praktikum", "werkstudent", "kfz", "trainee", "intern",
    "student", "azubi", "school", "praktikant", "minijob"
]

EMAIL_TO = os.getenv("RECEIVER_EMAIL")
BREVO_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = "daily@jobbot.ai"
HEADLESS = True

# -------------------- HELPERS -------------------- #
def filter_job(title, description=""):
    combined = (title + " " + description).lower()
    return any(k in combined for k in KEYWORDS) and not any(e in combined for e in EXCLUDE)

def start_browser():
    chromedriver_autoinstaller.install()
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    return webdriver.Chrome(options=options)

# -------------------- SCRAPERS -------------------- #
def scrape_stepstone(driver):
    print("🔎 StepStone")
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
    print("🔎 LinkedIn (Static URLs Only)")
    return [
        ("LinkedIn – Mechatronics", "https://www.linkedin.com/jobs/search/?keywords=Mechatronics&location=Germany&f_TP=1&sortBy=DD"),
        ("LinkedIn – Simulation", "https://www.linkedin.com/jobs/search/?keywords=Simulation&location=Germany&f_TP=1&sortBy=DD")
    ]

# -------------------- EMAIL -------------------- #
def format_email(data):
    html = "<h2>🔍 Matched Jobs – Germany (Full-Time)</h2>"
    for site, jobs in data.items():
        html += f"<h3>{site}</h3><ul>"
        if not jobs:
            html += "<li>No jobs found.</li>"
        else:
            for title, link in jobs:
                html += f"<li><a href='{link}'>{title}</a></li>"
        html += "</ul>"
    html += "<p>This is an automated message based on your profile.</p>"
    return html

def send_email(html):
    print("📤 Sending email...")
    url = "https://api.brevo.com/v3/smtp/email"
    payload = {
        "sender": {"name": "Daily JobBot", "email": SENDER_EMAIL},
        "to": [{"email": EMAIL_TO}],
        "subject": "🔔 Daily Germany Job Alerts – Profile Matched",
        "htmlContent": html or "<p>No jobs found today.</p>"
    }
    headers = {
        "accept": "application/json",
        "api-key": BREVO_KEY,
        "content-type": "application/json"
    }
    res = requests.post(url, headers=headers, json=payload)
    print("📤 Brevo response:", res.status_code, res.text)

# -------------------- MAIN -------------------- #
def run():
    print("🚀 Running fixed job scraper...")
    driver = start_browser()

    data = {
        "StepStone": scrape_stepstone(driver),
        "LinkedIn": scrape_linkedin()
    }

    driver.quit()
    html = format_email(data)
    send_email(html)

if __name__ == "__main__":
    run()
