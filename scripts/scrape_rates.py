import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz
import re

URL = "https://ibjarates.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
}

res = requests.get(URL, headers=headers, timeout=30)
if res.status_code != 200:
    print("Failed to fetch page")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    return re.sub(r"[^\d]", "", text) or "0"

# Initialize
gold_24k_10g = "0"
gold_22k_10g = "0"
silver_999_kg = "0"

# Scrape AM rates
tables = soup.find_all("table")
for table in tables:
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True).lower() for td in tr.find_all(["td", "th"])]
        if not cols or len(cols) < 2:
            continue
        
        # Gold 24K / 999
        if "999" in cols[0] and "gold" in cols[0]:
            if "am" in cols:
                gold_24k_10g = extract_number(cols[1])
        
        # Gold 22K / 916
        elif "916" in cols[0] or "22k" in cols[0]:
            if "am" in cols:
                gold_22k_10g = extract_number(cols[1])
        
        # Silver 999 / 1kg
        elif "999" in cols[0] and "silver" in cols[0]:
            if "am" in cols:
                silver_999_kg = extract_number(cols[1])

# Current date/time
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

# JSON data
data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": now.strftime("%I:%M %p IST"),
    "gold_24k_per_10gram": f"₹{gold_24k_10g}",
    "gold_22k_per_10gram": f"₹{gold_22k_10g}",
    "silver_999_per_kg": f"₹{silver_999_kg}",
    "source": "ibjarates.com",
    "note": "Rates are IBJA AM benchmark (without taxes/making charges)."
}

with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Success!")
print(json.dumps(data, ensure_ascii=False, indent=2))
