import schedule
import time
from main import main

is_running = False

def job():
    global is_running
    if is_running:
        print("⏳ Job đang chạy, bỏ qua")
        return
    is_running = True
    try:
        main()
    finally:
        is_running = False

schedule.every(1).hours.do(job)

print("⏱ Auto crawler running...")

try:
    while True:
        schedule.run_pending()
        time.sleep(10)
except KeyboardInterrupt:
    print("🛑 Stopped safely")