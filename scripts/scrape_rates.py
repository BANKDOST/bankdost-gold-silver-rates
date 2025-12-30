import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import json
import re

# IBJA website
URL = "https://ibjarates.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
}

# Fetch the page
res = requests.get(URL, headers=headers, timeout=30)
if res.status_code != 200:
    print("Failed to fetch page")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    """Keep only digits"""
    return re.sub(r"[^\d]", "", text) or "0"

# Current date/time in IST
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
today_str = now.strftime("%d/%m/%Y")  # DD/MM/YYYY
current_time = now.strftime("%I:%M %p IST")

# Flexible regex for date (match 30/12/2025 or 30-12-2025)
today_regex = today_str.replace("/", "[-/]")

# Initialize rates
gold_24k_10g = gold_22k_10g = silver_999_kg = "0"

# Find today's date <p> element
date_tags = soup.find_all(string=re.compile(today_regex))
for date_tag in date_tags:
    parent = date_tag.find_parent()
    if parent:
        # Find the first table after today's date
        table = parent.find_next("table")
        if table:
            for tr in table.find_all("tr"):
                cols = [td.get_text(strip=True).replace("\u00a0", " ").lower() for td in tr.find_all(["td", "th"])]
                if len(cols) < 2:
                    continue
                purity = cols[0]

                am_rate = extract_number(cols[1])  # AM column

                if "gold" in purity and "999" in purity:
                    gold_24k_10g = am_rate
                elif "gold" in purity and ("916" in purity or "22k" in purity):
                    gold_22k_10g = am_rate
                elif "silver" in purity and "999" in purity:
                    silver_999_kg = am_rate
            break
    break

# Build JSON
data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": current_time,
    "gold_24k_per_10gram": f"₹{gold_24k_10g}",
    "gold_22k_per_10gram": f"₹{gold_22k_10g}",
    "silver_999_per_kg": f"₹{silver_999_kg}",
    "source": "ibjarates.com",
    "note": "Rates are IBJA AM benchmark (without taxes/making charges)."
}

# Save JSON
with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Success!")
print(json.dumps(data, indent=2))
