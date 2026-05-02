from scraper.scraper import scrape_all
from database.db import create_db, insert_data

def main():
    print("🚀 Crawling...")
    data = scrape_all()

    create_db()
    insert_data(data)

    print(f"✅ Done: {len(data)} records")

if __name__ == "__main__":
    main()