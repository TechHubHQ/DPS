import schedule
import time
import pytz
from database import clear_old_submissions
from datetime import datetime


def cleanup_task():
    clear_old_submissions()
    ist = pytz.timezone('Asia/Kolkata')
    ist_time = datetime.now(ist)
    print(f"Cleanup completed at {ist_time.strftime('%Y-%m-%d %H:%M:%S IST')}")


def is_first_day_of_month_ist():
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    return now_ist.day == 1


# Schedule cleanup daily at midnight IST, but only run on the first day of the month
schedule.every().day.at("00:00").do(
    lambda: cleanup_task() if is_first_day_of_month_ist() else None
)

if __name__ == "__main__":
    print("Monthly cleanup job started (IST timezone)...")
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour
