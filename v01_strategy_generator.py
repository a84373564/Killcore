import os
import json
import random

def generate_strategies_v01_final(
    num_modules=500,
    output_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json"
):
    os.makedirs(output_dir, exist_ok=True)

    # 策略代號、中文簡稱、英文識別
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
        ("E", "拉回佈局", "pullback_buy", {
            "pullback_pct": [0.03, 0.05],
            "trend_window": [10, 20]
        }),
        ("F", "動能疊加", "momentum_stack", {
            "momentum_window": [5, 10],
            "confirm_count": [2, 3]
        }),
        ("G", "均線交叉", "crossover_ma", {
            "fast": [5, 10],
            "slow": [20, 30]
        }),
        ("H", "價量共振", "volume_expansion", {
            "vol_window": [5, 10],
            "volume_ratio": [1.5, 2.0]
        }),
        ("I", "RSI 背離", "rsi_divergence", {
            "rsi_period": [14],
            "div_threshold": [5, 10]
        }),
        ("J", "布林爆發", "boll_squeeze", {
            "boll_window": [20],
            "squeeze_threshold": [0.02, 0.03]
        })
    ]

    # 判斷是否允許重試
    def allow_retry(signature, memory):
        related = [m for m in memory if m["strategy_signature"] == signature]
        if not related:
            return True, False
        retry_chance = 0.01
        for entry in related:
            if entry.get("was_king"):
                if entry.get("king_count", 1) >= 2:
                    retry_chance = max(retry_chance, 0.5)
                else:
                    retry_chance = max(retry_chance, 0.05)
        return random.random() < retry_chance, True

    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
    except Exception:
        memory = []

    past_failures = {item["strategy_signature"] for item in memory}
    counts = {code: 0 for code, _, _, _ in strategy_definitions}
    generated = 0

    for _ in range(num_modules * 5):
        code, cname, sname, param_space = random.choice(strategy_definitions)
        params = {k: random.choice(v) for k, v in param_space.items()}
        sig_parts = [sname] + [str(v) for v in params.values()]
        signature = "_".join(sig_parts)

        is_retry_allowed, from_retry = True, False
        if signature in past_failures:
            is_retry_allowed, from_retry = allow_retry(signature, memory)
            if not is_retry_allowed:
                continue

        counts[code] += 1
        mod = {
            "name": f"{code}-{counts[code]}",
            "strategy_name": sname,
            "strategy_label": cname,
            "parameters": params,
            "signature": signature,
            "from_retry": from_retry,
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
    count = generate_strategies_v01_final()
    print(f"[v01] 已產生模組數量：{count}")
