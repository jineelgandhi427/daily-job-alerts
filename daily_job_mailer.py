
import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Job filtering keywords (based on resume)
KEYWORDS = [
    "mechatronics", "simulation", "sensor", "test engineer", "digital twin",
    "solidworks", "fusion 360", "robotics", "python", "ros", "unity", "test bench"
]

SEARCH_TERMS = [
    "mechatronics engineer",
    "sensor test engineer",
    "simulation engineer",
    "robotics developer",
    "digital twin engineer",
    "test development"
]

SEARCH_URLS = {
    "LinkedIn - Mechatronics (24h)": "https://www.linkedin.com/jobs/search/?keywords=Mechatronics%20Engineer&location=Germany&f_TP=1&sortBy=DD",
    "LinkedIn - Simulation (24h)": "https://www.linkedin.com/jobs/search/?keywords=Simulation%20Engineer&location=Germany&f_TP=1&sortBy=DD",
    "Indeed": "https://de.indeed.com/jobs?q={query}&l=Germany&fromage=1",
    "StepStone": "https://www.stepstone.de/en/jobs/{query}/germany/",
    "Jobtensor": "https://jobtensor.com/Jobs?q={query}&l=germany"
}

def fetch_links(query, url_template, site_name):
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    url = url_template.format(query=query.replace(" ", "+"))
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            title = link.get_text(strip=True).lower()
            href = link["href"]
            if any(k in title for k in KEYWORDS) and "ausbildung" not in title:
                full_link = href if href.startswith("http") else f"https://{site_name.lower()}.de{href}"
                jobs.append((title.title(), site_name, full_link))
    except Exception:
        pass
    return jobs

def collect_jobs():
    results = []
    for term in SEARCH_TERMS:
        results += fetch_links(term, SEARCH_URLS["Indeed"], "Indeed")
        results += fetch_links(term, SEARCH_URLS["StepStone"], "StepStone")
        results += fetch_links(term, SEARCH_URLS["Jobtensor"], "Jobtensor")
    for label, link in SEARCH_URLS.items():
        if "LinkedIn" in label:
            results.append((label, "LinkedIn", link))
    return results

def format_html(jobs):
    date = datetime.now().strftime('%d %B %Y')
    if not jobs:
        return "<p><b>No matching jobs found today.</b></p>"
    html = f"<h3>🔍 Matched Jobs – {date}</h3><ul>"
    for title, site, link in jobs:
        html += f"<li><b>{title}</b> – <i>{site}</i><br><a href='{link}'>Apply Now</a></li><br>"
    html += "</ul><br><i>This is an automated message.</i>"
    return html

# Collect job matches
jobs = collect_jobs()
html_body = format_html(jobs)

# Prepare API call to Brevo
API_KEY = os.getenv("BREVO_API_KEY")
headers = {
    "accept": "application/json",
    "api-key": API_KEY,
    "content-type": "application/json"
}
payload = {
    "sender": {"name": "Jineel Gandhi", "email": "jineelgandhi426@gmail.com"},
    "to": [{"email": "jineelgandhi426@gmail.com"}],
    "subject": "🔔 Daily Germany Job Alerts – Profile Matched",
    "htmlContent": html_body
}

# Send email using Brevo API
try:
    response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
    if response.status_code == 201:
        print("✅ Email sent successfully via Brevo API.")
    else:
        print("❌ Failed to send email:", response.status_code, response.text)
except Exception as e:
    print("❌ Exception occurred:", str(e))
