from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup

from flask import jsonify



app = Flask(__name__)

# OneSignal credentials (from Railway or Fly.io environment variables)
ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
PRAYER_TIMES_URL = "https://www.menatrust.org.uk/salahtimes/"

def scrape_prayer_times():
    print("Scraping prayer times now...")
    response = requests.get(PRAYER_TIMES_URL)
    print(f"Response status: {response.status_code}")
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
            print("Prayer times scraped and updated.")
            print("Prayer times data:", prayer_times)
            return prayer_times
    print("Failed to scrape prayer times.")
    return {}

def send_notification(prayer, iqama_time):
    url = "https://onesignal.com/api/v1/notifications"
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],
        "headings": {"en": "Prayer Reminder"},
        "contents": {"en": f"It’s time for {prayer} prayer (Iqama at {iqama_time})."},
        "url": "https://your-github-pages-site"  # Change to your site URL!
    }
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Notification sent for {prayer} prayer!")
    else:
        print(f"Failed to send notification for {prayer}. Status: {response.status_code}")

def schedule_prayer_notifications(prayer_times):
    scheduler = BackgroundScheduler(timezone="UTC")
    today = datetime.utcnow().date()
    for prayer, times in prayer_times.items():
        iqama_time = times["iqama"]
        if iqama_time != "-" and iqama_time:
            hour, minute = map(int, iqama_time.split(":"))
            prayer_datetime = datetime(today.year, today.month, today.day, hour, minute) - timedelta(minutes=5)
            if prayer_datetime > datetime.utcnow():
                scheduler.add_job(send_notification, 'date', run_date=prayer_datetime,
                                  args=[prayer, iqama_time])
                print(f"Scheduled {prayer} notification at {prayer_datetime} UTC")
    scheduler.start()

@app.route("/")
def home():
    return "Prayer Notification Server Running!"

@app.route("/prayer-times")
def get_prayer_times():
    try:
        with open("today_prayer_times.json") as f:
            data = json.load(f)
            print("File data:", data)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Prayer times not found"}), 404

if __name__ == "__main__":
    print("Starting prayer notification server...")
    prayer_times = scrape_prayer_times()
    if prayer_times:
        schedule_prayer_notifications(prayer_times)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
