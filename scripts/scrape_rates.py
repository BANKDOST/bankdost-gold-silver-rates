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

def find_main_rate(label):
    """
    Finds the rate right below a main GOLD or SILVER header.
    """
    elem = soup.find(text=re.compile(label, re.IGNORECASE))
    if elem:
        # Look for next number-like sibling
        parent = elem.parent
        # Next siblings often contain the numeric text
        next_text = parent.find_next(string=re.compile(r"\d[\d,]*"))
        if next_text:
            return re.sub(r"[^\d]", "", next_text)
    return "0"

# Extract gold & silver
# Gold blocks likely show 10gm inside main view
gold24_10g = find_main_rate("GOLD")  # first gold
silver_1kg = find_main_rate("SILVER")

# Convert 10gm gold to per gram
gold24_per_gram = str(round(int(gold24_10g) / 10)) if gold24_10g != "0" else "0"

# Next, find 22K inside detail table
gold22_per_gram = "0"
table = soup.find("table")
if table:
    for tr in table.find_all("tr"):
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if not cols:
            continue
        if "Gold 22 Karat" in cols[0]:
            # find price under 1 Gram column
            # assume second column after label is the 1 Gram value
            if len(cols) > 1:
                gold22_per_gram = re.sub(r"[^\d]", "", cols[1])

# Final JSON
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": now.strftime("%I:%M %p IST"),
    "gold_24k_per_gram": f"₹{gold24_per_gram}",
    "gold_22k_per_gram": f"₹{gold22_per_gram}",
    "silver_999_per_kg": f"₹{silver_1kg}",
    "source": "bullions.co.in",
    "note": "Rates are indicative and may vary by city and jeweller."
}

with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated rates from Bullions!")
