import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz
import re

# IBJA rates URL
URL = "https://ibjarates.com/"

# Fetch page
response = requests.get(URL)
soup = BeautifulSoup(response.text, "html.parser")

def extract_rate(label):
    """
    Finds the rate number following a label like '916 Purity' or '995 Purity'.
    Returns string with ₹ symbol, or "0" if not found.
    """
    try:
        # Find element containing label text
        element = soup.find(string=re.compile(label))
        if element:
            # Look for next number in the siblings (could be text or span)
            parent_text = element.parent.get_text(separator=" ", strip=True)
            # Extract first number with optional commas
            match = re.search(r"[\d,]+", parent_text)
            if match:
                rate = match.group(0).replace(",", "")
                return f"\u20b9{rate}"
        return "0"
    except Exception:
        return "0"

# Build JSON
rates = {
    "date": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y"),
    "time": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p IST"),
    "gold_22k_916": extract_rate("916 Purity"),
    "gold_24k_995": extract_rate("995 Purity"),
    "gold_24k_999": extract_rate("999 Purity"),  # optional, remove if not needed
    "silver_999": extract_rate("Silver 999"),
    "source": "IBJA Reference",
    "note": "Rates are indicative and may vary by city and jeweller."
}

# Save JSON
with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(rates, f, ensure_ascii=False, indent=2)

print("Rates updated successfully!")
