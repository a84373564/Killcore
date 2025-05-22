import os
import json
import random

def generate_strategies_v01_final(
    num_modules=500,
    output_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json",
    king_archive_path="/mnt/data/killcore/v10_king_archive.json",
    symbol_pool_path="/mnt/data/killcore/symbol_pool.json"
):
    os.makedirs(output_dir, exist_ok=True)

    strategy_definitions = [
        ("A", "順勢追擊", "trend_follow", {
            "ma_window": [5, 10, 20, 30],
            "threshold": [0.01, 0.02, 0.03]
        }),
        ("B", "均值回歸", "mean_revert", {
            "ma_window": [10, 20],
            "threshold": [0.02, 0.03, 0.04]
        }),
        ("C", "突破進攻", "breakout", {
            "break_window": [20, 30, 40],
            "threshold": [0.01, 0.015]
        }),
        ("D", "波動爆發", "volatility_spike", {
            "vol_window": [10, 20],
            "spike_threshold": [1.5, 2.0]
        }),
        ("E", "壓力反打", "resistance_rebound", {
            "res_window": [10, 20],
            "fail_ratio": [0.1, 0.2]
        }),
        ("F", "盤整突破", "range_break", {
            "range_window": [15, 25],
            "confirm_ratio": [0.6, 0.7]
        }),
        ("G", "高低反轉", "highlow_reversal", {
            "lookback": [10, 20],
            "reversal_ratio": [0.2, 0.3]
        }),
        ("H", "籌碼累積", "volume_accumulation", {
            "vol_window": [10, 15],
            "threshold": [0.05, 0.08]
        }),
        ("I", "單邊趨勢", "unilateral_trend", {
            "trend_strength": [1.2, 1.5],
            "bias": [0.1, 0.2]
        }),
        ("J", "多空激戰", "mixed_warfare", {
            "short_ma": [5, 10],
            "long_ma": [20, 30],
            "bias": [0.05, 0.1]
        })
    ]

    def get_resurrect_prob(king_count):
        if king_count == 2: return 0.2
        if king_count == 3: return 0.4
        if king_count == 4: return 0.6
        if king_count >= 5: return 0.8
        return 0.0

    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
        dead_signatures = {item["strategy_signature"] for item in memory}
    except:
        dead_signatures = set()

    try:
        with open(king_archive_path, "r") as f:
            king_archive = json.load(f)
    except:
        king_archive = []

    try:
        with open(symbol_pool_path, "r") as f:
            symbols = json.load(f)
    except:
        symbols = ["BTCUSDT", "ETHUSDT", "SUIUSDT", "APTUSDT"]

    king_map = {item["signature"]: item.get("king_count", 1) for item in king_archive if "signature" in item}
    counters = {s[0]: 0 for s in strategy_definitions}
    seen = set()
    modules = []

    while len(modules) < num_modules:
        code, label, name, param_space = random.choice(strategy_definitions)
        if not all(param_space.values()):
            continue
        params = {k: random.choice(v) for k, v in param_space.items()}
        sig = f"{name}_" + "_".join(str(v) for v in params.values())
        if sig in seen:
            continue

        from_retry = False
        resurrected_king = False

        if sig in dead_signatures:
            if sig in king_map:
                prob = get_resurrect_prob(king_map[sig])
                if random.random() < prob:
                    from_retry = True
                    resurrected_king = True
                else:
                    continue
            elif random.random() < 0.01:
                from_retry = True
            else:
                continue

        seen.add(sig)
        counters[code] += 1
        mod = {
            "name": f"{code}-{counters[code]:03d}",
            "strategy_name": name,
            "strategy_label": label,
            "parameters": params,
            "symbol": random.choice(symbols),
            "strategy_logic": "PLACEHOLDER",
            "signature": sig,
            "from_retry": from_retry,
            "resurrected_king": resurrected_king,
            "force_retry": False
        }
        modules.append(mod)

    while len(modules) < 500:
        code, label, name, param_space = random.choice(strategy_definitions)
        params = {k: random.choice(v) for k, v in param_space.items() if v}
        sig = f"{name}_" + "_".join(str(v) for v in params.values())
        counters[code] += 1
        mod = {
            "name": f"{code}-{counters[code]:03d}",
            "strategy_name": name,
            "strategy_label": label,
            "parameters": params,
            "symbol": random.choice(symbols),
            "strategy_logic": "PLACEHOLDER",
            "signature": sig,
            "from_retry": True,
            "resurrected_king": False,
            "force_retry": True
        }
        modules.append(mod)

    for mod in modules:
        file_path = os.path.join(output_dir, f"{mod['name']}.json")
        with open(file_path, "w") as f:
            json.dump(mod, f, indent=2)

    return len(modules)

if __name__ == "__main__":
    count = generate_strategies_v01_final()
    print(f"[v01] 已產生模組數量：{count}（A～J 策略 + 多幣 + WDRR + 智慧補血）")
