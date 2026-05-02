import schedule
import time
from main import main

schedule.every(1).hours.do(main)

print("⏱ Auto crawler running...")

while True:
    schedule.run_pending()
    time.sleep(10)