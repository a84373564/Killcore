# === 防呆補丁：確保 symbol_pool 結構存在且非空 ===
import json
SYMBOL_POOL_PATH = "/mnt/data/killcore/symbol_pool.json"
try:
    with open(SYMBOL_POOL_PATH, "r") as f:
        raw_pool = json.load(f)
    SYMBOL_LIST = raw_pool.get("symbol_pool", [])
    if not SYMBOL_LIST:
        print("[v01] 幣池為空，跳過本輪。")
        exit()
except Exception as e:
    print(f"[v01] 無法讀取幣池：{e}")
    exit()

import os
import random

def generate_strategies_v01_final(
    num_modules=500,
    output_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json",
    king_archive_path="/mnt/data/killcore/v10_king_archive.json",
    symbol_list=None
):
    os.makedirs(output_dir, exist_ok=True)
    symbols = symbol_list or []

    if not symbols:
        print("[v01] symbols 空值異常，強制跳過")
        return 0

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
        # === 限制最多記住 300 筆，保留最新的 ===
        if len(memory) > 300:
            memory = sorted(memory, key=lambda x: x.get("timestamp", ""), reverse=True)[:300]
        dead_signatures = {item["strategy_signature"] for item in memory}
    except:
        dead_signatures = set()

    try:
        with open(king_archive_path, "r") as f:
            king_archive = json.load(f)
    except:
        king_archive = []

    king_map = {item["signature"]: item.get("king_count", 1) for item in king_archive if "signature" in item}
    counters = {s[0]: 0 for s in strategy_definitions}
    seen = set()
    modules = []

    attempts = 0
    max_attempts = 2000

    while len(modules) < num_modules and attempts < max_attempts:
        code, label, name, param_space = random.choice(strategy_definitions)
        if not all(param_space.values()):
            attempts += 1
            continue
        params = {k: random.choice(v) for k, v in param_space.items() if v}

        # === 模組突變邏輯：隨機選一個參數，重新選一次 ===
        if params:
            mutate_key = random.choice(list(params.keys()))
            params[mutate_key] = random.choice(param_space[mutate_key])

        sig = f"{name}_" + "_".join(str(v) for v in params.values())
        if sig in seen:
            attempts += 1
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
                    attempts += 1
                    continue
            elif random.random() < 0.01:
                from_retry = True
            else:
                attempts += 1
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
            "force_retry": from_retry
        }
        modules.append(mod)
        attempts += 1

    for mod in modules:
        file_path = os.path.join(output_dir, f"{mod['name']}.json")
        with open(file_path, "w") as f:
            json.dump(mod, f, indent=2)

    return len(modules)

if __name__ == "__main__":
    count = generate_strategies_v01_final(symbol_list=SYMBOL_LIST)
    print(f"[v01] 已產生模組數量：{count}（A～J 策略 + 多幣 + WDRR + 智慧補血）")
