import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

# IBJA rates page
URL = "https://ibjarates.com"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# ⚠ Adjust these selectors after inspecting the website
gold_22k_916 = soup.select_one("YOUR_SELECTOR_FOR_916").text.strip()
gold_24k_995 = soup.select_one("YOUR_SELECTOR_FOR_995").text.strip()
gold_24k_999 = soup.select_one("YOUR_SELECTOR_FOR_999").text.strip()
silver_999 = soup.select_one("YOUR_SELECTOR_FOR_SILVER").text.strip()

ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": "10:00 AM IST",
    "gold_24k_995": gold_24k_995,
    "gold_24k_999": gold_24k_999,
    "gold_22k_916": gold_22k_916,
    "silver_999": silver_999,
    "source": "IBJA Reference",
    "note": "Rates are indicative and may vary by city and jeweller."
}

# Save JSON
with open("gold_silver_rate.json", "w") as f:
    json.dump(data, f, indent=2)

