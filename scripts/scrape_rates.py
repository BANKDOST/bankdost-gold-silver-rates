import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

URL = "https://ibjarates.com"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

def get_price(label):
    """Find the price for a given label on the page"""
    td = soup.find("td", string=label)
    if td and td.find_next_sibling("td"):
        return td.find_next_sibling("td").text.strip()
    else:
        print(f"Warning: {label} not found on the page.")
        return "0"

# Fetch prices
gold_22k_916 = get_price("916 Purity")
gold_24k_995 = get_price("995 Purity")
gold_24k_999 = get_price("999 Purity")
silver_999   = get_price("Silver 999")

# Convert per 10g / per kg to per gram safely
def per_gram(value, divisor):
    try:
        return str(round(int(value)/divisor))
    except:
        return "0"

gold_22k_916 = per_gram(gold_22k_916, 10)
gold_24k_995 = per_gram(gold_24k_995, 10)
gold_24k_999 = per_gram(gold_24k_999, 10)
silver_999   = per_gram(silver_999, 1000)

# IST time
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)

data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": "10:00 AM IST",
    "gold_22k_916": f"₹{gold_22k_916}",
    "gold_24k_995": f"₹{gold_24k_995}",
    "gold_24k_999": f"₹{gold_24k_999}",
    "silver_999": f"₹{silver_999}",
    "source": "IBJA Reference",
    "note": "Rates are indicative and may vary by city and jeweller."
}

# Save JSON
with open("gold_silver_rate.json", "w") as f:
    json.dump(data, f, indent=2)

print("Gold & Silver rates updated successfully!")
