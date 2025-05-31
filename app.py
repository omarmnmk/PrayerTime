# from flask import Flask, jsonify
# from apscheduler.schedulers.background import BackgroundScheduler
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime, timedelta
# import os


# app = Flask(__name__)

# ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
# ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
# PRAYER_TIMES_URL = "https://www.menatrust.org.uk/salahtimes/"

# # Global variable to hold today's prayer times in memory
# prayer_times_data = {}

# def scrape_prayer_times():
#     print("Scraping prayer times now...")
#     response = requests.get(PRAYER_TIMES_URL)
#     print(f"Response status: {response.status_code}")
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         table = soup.find("table", class_="dptTimetable dptNoBorder customStyles dptUserStyles")
#         if table:
#             prayer_times = {}
#             rows = table.find_all("tr")
#             for row in rows:
#                 prayer_name = row.find("th", class_="prayerName")
#                 if prayer_name:
#                     prayer = prayer_name.text.strip()
#                     if prayer.lower() == "sunrise":
#                         azan = row.find_all("td")[0].text.strip()
#                         iqama = "-"
#                     else:
#                         cols = row.find_all("td")
#                         if len(cols) == 2:
#                             azan = cols[0].text.strip()
#                             iqama = cols[1].text.strip()
#                         else:
#                             azan, iqama = "-", "-"
#                     prayer_times[prayer] = {"azan": azan, "iqama": iqama}
#             print("Prayer times data:", prayer_times)
#             return prayer_times
#     print("Failed to scrape prayer times.")
#     return {}

# def send_notification(prayer, iqama_time):
#     url = "https://onesignal.com/api/v1/notifications"
#     payload = {
#         "app_id": ONESIGNAL_APP_ID,
#         "included_segments": ["All"],
#         "headings": {"en": "Prayer Reminder"},
#         "contents": {"en": f"It’s time for {prayer} prayer (Iqama at {iqama_time})."},
#         "url": "https://omarmnmk.github.io/PrayerTime/"  # change to your real site URL!
#     }
#     headers = {
#         "Content-Type": "application/json; charset=utf-8",
#         "Authorization": f"Basic {ONESIGNAL_API_KEY}"
#     }
#     response = requests.post(url, headers=headers, json=payload)
#     if response.status_code == 200:
#         print(f"Notification sent for {prayer} prayer!")
#     else:
#         print(f"Failed to send notification for {prayer}. Status: {response.status_code}")


# def schedule_prayer_notifications(prayer_times):
#     scheduler = BackgroundScheduler(timezone="UTC")
#     today = datetime.utcnow().date()
    
#     for prayer, times in prayer_times.items():
#         # Azan time
#         azan_time = times["azan"]
#         if azan_time and azan_time != "-":
#             hour, minute = map(int, azan_time.split(":"))
#             azan_datetime = datetime(today.year, today.month, today.day, hour, minute) - timedelta(minutes=5)
#             if azan_datetime > datetime.utcnow():
#                 scheduler.add_job(send_notification, 'date', run_date=azan_datetime,
#                                   args=[f"{prayer} Azan", azan_time])
#                 print(f"Scheduled {prayer} Azan notification at {azan_datetime} UTC")
        
#         # Iqama time
#         iqama_time = times["iqama"]
#         if iqama_time and iqama_time != "-":
#             hour, minute = map(int, iqama_time.split(":"))
#             iqama_datetime = datetime(today.year, today.month, today.day, hour, minute) - timedelta(minutes=5)
#             if iqama_datetime > datetime.utcnow():
#                 scheduler.add_job(send_notification, 'date', run_date=iqama_datetime,
#                                   args=[f"{prayer} Iqama", iqama_time])
#                 print(f"Scheduled {prayer} Iqama notification at {iqama_datetime} UTC")
    
#     scheduler.start()


# @app.route("/")
# def home():
#     return "Prayer Notification Server Running!"

# @app.route("/prayer-times")
# def get_prayer_times():
#     if prayer_times_data:
#         return jsonify(prayer_times_data)
#     else:
#         return jsonify({"error": "Prayer times not found"}), 404

# if __name__ == "__main__":
#     print("Starting prayer notification server...")
#     prayer_times_data = scrape_prayer_times()
#     if prayer_times_data:
#         schedule_prayer_notifications(prayer_times_data)
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))


from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import threading

app = Flask(__name__)

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")
PRAYER_TIMES_URL = "https://www.menatrust.org.uk/salahtimes/"

prayer_times_data = {}

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
            print("Prayer times data:", prayer_times)
            return prayer_times
    print("Failed to scrape prayer times.")
    return {}

def send_notification(prayer, time):
    url = "https://onesignal.com/api/v1/notifications"
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "included_segments": ["All"],
        "headings": {"en": "Prayer Reminder"},
        "contents": {"en": f"It’s time for {prayer} prayer (at {time})."},
        "url": "https://omarmnmk.github.io/PrayerTime/"
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
        # Azan time
        azan_time = times["azan"]
        if azan_time and azan_time != "-":
            hour, minute = map(int, azan_time.split(":"))
            azan_datetime = datetime(today.year, today.month, today.day, hour, minute) - timedelta(minutes=5)
            if azan_datetime > datetime.utcnow():
                scheduler.add_job(send_notification, 'date', run_date=azan_datetime,
                                  args=[f"{prayer} Azan", azan_time])
                print(f"Scheduled {prayer} Azan notification at {azan_datetime} UTC")
        
        # Iqama time
        iqama_time = times["iqama"]
        if iqama_time and iqama_time != "-":
            hour, minute = map(int, iqama_time.split(":"))
            iqama_datetime = datetime(today.year, today.month, today.day, hour, minute) - timedelta(minutes=5)
            if iqama_datetime > datetime.utcnow():
                scheduler.add_job(send_notification, 'date', run_date=iqama_datetime,
                                  args=[f"{prayer} Iqama", iqama_time])
                print(f"Scheduled {prayer} Iqama notification at {iqama_datetime} UTC")
    
    scheduler.start()

def background_setup():
    global prayer_times_data
    prayer_times_data = scrape_prayer_times()
    if prayer_times_data:
        schedule_prayer_notifications(prayer_times_data)

@app.route("/")
def home():
    return "Prayer Notification Server Running!"

@app.route("/prayer-times")
def get_prayer_times():
    if prayer_times_data:
        return jsonify(prayer_times_data)
    else:
        return jsonify({"error": "Prayer times not found"}), 404

if __name__ == "__main__":
    print("Starting prayer notification server...")

    # Start the scraping and scheduler in a separate thread
    threading.Thread(target=background_setup, daemon=True).start()

    # Start the Flask server
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
