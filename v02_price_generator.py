import os
import json
import random
from datetime import datetime, timedelta

def generate_price_scenario(days=100,
                            mode="choppy",  # choppy / uptrend / downtrend / volatile
                            start_price=100.0,
                            output_path="/mnt/data/killcore/prices/sim_price.json"):
    prices = []
    timestamp = datetime.now()
    price = start_price

    for _ in range(days):
        if mode == "choppy":
            change = random.uniform(-0.5, 0.5)
        elif mode == "uptrend":
            change = random.uniform(0, 1)
        elif mode == "downtrend":
            change = random.uniform(-1, 0)
        elif mode == "volatile":
            change = random.uniform(-2, 2)
        else:
            change = 0

        open_price = price
        high_price = open_price + abs(change) * random.uniform(0.5, 1.2)
        low_price = open_price - abs(change) * random.uniform(0.5, 1.2)
        close_price = open_price + change
        price = max(1, close_price)

        prices.append({
            "time": timestamp.strftime("%Y-%m-%d"),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2)
        })
        timestamp += timedelta(days=1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(prices, f, indent=2)

    return output_path, len(prices)

if __name__ == "__main__":
    out, count = generate_price_scenario()
    print(f"[v02] 已產生模擬行情：{count} 天，儲存於：{out}")
