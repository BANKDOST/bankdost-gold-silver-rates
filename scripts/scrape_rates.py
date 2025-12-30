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
    print(f"Failed to fetch page: {res.status_code}")
    exit()

soup = BeautifulSoup(res.text, "html.parser")

def extract_number(text):
    """Keep only digits from text"""
    return re.sub(r"[^\d]", "", text) or "0"

# Current date/time in IST
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist)
today_str = now.strftime("%d/%m/%Y")  # e.g., 31/12/2025
current_time = now.strftime("%I:%M %p IST")

# Flexible regex for today's date (handles / or -)
today_regex = re.escape(today_str).replace("\\/", "[-/]")

# Initialize rates
gold_24k_10g = gold_22k_10g = silver_999_kg = "0"
displayed_date = "Unknown"
rate_source = "latest available"

# Try to find today's date and extract rates from the following table
date_tags = soup.find_all(string=re.compile(today_regex, re.IGNORECASE))
if date_tags:
    date_tag = date_tags[0]
    displayed_date = date_tag.strip()
    parent = date_tag.find_parent()
    if parent:
        table = parent.find_next("table")
        if table:
            rate_source = f"{displayed_date} AM benchmark"
            for tr in table.find_all("tr"):
                cols = [td.get_text(strip=True).replace("\u00a0", " ").lower() for td in tr.find_all(["td", "th"])]
                if len(cols) < 3:
                    continue
                purity = cols[0]
                am_rate = extract_number(cols[1])
                if "gold" in purity and "999" in purity and am_rate != "0":
                    gold_24k_10g = am_rate
                elif "gold" in purity and ("916" in purity or "22k" in purity or "22ct" in purity) and am_rate != "0":
                    gold_22k_10g = am_rate
                elif "silver" in purity and "999" in purity and am_rate != "0":
                    silver_999_kg = am_rate

# Fallback: if today's rates not found, use the first main rates table (latest available)
if gold_24k_10g == "0":
    print("Today's rates not available. Falling back to latest displayed rates.")
    main_table = soup.find("table")  # The first table is usually the current/latest rates
    if main_table:
        displayed_date_tag = main_table.find_previous(string=re.compile(r"\d{2}[/-]\d{2}[/-]\d{4}"))
        if displayed_date_tag:
            displayed_date = displayed_date_tag.strip()
        rate_source = f"{displayed_date} AM benchmark (latest available)"
        for tr in main_table.find_all("tr"):
            cols = [td.get_text(strip=True).replace("\u00a0", " ").lower() for td in tr.find_all(["td", "th"])]
            if len(cols) < 3:
                continue
            purity = cols[0]
            am_rate = extract_number(cols[1])
            pm_rate = extract_number(cols[2] if len(cols) > 2 else "0")
            # Prefer AM, fallback to PM if AM is zero/empty
            rate = am_rate if am_rate != "0" else pm_rate
            if rate == "0":
                continue
            if "gold" in purity and "999" in purity:
                gold_24k_10g = rate
            elif "gold" in purity and ("916" in purity or "22k" in purity or "22ct" in purity):
                gold_22k_10g = rate
            elif "silver" in purity and "999" in purity:
                silver_999_kg = rate

# Build JSON
data = {
    "date": now.strftime("%d-%m-%Y"),
    "time": current_time,
    "displayed_rate_date": displayed_date,
    "gold_24k_per_10gram": f"₹{gold_24k_10g}",
    "gold_22k_per_10gram": f"₹{gold_22k_10g}",
    "silver_999_per_kg": f"₹{silver_999_kg}",
    "source": "ibjarates.com",
    "note": f"Rates are IBJA {rate_source} (without taxes/making charges)."
}

# Save JSON
with open("gold_silver_rate.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Success!")
print(json.dumps(data, indent=2, ensure_ascii=False))
