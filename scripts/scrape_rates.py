import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz
import re

URL = "https://bullions.co.in"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=20)
soup = BeautifulSoup(response.text, "html.parser")

def clean_price(text):
    # Remove ₹, commas, spaces
    return re.sub(r"[^\d.]", "", text)

gold_22k = "0"
gold_24k = "0"
silver_999 = "0"

# Find all table rows
for row in soup.find_all("tr"):
    cols = [c.get_text(strip=True) for c in row.find_all("td")]
    if not cols:
        continue

    row_text = " ".join(cols).lower()

    # Gold 22K per gram
    if "gold 22" in row_text and "gram" in row_text:
        gold_22k = clean_price(cols[-1])

    # Gold 24K per gram
    if "gold 24" in row_text and "gram" in row_text:
        gold_24k = clean_price(cols[-1])

    # Silver 999 per kg
    if "silver" in row_text and "kg" in row_text:
        silver_999 = clean_price(cols[-1])

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

print("Bullions rates updated successfully")
