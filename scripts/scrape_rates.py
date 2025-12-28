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
    print("Failed to fetch page")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    return re.sub(r"[^\d]", "", text) or "0"

gold_24k_10g = "0"
gold_22k_10g = "0"
silver_999_kg = "0"

tables = soup.find_all("table")
print(f"Found {len(tables)} tables\n")

for table_idx, table in enumerate(tables):
    print(f"--- Table {table_idx + 1} ---")
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cols) < 6:
            continue
        
        row_name_lower = cols[0].lower()
        print(f"Row original: '{cols[0]}'")
        print(f"Row lowered: '{row_name_lower}'")
        print(f"10g raw: '{cols[2]}' -> extracted: {extract_number(cols[2])}")
        print(f"1kg raw: '{cols[4]}' -> extracted: {extract_number(cols[4])}")
        print("---")
               if "24" in row_name_lower and "karat" in row_name_lower:
            gold_24k_10g = extract_number(cols[2])
            print(">>> 24K MATCHED!")
        elif "22 karat" in row_name_lower:
            gold_22k_10g = extract_number(cols[2])
            print(">>> 22K MATCHED!")
        elif "999 fine" in row_name_lower:
            silver_999_kg = extract_number(cols[4])
            print(">>> SILVER MATCHED!")

print(f"\nFinal extracted: 24K={gold_24k_10g}, 22K={gold_22k_10g}, Silver={silver_999_kg}")

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

print("Success!")
print(json.dumps(data, ensure_ascii=False, indent=2))
