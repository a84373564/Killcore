import requests
import json
import os

KEY_PATH = "/mnt/data/killcore/mexc_keys.json"
OUTPUT_PATH = "/mnt/data/killcore/symbol_pool.json"
MIN_VOLUME_USDT = 500000  # 最低 24h 成交量門檻
TOP_LIMIT = 3             # 取前幾名幣種

def load_keys():
    try:
        with open(KEY_PATH, "r") as f:
            keys = json.load(f)
        return keys["api_key"], keys["api_secret"]
    except Exception as e:
        print(f"[!] 無法讀取金鑰：{e}")
        return None, None

def get_mexc_symbols():
    url = "https://api.mexc.com/api/v3/exchangeInfo"
    try:
        resp = requests.get(url, timeout=10)
        symbols = resp.json()["symbols"]
        usdt_pairs = [s["symbol"] for s in symbols if s["quoteAsset"] == "USDT" and s["status"] == "ENABLED"]
        return usdt_pairs
    except Exception as e:
        print(f"[!] 取得幣種清單失敗：{e}")
        return []

def get_ticker_data():
    url = "https://api.mexc.com/api/v3/ticker/24hr"
    try:
        resp = requests.get(url, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"[!] 取得成交量資料失敗：{e}")
        return []

def build_symbol_pool():
    all_symbols = get_mexc_symbols()
    ticker_data = get_ticker_data()
    volume_rank = []

    for item in ticker_data:
        symbol = item.get("symbol")
        quote_volume = float(item.get("quoteVolume", 0))
        if symbol in all_symbols and quote_volume >= MIN_VOLUME_USDT:
            volume_rank.append((symbol, quote_volume))

    # 按成交量排序，取前 N 名
    sorted_top = sorted(volume_rank, key=lambda x: x[1], reverse=True)[:TOP_LIMIT]
    top_symbols = [s[0] for s in sorted_top]

    # 寫入 JSON 結果
    with open(OUTPUT_PATH, "w") as f:
        json.dump(top_symbols, f, indent=2)

    print(f"[S16] 幣池已建構：{top_symbols}")
    return top_symbols

if __name__ == "__main__":
    build_symbol_pool()
