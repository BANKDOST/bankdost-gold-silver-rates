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

res = requests.get(URL, headers=headers, timeout=30)
if res.status_code != 200:
    print(f"Error: Failed to fetch page (status {res.status_code})")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    cleaned = re.sub(r"[^\d]", "", text)
    return cleaned if cleaned else "0"

gold_24k_10g = "0"
gold_22k_10g = "0"
silver_999_kg = "0"

tables = soup.find_all("table")

for table in tables:
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cols) < 6:
            continue
        
        row_name = cols[0].lower()
        
        # Exact matching based on site's row names
        if "gold 24 karat" in row_name:
            gold_24k_10g = extract_number(cols[2])  # 10 Gram column
        elif "gold 22 karat" in row_name:
            gold_22k_10g = extract_number(cols[2])  # 10 Gram column
        elif "silver 999 fine" in row_name:
            silver_999_kg = extract_number(cols[4])  # 1 Kilogram column

# Safety check
if "0" in (gold_24k_10g, gold_22k_10g, silver_999_kg):
    print("Warning: Failed to extract one or more rates. Site may have changed.")

ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": now.strftime("%I:%M %p IST"),
    "gold_24k_per_10gram": f"₹{gold_24k_10g}",
    "gold_22k_per_10gram": f"₹{gold_22k_10g}",
    "silver_999_per_kg": f"₹{silver_999_kg}",
    "source": "bullions.co.in",
    "note": "Rates are indicative bullion rates (without taxes/making charges). May vary by city and jeweller."
}

with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Rates fetched successfully!")
print(json.dumps(data, ensure_ascii=False, indent=2))
