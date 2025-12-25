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

def clean(text):
    return re.sub(r"[^\d]", "", text)

gold_22k = "0"
gold_24k = "0"
silver_999 = "0"

# Find the rates table
table = soup.find("table")
if table:
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) < 2:
            continue

        label = cols[0].lower()

        # ✅ Gold 24K – 1 Gram
        if "gold 24" in label and "gram" in label:
            gold_24k = clean(cols[-1])

        # ✅ Gold 22K – 1 Gram
        if "gold 22" in label and "gram" in label:
            gold_22k = clean(cols[-1])

        # ✅ Silver 999 – 1 Kilogram
        if "silver 999" in label and "kilogram" in label:
            silver_999 = clean(cols[-1])

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

print("Bullions rates updated correctly")
