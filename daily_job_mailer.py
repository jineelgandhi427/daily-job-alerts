
import requests
from bs4 import BeautifulSoup
import os

def fetch_jobs_stepstone():
    jobs = []
    url = "https://www.stepstone.de/jobs/mechatronics"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        for link in soup.select("a[data-at=job-item-title]"):
            title = link.text.strip()
            href = "https://www.stepstone.de" + link.get("href")
            jobs.append(f"{title} – StepStone\n{href}")
    except Exception as e:
        jobs.append(f"StepStone error: {e}")
    return jobs

def fetch_jobs_jobtensor():
    jobs = []
    url = "https://www.jobtensor.com/de/Mechatronik-Jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        for item in soup.select("a.position_title"):
            title = item.text.strip()
            href = "https://www.jobtensor.com" + item.get("href")
            jobs.append(f"{title} – Jobtensor\n{href}")
    except Exception as e:
        jobs.append(f"Jobtensor error: {e}")
    return jobs

def fetch_jobs_linkedin():
    jobs = []
    url = "https://www.linkedin.com/jobs/search?keywords=Mechatronics&location=Germany&f_TPR=r86400"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        for link in soup.find_all("a", class_="base-card__full-link"):
            title = link.get_text(strip=True)
            href = link.get("href")
            jobs.append(f"{title} – LinkedIn\n{href}")
    except Exception as e:
        jobs.append(f"LinkedIn error: {e}")
    return jobs

def send_email(job_list):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
    SENDER_EMAIL = "jineelgandhi426@gmail.com"

    html_body = "<h2>🔍 Matched Jobs – Germany</h2><ul>"
    for job in job_list:
        if "http" in job:
            title, link = job.split("\n")
            html_body += f"<li><strong>{title}</strong><br><a href='{link}'>{link}</a></li>"
    html_body += "</ul>"

    data = {
        "sender": {"name": "Daily JobBot", "email": SENDER_EMAIL},
        "to": [{"email": RECEIVER_EMAIL}],
        "subject": "🔔 Daily Germany Job Alerts – Profile Matched",
        "htmlContent": html_body,
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
        json=data
    )

    if response.status_code == 201:
        print("✅ Email sent successfully.")
    else:
        print(f"❌ Failed to send email: {response.status_code} {response.text}")

def main():
    job_list = []
    job_list += fetch_jobs_stepstone()
    job_list += fetch_jobs_jobtensor()
    job_list += fetch_jobs_linkedin()

    if any("http" in j for j in job_list):
        send_email(job_list)
    else:
        send_email(["No matching jobs found today."])

if __name__ == "__main__":
    main()
