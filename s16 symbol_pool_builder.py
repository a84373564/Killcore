import os
import json
import requests
from datetime import datetime

API = "https://api.mexc.com/api/v3/ticker/24hr"
TOP_N = 5
MIN_VOLUME = 300_000
EXCLUDE_KEYWORDS = ["PEPE", "TRUMP", "BONK", "1000", "DOGE", "LEVER", "DOWN", "UP", "ETF"]
FALLBACK = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
SAVE_PATH = "/mnt/data/killcore/symbol_pool.json"

def is_valid_symbol(symbol: str) -> bool:
    if not symbol.endswith("USDT"):
        return False
    for kw in EXCLUDE_KEYWORDS:
        if kw in symbol:
            return False
    return True

def get_top_symbols():
    try:
        res = requests.get(API, timeout=10)
        data = res.json()
        pool = []

        for item in data:
            symbol = item["symbol"]
            quote_volume = float(item.get("quoteVolume", 0))

            if not is_valid_symbol(symbol):
                continue
            if quote_volume < MIN_VOLUME:
                continue

            pool.append((symbol, quote_volume))

        pool.sort(key=lambda x: x[1], reverse=True)
        top_symbols = [s[0] for s in pool[:TOP_N]]

        if not top_symbols:
            print("[S16] 無合格幣種，自動使用主流備選幣。")
            top_symbols = FALLBACK

        result = {
            "timestamp": datetime.now().isoformat(),
            "symbol_pool": top_symbols
        }

        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w") as f:
            json.dump(result, f, indent=2)

        print(f"[S16] 幣池建構完成：{top_symbols}")

    except Exception as e:
        print(f"[S16] 錯誤：{e}")

if __name__ == "__main__":
    get_top_symbols()
