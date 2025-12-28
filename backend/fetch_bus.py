import requests
import psycopg2
from datetime import datetime
# 引用你剛剛寫好的 tdx_auth 來取得 Token
from tdx_auth import get_tdx_token

# --- 資料庫連線設定 (請確認密碼正確) ---
DB_CONFIG = {
    "host": "localhost",
    "dbname": "smart_city",
    "user": "postgres",
    "password": "asrtghjv524",  # ⚠️ 請記得修改這裡
    "port": "5432"
}

# --- TDX 公車即時動態 API (台北市) ---
# 抓取公車的即時位置
BUS_API_URL = "https://tdx.transportdata.tw/api/basic/v2/Bus/RealTimeByFrequency/City/Taipei?$format=JSON"

def fetch_bus_data():
    try:
        # 1. 取得 Token
        token = get_tdx_token()
        
        # 2. 設定 Header
        headers = {
            "authorization": f"Bearer {token}"
        }
        
        # 3. 呼叫 API
        print("🚌 正在抓取公車資料...")
        response = requests.get(BUS_API_URL, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API 抓取失敗: {response.status_code}, {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return []

def save_bus_to_db(bus_list):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        count = 0
        for bus in bus_list:
            # 解析資料
            plate_numb = bus.get("PlateNumb", "未知車號")
            route_name = bus.get("RouteName", {}).get("Zh_tw", "未知路線")
            lat = bus.get("BusPosition", {}).get("PositionLat")
            lon = bus.get("BusPosition", {}).get("PositionLon")
            speed = bus.get("Speed", 0)
            
            # 組合站點名稱為 "路線 - 車號" (例如: 307 - 123-FA)
            display_name = f"{route_name} - {plate_numb}"

            # 插入資料庫 (這裡我們把公車視為 public_transit 的一種)
            # 注意：經緯度若為空則跳過
            if lat and lon:
                cur.execute("""
                    INSERT INTO public_transit 
                    (station_name, location, usage_count, transport_type, created_at)
                    VALUES (%s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s, NOW());
                """, (display_name, float(lon), float(lat), int(speed), "bus"))
                count += 1

        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ 成功寫入 {count} 筆公車資料到資料庫！")

    except Exception as e:
        print(f"❌ 資料庫錯誤: {e}")

if __name__ == "__main__":
    # 執行流程
    data = fetch_bus_data()
    if data:
        print(f"📥 取得 {len(data)} 筆原始資料")
        save_bus_to_db(data)
