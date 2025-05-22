import os
import json
import random
import time

def generate_strategies_v01_final(
    num_modules=500,
    output_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json",
    king_archive_path="/mnt/data/killcore/v10_king_archive.json"
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
        })
    ]

    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
        dead_signatures = {item["strategy_signature"] for item in memory}
    except:
        dead_signatures = set()

    try:
        with open(king_archive_path, "r") as f:
            king_history = json.load(f)
    except:
        king_history = []

    resurrected_pool = []
    for item in king_history:
        if item.get("name") and item.get("king_count", 0) >= 2:
            prob = min(0.2 * item["king_count"], 0.8)
            if random.random() < prob:
                resurrected_pool.append(item["signature"])

    generated = []
    seen = set()
    counter = {code: 0 for code, _, _, _ in strategy_definitions}

    while len(generated) < num_modules:
        code, label, name, param_space = random.choice(strategy_definitions)
        params = {k: random.choice(v) for k, v in param_space.items()}
        sig = f"{name}_" + "_".join(str(v) for v in params.values())
        if sig in seen or sig in dead_signatures:
            continue

        seen.add(sig)
        counter[code] += 1

        mod = {
            "name": f"{code}-{counter[code]:03d}",
            "strategy_name": name,
            "strategy_label": label,
            "parameters": params,
            "strategy_logic": "PLACEHOLDER",
            "signature": sig,
            "from_retry": False,
            "resurrected_king": sig in resurrected_pool,
            "force_retry": False
        }

        generated.append(mod)

    # 智慧補血：補滿至 500
    while len(generated) < 500:
        code, label, name, param_space = random.choice(strategy_definitions)
        params = {k: random.choice(v) for k, v in param_space.items()}
        sig = f"{name}_" + "_".join(str(v) for v in params.values())
        counter[code] += 1

        mod = {
            "name": f"{code}-{counter[code]:03d}",
            "strategy_name": name,
            "strategy_label": label,
            "parameters": params,
            "strategy_logic": "PLACEHOLDER",
            "signature": sig,
            "from_retry": True,
            "resurrected_king": False,
            "force_retry": True
        }

        generated.append(mod)

    for mod in generated:
        file_path = os.path.join(output_dir, f"{mod['name']}.json")
        with open(file_path, "w") as f:
            json.dump(mod, f, indent=2)

    return len(generated)

if __name__ == "__main__":
    count = generate_strategies_v01_final()
    print(f"[v01] 已產生模組數量：{count}（含補血與重生邏輯）")
