import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz

URL = "https://ibjarates.com"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# --------------------------
# Replace these selectors with actual HTML content of ibjarates.com
# The site usually has a table with <td>Purity</td> and <td>Price</td>
# --------------------------
gold_22k_916 = soup.find("td", text="916 Purity").find_next_sibling("td").text.strip()
gold_24k_995 = soup.find("td", text="995 Purity").find_next_sibling("td").text.strip()
gold_24k_999 = soup.find("td", text="999 Purity").find_next_sibling("td").text.strip()
silver_999   = soup.find("td", text="Silver 999").find_next_sibling("td").text.strip()

# Convert per 10g / per kg to per gram
gold_22k_916 = str(round(int(gold_22k_916)/10))
gold_24k_995 = str(round(int(gold_24k_995)/10))
gold_24k_999 = str(round(int(gold_24k_999)/10))
silver_999   = str(round(int(silver_999)/1000))

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
