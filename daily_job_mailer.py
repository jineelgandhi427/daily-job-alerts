import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Step 1: Define broad matching terms
INCLUDE_KEYWORDS = [
    "mechatronics", "simulation", "test", "sensor", "r&d", "hardware", "automation",
    "development engineer", "graduate", "entry", "robotics", "embedded"
]
EXCLUDE_KEYWORDS = ["ausbildung", "nurse", "sales", "praktikum", "pflege", "azubi"]

SEARCH_TERMS = [
    "mechatronics engineer", "test engineer", "simulation", "graduate engineer", "r&d engineer", "hardware developer"
]

# Step 2: Define sources
SOURCES = {
    "StepStone": "https://www.stepstone.de/en/jobs/{query}/germany/",
    "Jobtensor": "https://jobtensor.com/Jobs?q={query}&l=germany"
}

# Step 3: Scrape logic
def fetch_jobs(site_name, base_url, query):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = base_url.format(query=query.replace(" ", "+"))
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True).lower()
            if any(kw in title for kw in INCLUDE_KEYWORDS) and not any(x in title for x in EXCLUDE_KEYWORDS):
                full_url = a["href"]
                if not full_url.startswith("http"):
                    full_url = f"https://{site_name.lower()}.com{full_url}"
                jobs.append((title.title(), full_url, site_name))
    except Exception as e:
        print(f"❌ {site_name} failed: {e}")
    print(f"✅ {site_name}: {len(jobs)} jobs matched for '{query}'")
    return jobs

# Step 4: Collect all jobs
def collect_all_jobs():
    all_jobs = []
    for query in SEARCH_TERMS:
        for source, url in SOURCES.items():
            jobs = fetch_jobs(source, url, query)
            all_jobs.extend(jobs)
    return list(dict.fromkeys(all_jobs))  # remove duplicates

# Step 5: Format email content
def format_html(jobs):
    if not jobs:
        return "<p><b>No matching jobs found today.</b></p>"
    date = datetime.now().strftime('%d %B %Y')
    html = f"<h3>🔍 Matched Jobs – {date}</h3><ul>"
    for title, link, source in jobs:
        html += f"<li><b>{title}</b> – <i>{source}</i><br><a href='{link}' target='_blank'>Apply Now</a></li><br>"
    html += "</ul><br><i>This is an automated daily alert based on your resume.</i>"
    return html

# Step 6: Send email via Brevo API
def send_email(html_body):
    API_KEY = os.getenv("BREVO_API_KEY")
    headers = {
        "accept": "application/json",
        "api-key": API_KEY,
        "content-type": "application/json"
    }
    payload = {
        "sender": {"name": "Jineel Gandhi", "email": "jineelgandhi426@gmail.com"},
        "to": [{"email": "jineelgandhi426@gmail.com"}],
        "subject": "🔔 Daily Germany Job Alerts – Realtime Matches",
        "htmlContent": html_body
    }
    try:
        res = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
        if res.status_code == 201:
            print("✅ Email sent successfully.")
        else:
            print(f"❌ Email failed: {res.status_code} {res.text}")
    except Exception as e:
        print("❌ Email exception:", str(e))

# Run the full script
if __name__ == "__main__":
    job_list = collect_all_jobs()
    email_html = format_html(job_list)
    send_email(email_html)
