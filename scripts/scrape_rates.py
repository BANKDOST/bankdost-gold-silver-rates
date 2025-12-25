import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz
import re

URL = "https://bullions.co.in"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
}

res = requests.get(URL, headers=headers, timeout=20)
if res.status_code != 200:
    print(f"Error: Failed to fetch page (status {res.status_code})")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    return re.sub(r"[^\d]", "", text) or "0"

gold_22k = "0"
gold_24k = "0"
silver_999 = "0"

# Scan all tables
tables = soup.find_all("table")
for table in tables:
    rows = table.find_all("tr")
    for tr in rows:
        cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cols) < 5:  # Need at least Name + 1g + ... + 1kg
            continue
        
        name = cols[0].lower()
        price_1g = extract_number(cols[1])      # 1 Gram column
        price_1kg = extract_number(cols[4])     # 1 Kilogram column (index 4)

        if "gold 22" in name or "22 karat" in name:
            gold_22k = price_1g
        elif "gold 24" in name or "24 karat" in name:
            gold_24k = price_1g
        elif "silver 999" in name or "999 fine" in name:
            silver_999 = price_1kg

# Fallback message if not found
if gold_24k == "0" or gold_22k == "0" or silver_999 == "0":
    print("Warning: Some rates not found. Site structure may have changed.")

ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": now.strftime("%I:%M %p IST"),
    "gold_22k_per_gram": f"₹{gold_22k}",
    "gold_24k_per_gram": f"₹{gold_24k}",
    "silver_999_per_kg": f"₹{silver_999}",
    "source": "bullions.co.in",
    "note": "Rates are indicative and may vary by city and jeweller."
}

with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Rates fetched successfully from bullions.co.in")
print(data)  # Optional: print to console for quick check
