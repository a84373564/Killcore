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

    def get_resurrect_prob(king_count):
        if king_count == 2:
            return 0.2
        elif king_count == 3:
            return 0.4
        elif king_count == 4:
            return 0.6
        elif king_count >= 5:
            return 0.8
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

    king_map = {item["signature"]: item.get("king_count", 1) for item in king_archive if "signature" in item}
    counters = {s[0]: 0 for s in strategy_definitions}
    generated = 0
    seen = set()
    modules = []

    while len(modules) < num_modules:
        code, label, name, param_space = random.choice(strategy_definitions)
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
            "strategy_logic": "PLACEHOLDER",
            "signature": sig,
            "from_retry": from_retry,
            "resurrected_king": resurrected_king,
            "force_retry": False
        }
        modules.append(mod)

    while len(modules) < 500:
        code, label, name, param_space = random.choice(strategy_definitions)
        params = {k: random.choice(v) for k, v in param_space.items()}
        sig = f"{name}_" + "_".join(str(v) for v in params.values())
        counters[code] += 1
        mod = {
            "name": f"{code}-{counters[code]:03d}",
            "strategy_name": name,
            "strategy_label": label,
            "parameters": params,
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
    print(f"[v01] 已產生模組數量：{count}（含智慧補血與王者復活機制）")
