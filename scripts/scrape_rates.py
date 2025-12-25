import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pytz

# URL of IBJA rates page
url = "https://ibjarates.com/"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

def extract_rate(label):
    try:
        td = soup.find("td", string=label)
        if td:
            return td.find_next_sibling("td").text.strip()
        return "0"
    except:
        return "0"

rates = {
    "date": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y"),
    "time": datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p IST"),
    "gold_22k_916": extract_rate("916 Purity"),
    "gold_24k_995": extract_rate("995 Purity"),
    "gold_24k_999": extract_rate("999 Purity"),  # optional, can remove if not used
    "silver_999": extract_rate("999 Silver"),
    "source": "IBJA Reference",
    "note": "Rates are indicative and may vary by city and jeweller."
}

# Save JSON
with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(rates, f, ensure_ascii=False, indent=2)
