import json
import os
import requests
from bs4 import BeautifulSoup
from google import genai

# Initialize Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

TARGET_SITES = [
    {"name": "Business Recorder", "url": "https://www.brecorder.com/business-finance"},
    {"name": "Dawn Business", "url": "https://www.dawn.com/business"},
    {"name": "State Bank of Pakistan", "url": "https://www.sbp.org.pk/"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def scrape_site_text(url):
    try:
        res = requests.get(url, headers=headers, timeout=12)
        soup = BeautifulSoup(res.text, "html.parser")
        # Extract main body text and headlines
        paragraphs = soup.find_all(['p', 'h2', 'h3'])
        text_data = " ".join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 30])
        return text_data[:6000] # Cap text length for fast API processing
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

summaries = []

for site in TARGET_SITES:
    raw_text = scrape_site_text(site["url"])
    if raw_text:
        prompt = (
            f"You are a senior financial analyst. Summarize the key business, macroeconomic, or policy developments "
            f"from the following text scraped from {site['name']} into 3 concise bullet points:\n\n{raw_text}"
        )
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            summaries.append({
                "source": site["name"],
                "url": site["url"],
                "summary": response.text
            })
        except Exception as e:
            print(f"AI Generation error for {site['name']}: {e}")

# Write to JSON file
with open("news_data.json", "w", encoding="utf-8") as f:
    json.dump(summaries, f, indent=4)

print("Daily news update completed successfully.")
