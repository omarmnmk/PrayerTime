import json
import requests
from datetime import datetime

# Load the prayer times from JSON
with open("today_prayer_times.json") as f:
    prayer_times = json.load(f)

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

# Example: Send a notification for Fajr
prayer_name = "Fajr"
fajr_time = prayer_times[prayer_name]["iqama"]

# Customize the message
message = f"It’s time for {prayer_name} prayer (Iqama at {fajr_time})."

# OneSignal API endpoint
url = "https://onesignal.com/api/v1/notifications"

# Notification payload
payload = {
    "app_id": ONESIGNAL_APP_ID,
    "included_segments": ["All"],  # You can target specific users here
    "headings": {"en": "Prayer Reminder"},
    "contents": {"en": message},
    "url": "https://your-github-pages-site",  # Optional: link to your site
}

# Send the notification
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": f"Basic {ONESIGNAL_API_KEY}",
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    print(f"Notification sent successfully for {prayer_name} prayer!")
else:
    print(f"Failed to send notification. Status: {response.status_code}")
    print(response.text)
