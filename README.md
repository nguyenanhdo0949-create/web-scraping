# Web Scraping & Automation Nâng Cao

> **Đồ án:** Crawl dữ liệu thông minh vượt anti-bot bằng Playwright + Stealth  
> **Công nghệ chính:** Playwright · Selenium · Scrapy · Flask · SQLite

---

## Kiến trúc dự án

```
web-scraping-project/
├── app.py                          # Flask web dashboard (API + UI)
├── main.py                         # Entry point: chạy toàn bộ pipeline
├── config.py                       # Cấu hình đường dẫn, biến môi trường
├── logger.py                       # Logging thống nhất (console + file)
├── auto_run.py                     # Scheduler tự động crawl mỗi 1 giờ
├── requirements.txt
├── database/
│   └── db.py                       # SQLite: create, insert, query, stats
├── scraper/
│   ├── scraper.py                  # Playwright scraper (books.toscrape.com)
│   ├── selenium_scraper.py         # Selenium scraper (quotes JS-rendered)
│   └── scrapy_crawler/
│       └── quotes_crawler/
│           ├── spiders/
│           │   └── quotes_spider.py   # Scrapy spider (quotes static HTML)
│           ├── pipelines.py           # JSON + SQLite pipeline
│           ├── middlewares.py         # Random User-Agent middleware
│           └── settings.py
├── templates/
│   └── index.html                  # Dashboard UI (dark mode, responsive)
└── data/                           # Output JSON/CSV files
```

---

## Cài đặt môi trường

### Bước 1: Tạo virtual environment
```bash
python -m venv venv
```

### Bước 2: Kích hoạt venv
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 3: Cài dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cài Playwright browsers
```bash
playwright install chromium
```

---

## Cách chạy

### ▶ Cách 1: Chạy toàn bộ pipeline (3 scrapers)
```bash
python main.py
```
Pipeline sẽ lần lượt:
1. **Playwright** → crawl `books.toscrape.com` (1000 sách, toàn bộ phân trang, anti-bot stealth)
2. **Selenium** → crawl `quotes.toscrape.com/js/` (JS-rendered content)
3. **Scrapy** → crawl `quotes.toscrape.com` (static HTML, concurrent requests)

### ▶ Cách 2: Chạy Dashboard web
```bash
python app.py
```
Mở trình duyệt: **http://localhost:5000**

Từ dashboard có thể:
- Xem toàn bộ dữ liệu với phân trang
- Tìm kiếm, lọc theo loại dữ liệu và công cụ scraping
- Nhấn **"Chạy Scraper"** để kích hoạt pipeline ngay trên UI
- Xuất **CSV** hoặc xem **JSON API**

### ▶ Cách 3: Chạy tự động theo lịch (mỗi 1 giờ)
```bash
python auto_run.py
```

### ▶ Cách 4: Chạy từng scraper riêng lẻ
```bash
# Playwright only
python scraper/scraper.py

# Selenium only
python scraper/selenium_scraper.py

# Scrapy only
cd scraper/scrapy_crawler
scrapy crawl quotes_spider
```

---

## API Endpoints

| Endpoint | Method | Mô tả |
|---|---|---|
| `GET /` | GET | Dashboard chính |
| `GET /api/data` | GET | Lấy dữ liệu dạng JSON (hỗ trợ filter) |
| `GET /api/stats` | GET | Thống kê tổng quan |
| `POST /api/run-scraper` | POST | Kích hoạt pipeline trong background |
| `GET /api/scraper-status` | GET | Trạng thái + log scraper đang chạy |
| `GET /export/csv` | GET | Xuất CSV (hỗ trợ filter) |
| `GET /export/json` | GET | Xuất JSON (hỗ trợ filter) |

### Query params cho `/api/data`, `/export/csv`, `/export/json`:
- `keyword` — tìm kiếm text
- `data_type` — `books` hoặc `quotes`
- `scraped_by` — `playwright`, `selenium`, hoặc `scrapy`
- `page` — số trang (mặc định 1)

---

## Công nghệ & Tính năng nổi bật

### Anti-bot / Stealth
- **Playwright**: inject stealth JS (ẩn `navigator.webdriver`, giả `plugins`, `languages`, `chrome.runtime`)
- **Selenium**: CDP command ẩn automation flag, custom User-Agent
- **Scrapy**: Random User-Agent middleware, randomized download delay
- Tất cả: giả lập hành vi người dùng (random delay, mouse movement)

### Database
- SQLite với WAL mode (write-ahead logging) cho hiệu năng cao
- Unified VIEW `all_data` gộp books + quotes để query đồng nhất
- Pagination, filter, full-text search

### Dashboard
- Dark mode glassmorphism UI
- Realtime scraper status polling
- Export CSV/JSON với filter
- Responsive layout

---

## Yêu cầu hệ thống

- Python 3.10+
- Chrome/Chromium (cho Playwright và Selenium)
- Windows 10+ / Linux / macOS
