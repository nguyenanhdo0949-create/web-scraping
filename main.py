from scraper.scraper import scrape_all
from database.db import create_db, insert_data

def main():
    print("🚀 Crawl multi-site...")
    data = scrape_all()
    print(f"✅ Tổng dữ liệu: {len(data)}")

    create_db()
    insert_data(data)

    print("💾 Đã lưu DB")

if __name__ == "__main__":
    main()