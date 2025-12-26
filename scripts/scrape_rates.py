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
    return re.sub(r"[^\d]", "", text) or "0"

# Initialize
gold_24k_10g = "0"
gold_22k_10g = "0"
silver_999_kg = "0"

tables = soup.find_all("table")
print(f"Found {len(tables)} tables on the page.\n")  # Debug

for table_idx, table in enumerate(tables):
    print(f"--- Processing Table {table_idx + 1} ---")  # Debug
    rows = table.find_all("tr")
    for tr in rows:
        cols = [cell.get_text(strip=True) for cell in tr.find_all(["td", "th"])]
        if len(cols) < 6:
            continue
        
        name = cols[0]
        name_lower = name.lower()
        print(f"Row: {name} | 10g: {cols[2]} | 1kg: {cols[4]}")  # Debug - shows raw values
        
        if "gold" in name_lower:
            price_10g = extract_number(cols[2])
            if "24" in name_lower and ("karat" in name_lower or "carat" in name_lower):
                gold_24k_10g = price_10g
                print(f"--> Matched 24K Gold: ₹{price_10g}")
            elif "22" in name_lower and ("karat" in name_lower or "carat" in name_lower):
                gold_22k_10g = price_10g
                print(f"--> Matched 22K Gold: ₹{price_10g}")
        
        elif "silver" in name_lower and "999" in name_lower:
            price_1kg = extract_number(cols[4])
            silver_999_kg = price_1kg
            print(f"--> Matched Silver 999: ₹{price_1kg}")

print("\nFinal extracted values:")
print(f"24K 10g: ₹{gold_24k_10g}")
print(f"22K 10g: ₹{gold_22k_10g}")
print(f"Silver kg: ₹{silver_999_kg}")

if gold_24k_10g == "0" or gold_22k_10g == "0" or silver_999_kg == "0":
    print("ERROR: Missing some rates! Check debug output above.")

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

print("\nRates saved successfully!")
print(json.dumps(data, ensure_ascii=False, indent=2))
