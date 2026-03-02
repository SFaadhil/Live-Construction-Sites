import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

URL = "https://rera.tn.gov.in/registered-building/tn"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_csrf_token(session):
    response = session.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "lxml")

    token_input = soup.find("input", {"name": "_token"})
    if token_input:
        return token_input.get("value")
    return None


def scrape_year(session, year):
    print(f"Scraping year {year}...")

    token = get_csrf_token(session)
    if not token:
        print("CSRF token not found.")
        return []

    payload = {
        "_token": token,
        "year": year
    }

    response = session.post(URL, headers=HEADERS, data=payload)
    soup = BeautifulSoup(response.text, "lxml")

    table = soup.find("table")
    if not table:
        print(f"No table found for {year}")
        return []

    rows = table.find_all("tr")[1:]
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 8:
            continue

        links = cols[6].find_all("a")
        hyperlink_list = [a["href"] for a in links] if links else ["None"]

        data.append({
            "Year": year,
            "S. No": cols[0].get_text(strip=True),
            "Project Registration No.": cols[1].get_text(" ", strip=True),
            "Name & Address of Promoter": cols[2].get_text(" ", strip=True),
            "Project Details & Address": cols[3].get_text(" ", strip=True),
            "Approval Details": cols[4].get_text(" ", strip=True),
            "Project Completion Date": cols[5].get_text(strip=True),
            "Other Details Links": ", ".join(hyperlink_list),
            "Current Status of Project": cols[7].get_text(" ", strip=True)
        })

    return data


if __name__ == "__main__":
    session = requests.Session()
    session.headers.update(HEADERS)

    all_data = []

    for year in range(2023, 2026):   # adjust years as needed
        year_data = scrape_year(session, year)
        all_data.extend(year_data)
        time.sleep(1)  # polite delay

    df = pd.DataFrame(all_data)

    save_path = "tnrera_all_years.csv"
    df.to_csv(save_path, index=False)

    print(f"\nSaved {len(df)} total records to:")
    print(save_path)