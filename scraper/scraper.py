import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_prayer_times():
    url = "https://www.menatrust.org.uk/salahtimes/"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="dptTimetable dptNoBorder customStyles dptUserStyles")
        if table:
            prayer_times = {}

            rows = table.find_all("tr")
            for row in rows:
                prayer_name = row.find("th", class_="prayerName")
                if prayer_name:
                    prayer = prayer_name.text.strip()
                    if prayer.lower() == "sunrise":
                        azan = row.find_all("td")[0].text.strip()
                        iqama = "-"
                    else:
                        cols = row.find_all("td")
                        if len(cols) == 2:
                            azan = cols[0].text.strip()
                            iqama = cols[1].text.strip()
                        else:
                            azan, iqama = "-", "-"
                    prayer_times[prayer] = {"azan": azan, "iqama": iqama}

            # Save today's prayer times to a JSON file
            with open("today_prayer_times.json", "w") as f:
                json.dump(prayer_times, f, indent=2)

            print(f"[{datetime.now()}] Prayer times updated!")
        else:
            print("Prayer times table not found.")
    else:
        print(f"Failed to fetch page. Status: {response.status_code}")

if __name__ == "__main__":
    scrape_prayer_times()
