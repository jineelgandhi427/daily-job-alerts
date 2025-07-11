
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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

def write_to_file(jobs):
    date = datetime.now().strftime('%d %B %Y')
    with open("matched_jobs.txt", "w", encoding="utf-8") as f:
        f.write(f"🔍 Matched Jobs – {date}\n\n")
        if not jobs:
            f.write("No matching jobs found today.\n")
        else:
            for title, site, link in jobs:
                f.write(f"{title} – via {site}\n{link}\n\n")
    print("✅ Job list written to matched_jobs.txt")

if __name__ == "__main__":
    job_results = collect_jobs()
    write_to_file(job_results)
