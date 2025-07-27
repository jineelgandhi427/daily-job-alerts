# advanced_job_scraper_debug.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
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
SENDER_EMAIL = "jineelgandhi426@gmail.com"
HEADLESS = False  # Set to False for debugging

# -------------------- HELPERS -------------------- #
def filter_job(title, description=""):
    combined = (title + " " + description).lower()
    is_match = any(k in combined for k in KEYWORDS) and not any(e in combined for e in EXCLUDE)
    if not is_match:
        print(f"❌ Excluded: {title}")
    return is_match

def start_browser():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

# -------------------- SCRAPERS -------------------- #
def scrape_stepstone(driver):
    print("🔎 StepStone")
    jobs = []
    try:
        driver.get("https://www.stepstone.de/en/jobs/mechatronics/")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        with open("StepStone_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        for a in soup.select("a[href^='/en/job/']"):
            title = a.get_text(strip=True)
            link = "https://www.stepstone.de" + a["href"]
            if filter_job(title):
                jobs.append((title, link))
    except Exception as e:
        print("❌ StepStone error:", e)
    return jobs

def scrape_monster():
    print("🔎 Monster")
    jobs = []
    try:
        url = "https://www.monster.de/jobs/suche?q=mechatronik&where=Deutschland"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        with open("Monster_debug.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        for a in soup.select("a.card-link"):
            title = a.get_text(strip=True)
            link = a["href"]
            if filter_job(title):
                jobs.append((title, link))
    except Exception as e:
        print("❌ Monster error:", e)
    return jobs

def scrape_jobtensor():
    print("🔎 Jobtensor")
    jobs = []
    try:
        url = "https://www.jobtensor.com/Mechatronics-Jobs-Germany"
        resp = requests.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, "html.parser")
        with open("Jobtensor_debug.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        for a in soup.select("a.card-title"):
            title = a.get_text(strip=True)
            link = "https://www.jobtensor.com" + a["href"]
            if filter_job(title):
                jobs.append((title, link))
    except Exception as e:
        print("❌ Jobtensor error:", e)
    return jobs

def scrape_bundesagentur(driver):
    print("🔎 Bundesagentur")
    jobs = []
    try:
        driver.get("https://jobboerse.arbeitsagentur.de/vamJB/startseite.html")
        time.sleep(6)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        with open("Bundesagentur_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if filter_job(text) and "jobdetails" in link["href"]:
                jobs.append((text, "https://jobboerse.arbeitsagentur.de" + link["href"]))
    except Exception as e:
        print("❌ Bundesagentur error:", e)
    return jobs

def scrape_linkedin():
    print("🔎 LinkedIn (Static URLs Only)")
    return [
        ("LinkedIn – Mechatronics", "https://www.linkedin.com/jobs/search/?keywords=Mechatronics&location=Germany&f_TP=1&sortBy=DD"),
        ("LinkedIn – Simulation", "https://www.linkedin.com/jobs/search/?keywords=Simulation&location=Germany&f_TP=1&sortBy=DD")
    ]

def scrape_xing(driver):
    print("🔎 Xing")
    jobs = []
    try:
        driver.get("https://www.xing.com/jobs/search?keywords=mechatronik&location=Germany")
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        with open("Xing_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        for a in soup.select("a[href*='/jobs/']"):
            title = a.get_text(strip=True)
            link = a["href"]
            if link.startswith("/jobs/"):
                link = "https://www.xing.com" + link
            if filter_job(title):
                jobs.append((title, link))
    except Exception as e:
        print("❌ Xing error:", e)
    return jobs

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
    print("🚀 Running full job scraper...")
    driver = start_browser()

    data = {
        "StepStone": scrape_stepstone(driver),
        "Monster": scrape_monster(),
        "Jobtensor": scrape_jobtensor(),
        "LinkedIn": scrape_linkedin(),
        "Bundesagentur": scrape_bundesagentur(driver),
        "Xing": scrape_xing(driver)
    }

    with open("job_log.txt", "w", encoding="utf-8") as f:
        for site, jobs in data.items():
            f.write(f"{site}:\n")
            for title, link in jobs:
                f.write(f"{title} – {link}\n")
            f.write("\n")

    driver.quit()
    html = format_email(data)
    send_email(html)

if __name__ == "__main__":
    run()
