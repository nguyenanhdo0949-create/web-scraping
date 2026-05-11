import schedule
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

is_running = False

def job():
    global is_running
    if is_running:
        print("[auto_run] Job is already running, skipping...")
        return
    is_running = True
    print(f"\n[auto_run] Starting scheduled job at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        main()
    except Exception as e:
        print(f"[auto_run] ERROR: {e}")
    finally:
        is_running = False
        print(f"[auto_run] Job finished at {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Run immediately on start, then every 1 hour
print(f"[auto_run] Scheduler started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("[auto_run] Running initial crawl...")
job()

schedule.every(1).hours.do(job)
print("[auto_run] Next crawl in 1 hour. Press Ctrl+C to stop.")

try:
    while True:
        schedule.run_pending()
        time.sleep(10)
except KeyboardInterrupt:
    print("\n[auto_run] Stopped safely.")