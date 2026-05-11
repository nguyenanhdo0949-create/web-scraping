import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "products.db")
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
CRAWL_INTERVAL_HOURS = int(os.getenv("CRAWL_INTERVAL_HOURS", 1))
