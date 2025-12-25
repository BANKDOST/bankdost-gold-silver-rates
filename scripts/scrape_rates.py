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

# Fetch the page
res = requests.get(URL, headers=headers, timeout=30)
if res.status_code != 200:
    print(f"Error: Failed to fetch page (status {res.status_code})")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    """Remove all non-digits (handles commas, ₹, etc.)"""
    return re.sub(r"[^\d]", "", text) or "0"

# Initialize variables
gold_24k_10g = "0"
gold_22k_10g = "0"
silver_999_kg = "0"

# Find all tables
tables = soup.find_all("table")

for table in tables:
    rows = table.find_all("tr")
    for tr in rows:
        cols = [cell.get_text(strip=True) for cell in tr.find_all(["td", "th"])]
        
        # Skip header or incomplete rows
        if len(cols) < 6:  # We need up to 1 Tola column (index 5)
            continue
        
        name = cols[0].lower()
        price_10g = extract_number(cols[2])   # 10 Gram column (index 2)
        price_1kg = extract_number(cols[4])   # 1 Kilogram column (index 4)

        # Match Gold 24 Karat
        if "24 karat" in name or "24karat" in name:
            gold_24k_10g = price_10g
        
        # Match Gold 22 Karat
        elif "22 karat" in name or "22karat" in name:
            gold_22k_10g = price_10g
        
        # Match Silver 999 Fine
        elif "silver 999" in name or "999 fine" in name:
            silver_999_kg = price_1kg

# Warning if any value not found
if gold_24k_10g == "0" or gold_22k_10g == "0" or silver_999_kg == "0":
    print("Warning: Some rates not found. The site layout may have changed.")
    print(f"Found: 24K={gold_24k_10g}, 22K={gold_22k_10g}, Silver={silver_999_kg}")

# Get current IST time
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

# Prepare JSON data
data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": now.strftime("%I:%M %p IST"),
    "gold_24k_per_10gram": f"₹{gold_24k_10g}",
    "gold_22k_per_10gram": f"₹{gold_22k_10g}",
    "silver_999_per_kg": f"₹{silver_999_kg}",
    "source": "bullions.co.in",
    "note": "Rates are indicative bullion rates (without taxes/making charges). May vary by city and jeweller."
}

# Save to JSON file
with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Print success and current values
print("Rates fetched successfully from bullions.co.in")
print(json.dumps(data, ensure_ascii=False, indent=2))
