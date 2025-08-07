import schedule
import time
from database import clear_old_submissions
import pytz
from datetime import datetime

def cleanup_task():
    clear_old_submissions()
    ist = pytz.timezone('Asia/Kolkata')
    ist_time = datetime.now(ist)
    print(f"Cleanup completed at {ist_time.strftime('%Y-%m-%d %H:%M:%S IST')}")

# Schedule cleanup daily at midnight IST
schedule.every().day.at("00:00").do(cleanup_task)

if __name__ == "__main__":
    print("Cleanup job started (IST timezone)...")
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour