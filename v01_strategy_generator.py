import os
import json
import random

def generate_strategies_v01_retryable(
    num_modules=500,
    output_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json"
):
    os.makedirs(output_dir, exist_ok=True)

    # 策略模板池
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

    # 判斷是否給重生機會
    def allow_retry(signature, memory):
        related = [m for m in memory if m["strategy_signature"] == signature]
        if not related:
            return True  # 沒死過，當然可以生成

        retry_chance = 0.01  # 基本死法重試率
        for entry in related:
            if entry.get("was_king"):
                if entry.get("king_count", 1) >= 2:
                    retry_chance = max(retry_chance, 0.5)  # 多次王者給 50%
                else:
                    retry_chance = max(retry_chance, 0.05)  # 一次王者給 5%
        return random.random() < retry_chance

    # 載入記憶資料
    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
    except Exception:
        memory = []

    past_failures = {item["strategy_signature"] for item in memory}

    counts = {"trend_follow": 0, "mean_revert": 0, "breakout": 0}
    generated = 0

    # 開始生成模組
    for i in range(num_modules * 4):  # 預留足夠嘗試次數
        template = random.choice(strategy_templates)
        params = {k: random.choice(v) for k, v in template["param_space"].items()}
        sig_parts = [template["name"]] + [str(v) for v in params.values()]
        signature = "_".join(sig_parts)

        # 若為死亡組合，檢查是否允許重試
        if signature in past_failures and not allow_retry(signature, memory):
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

# 主程式入口
if __name__ == "__main__":
    count = generate_strategies_v01_retryable()
    print(f"[v01] 已產生模組數量：{count}")
