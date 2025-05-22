import os
import json
import random

def generate_strategies_v01_clean(
    num_modules=500,
    output_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json"
):
    os.makedirs(output_dir, exist_ok=True)

    strategy_templates = [
        {
            "name": "trend_follow",
            "logic": "if ma > price: signal = 'buy'",
            "param_space": {
                "ma_window": [5, 10, 20, 30],
                "threshold": [0.01, 0.02, 0.03]
            }
        },
        {
            "name": "mean_revert",
            "logic": "if price < ma - threshold: signal = 'buy'",
            "param_space": {
                "ma_window": [10, 20],
                "threshold": [0.02, 0.03, 0.04]
            }
        },
        {
            "name": "breakout",
            "logic": "if price > highest_recent: signal = 'buy'",
            "param_space": {
                "break_window": [20, 30, 40],
                "threshold": [0.01, 0.015]
            }
        }
    ]

    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
            past_failures = {item["strategy_signature"] for item in memory}
    except Exception:
        past_failures = set()

    counts = {"trend_follow": 0, "mean_revert": 0, "breakout": 0}
    generated = 0
    for i in range(num_modules * 2):
        template = random.choice(strategy_templates)
        params = {k: random.choice(v) for k, v in template["param_space"].items()}
        sig_parts = [template["name"]] + [str(v) for v in params.values()]
        signature = "_".join(sig_parts)
        if signature in past_failures:
            continue

        counts[template["name"]] += 1
        mod = {
            "name": f"mod_{template['name']}_{counts[template['name']]:03d}",
            "strategy_name": template["name"],
            "parameters": params,
            "strategy_logic": template["logic"],
            "signature": signature,
            "run": "def run(data, capital, history): return {'signal': 'buy', 'confidence': 0.8}"
        }

        file_path = os.path.join(output_dir, f"{mod['name']}.json")
        with open(file_path, "w") as f:
            json.dump(mod, f, indent=2)

        generated += 1
        if generated >= num_modules:
            break

    return generated

if __name__ == "__main__":
    count = generate_strategies_v01_clean()
    print(f"[v01] 已產生模組數量：{count}")
