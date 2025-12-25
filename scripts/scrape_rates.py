import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz
import re

URL = "https://bullions.co.in"
headers = {"User-Agent": "Mozilla/5.0"}

res = requests.get(URL, headers=headers, timeout=20)
soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    return re.sub(r"[^\d]", "", text)

gold_22k = "0"
gold_24k = "0"
silver_999 = "0"

# Scan ALL tables
tables = soup.find_all("table")

for table in tables:
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cols) < 2:
            continue

        name = cols[0].lower()

        # Price is ALWAYS the LAST column on bullions.co.in
        price = extract_number(cols[-1])

        if "gold 22" in name:
            gold_22k = price

        elif "gold 24" in name:
            gold_24k = price

        elif "silver 999" in name:
            silver_999 = price

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
