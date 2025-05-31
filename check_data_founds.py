import requests
import sys

# Replace this with your actual Fly.io app URL
PRAYER_TIMES_ENDPOINT = "https://prayertime.fly.dev/prayer-times"

try:
    response = requests.get(PRAYER_TIMES_ENDPOINT, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            print("⚠️  Error in prayer times data:", data["error"])
            sys.exit(1)
        else:
            print("✅ Prayer times data found:", data)
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print("❌ Failed to connect or parse data:", e)
    sys.exit(1)
