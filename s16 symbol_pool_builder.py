import requests
import json
import os

KEY_PATH = "/mnt/data/killcore/mexc_keys.json"
SAVE_PATH = "/mnt/data/killcore/symbol_pool.json"
TOP_LIMIT = 3
MIN_VOLUME_USDT = 100000  # 可視情況調低來避免空結果

def load_keys():
    try:
        with open(KEY_PATH, "r") as f:
            keys = json.load(f)
            return keys.get("api_key", ""), keys.get("api_secret", "")
    except Exception as e:
        print(f"[S16] 無法讀取金鑰：{e}")
        return "", ""

def get_top_symbols():
    url = "https://api.mexc.com/api/v3/ticker/24hr"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        symbols = [
            {
                "symbol": item["symbol"],
                "volume": float(item.get("quoteVolume", 0))
            }
            for item in data
            if item["symbol"].endswith("USDT") and float(item.get("quoteVolume", 0)) > MIN_VOLUME_USDT
        ]
        sorted_symbols = sorted(symbols, key=lambda x: x["volume"], reverse=True)
        return [s["symbol"] for s in sorted_symbols[:TOP_LIMIT]]
    except Exception as e:
        print(f"[S16] 抓取幣種失敗：{e}")
        return []

def save_pool(symbols):
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(symbols, f, indent=2)
        print(f"[S16] 幣池已建構：{symbols}")
    except Exception as e:
        print(f"[S16] 儲存幣池失敗：{e}")

if __name__ == "__main__":
    top_symbols = get_top_symbols()
    if not top_symbols:
        print("[S16] 警告：幣池為空，請檢查 API 回應、網路、或 MIN_VOLUME_USDT 設定")
    save_pool(top_symbols)
