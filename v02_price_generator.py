import os
import json
import random
from datetime import datetime, timedelta

def generate_multi_scenario_prices(
    output_dir="/mnt/data/killcore/prices",
    start_price=100.0,
    days=100,
    scenarios=None
):
    if scenarios is None:
        scenarios = ["choppy", "uptrend", "downtrend", "volatile"]

    os.makedirs(output_dir, exist_ok=True)
    price_sets = {}

    for mode in scenarios:
        prices = []
        price = start_price
        timestamp = datetime.now()

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

        file_path = os.path.join(output_dir, f"{mode}.json")
        with open(file_path, "w") as f:
            json.dump(prices, f, indent=2)
        price_sets[mode] = file_path

    return price_sets

if __name__ == "__main__":
    files = generate_multi_scenario_prices()
    for k, v in files.items():
        print(f"[v02] 已產生情境 {k}，儲存於：{v}")
