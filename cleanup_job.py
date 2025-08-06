import schedule
import time
from database import clear_old_submissions

def cleanup_task():
    clear_old_submissions()
    print(f"Cleanup completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Schedule cleanup every 2 days at midnight
schedule.every(2).days.at("00:00").do(cleanup_task)

if __name__ == "__main__":
    print("Cleanup job started...")
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour