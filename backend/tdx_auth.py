import requests
import datetime

# 你的 TDX 金鑰（請自行填入）
CLIENT_ID = "C112151122-e7fb475f-c84d-48df"
CLIENT_SECRET = "a81b9656-6b24-4c29-959c-00af6ce46c75"

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"

# 全域 Token 快取
token_data = {
    "access_token": None,
    "expires_at": None
}

def get_tdx_token():
    """取得 TDX Access Token，並在過期時自動更新"""
    global token_data

    # 若 token 尚未取得或已過期 → 重新請求
    if (
        token_data["access_token"] is None or 
        datetime.datetime.now() >= token_data["expires_at"]
    ):
        print("🔄 正在向 TDX 申請新 Token...")

        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
        )

        if response.status_code != 200:
            raise Exception(f"TDX Token 取得失敗: {response.text}")

        result = response.json()
        token_data["access_token"] = result["access_token"]

        # 設定 Token 過期時間（提前 10 秒）
        token_data["expires_at"] = datetime.datetime.now() + datetime.timedelta(
            seconds=result["expires_in"] - 10
        )

        print("✅ Token 取得成功！")

    return token_data["access_token"]

