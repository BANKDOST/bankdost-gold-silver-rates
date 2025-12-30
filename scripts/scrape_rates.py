import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import json
import re

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

# Get today's date in IST
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
today_str = now.strftime("%d-%m-%Y")
current_time = now.strftime("%I:%M %p IST")

# Initialize
gold_24k_10g = gold_22k_10g = silver_999_kg = "0"

# Locate the section below today's date
date_tags = soup.find_all(text=re.compile(today_str))
for date_tag in date_tags:
    parent = date_tag.find_parent()
    if parent:
        # Find next siblings containing metal rates
        siblings = parent.find_next_siblings()
        for sib in siblings:
            text = sib.get_text(separator=" ").lower()
            
            if "gold" in text and "999" in text and gold_24k_10g == "0":
                gold_24k_10g = extract_number(text)
            elif "gold" in text and ("916" in text or "22k" in text) and gold_22k_10g == "0":
                gold_22k_10g = extract_number(text)
            elif "silver" in text and "999" in text and silver_999_kg == "0":
                silver_999_kg = extract_number(text)
            
            # Break when all values found
            if gold_24k_10g != "0" and gold_22k_10g != "0" and silver_999_kg != "0":
                break
        break  # Stop after first date section

# Create JSON
data = {
    "date": today_str,
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
print(json.dumps(data, ensure_ascii=False, indent=2))
