import os
import json
import requests

API = "https://api.mexc.com/api/v3/ticker/24hr"
TOP_N = 3
EXCLUDE = ["PEPE"]
MIN_VOLUME = 300_000
SAVE_PATH = "/mnt/data/killcore/symbol_pool.json"

def get_top_symbols():
    try:
        res = requests.get(API, timeout=10)
        data = res.json()
        pool = []

        for item in data:
            sym = item["symbol"]
            vol = float(item.get("quoteVolume", 0))

            if not sym.endswith("USDT"):
                continue
            if any(ex in sym for ex in EXCLUDE):
                continue
            if vol < MIN_VOLUME:
                continue

            pool.append((sym, vol))

        pool.sort(key=lambda x: x[1], reverse=True)
        top_symbols = [s[0] for s in pool[:TOP_N]]

        with open(SAVE_PATH, "w") as f:
            json.dump(top_symbols, f, indent=2)

        print(f"[S16] 幣池已建構: {top_symbols}")

    except Exception as e:
        print(f"[S16] 錯誤：{e}")

if __name__ == "__main__":
    get_top_symbols()
