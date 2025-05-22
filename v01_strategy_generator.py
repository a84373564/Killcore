import os
import json
import random
from datetime import datetime

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

def generate_killcore_strategies(num_modules=500,
                                  output_dir="/mnt/data/killcore/v01_modules",
                                  memory_path="/mnt/data/killcore/memory_bank.json",
                                  lineage_prefix="GEN"):
    os.makedirs(output_dir, exist_ok=True)
    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
            past_failures = {item["strategy_signature"] for item in memory}
    except Exception:
        past_failures = set()

    generated = 0
    for i in range(num_modules * 2):
        template = random.choice(strategy_templates)
        params = {k: random.choice(v) for k, v in template["param_space"].items()}
        sig_parts = [template["name"]] + [str(v) for v in params.values()]
        signature = "_".join(sig_parts)
        if signature in past_failures:
            continue

        mod = {
            "name": f"mod_{int(datetime.now().timestamp())}_{i}",
            "created_at": str(datetime.now()),
            "lineage": f"{lineage_prefix}-{i:03d}",
            "strategy_name": template["name"],
            "parameters": params,
            "strategy_logic": template["logic"],
            "signature": signature,
            "run": "def run(data, capital, history): return {'signal': 'buy', 'confidence': 0.8}"
        }

        path = os.path.join(output_dir, f"{mod['name']}.json")
        with open(path, "w") as f:
            json.dump(mod, f, indent=2)
        generated += 1
        if generated >= num_modules:
            break

    return generated
