import requests
import psycopg2
from datetime import datetime
import time

# PostgreSQL 連線設定
DB_CONFIG = {
    "dbname": "smart_city",
    "user": "postgres",
    "password": "asrtghjv524",  # ⚠️ 改成你的密碼
    "host": "localhost",
    "port": "5432"
}

API_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"

def fetch_data():
    """ 從 API 抓資料 """
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ API 抓取失敗:", response.status_code)
        return None

def save_to_db(data):
    """ 儲存資料到 PostgreSQL """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for item in data:
            station_id = item.get("sno", "未知")
            station_name = item.get("sna", "未知")
            lat = float(item.get("lat", 0))
            lon = float(item.get("lng", 0))
            usage_count = int(item.get("sbi", 0))
            now_time = datetime.now()

            # 防止重複插入同一站同時間資料
            cursor.execute("""
                INSERT INTO public_transit (station_id, station_name, location, "timestamp", usage_count, transport_type)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, %s)
            """, (station_id, station_name, lon, lat, now_time, usage_count, "bike"))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ 已成功寫入 {len(data)} 筆資料")

    except Exception as e:
        print("資料庫錯誤:", e)

def run_scheduler(interval_minutes=5):
    """ 每隔 interval_minutes 分鐘自動執行 """
    while True:
        print(f"🚴 開始抓取資料 {datetime.now()}")
        data = fetch_data()
        if data:
            save_to_db(data)
        print(f"⏳ 等待 {interval_minutes} 分鐘後再次執行...\n")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    run_scheduler(interval_minutes=5)
