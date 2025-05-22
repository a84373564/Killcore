import os
import json
import random
import numpy as np

def logic_run(strategy_name, day_data, capital, history):
    price = day_data["close"]
    if strategy_name == "trend_follow":
        if len(history) >= 5:
            ma = np.mean([h["close"] for h in history[-5:]])
            if price > ma:
                return "buy", 0.7
    elif strategy_name == "mean_revert":
        if len(history) >= 10:
            ma = np.mean([h["close"] for h in history[-10:]])
            if price < ma:
                return "buy", 0.65
    elif strategy_name == "breakout":
        if len(history) >= 20:
            high = max([h["high"] for h in history[-20:]])
            if price > high:
                return "buy", 0.75
    return "", 0.0

def run_logic_based_sandbox(modules_dir="/mnt/data/killcore/v01_modules",
                            price_path="/mnt/data/killcore/prices/sim_price.json",
                            output_dir="/mnt/data/killcore/sandbox_results",
                            capital_file="/mnt/data/hello/mexc_keys.json"):
    os.makedirs(output_dir, exist_ok=True)
    with open(price_path, "r") as pf:
        prices = json.load(pf)

    with open(capital_file, "r") as cf:
        capital_info = json.load(cf)
        starting_capital = capital_info.get("capital", 100)

    results = []
    for filename in os.listdir(modules_dir):
        if not filename.endswith(".json"):
            continue
        try:
            with open(os.path.join(modules_dir, filename), "r") as mf:
                mod = json.load(mf)

            balance = starting_capital
            history = []
            win, loss = 0, 0
            equity_curve = []

            for day in prices:
                signal, confidence = logic_run(mod["strategy_name"], day, balance, history)

                if signal == "buy" and confidence >= 0.5:
                    pct_change = random.uniform(-0.02, 0.05)
                    profit = balance * pct_change
                    balance += profit
                    if profit > 0:
                        win += 1
                    else:
                        loss += 1

                equity_curve.append(balance)
                history.append(day)

            profit_pct = round((balance - starting_capital) / starting_capital * 100, 2)
            win_rate = round(win / (win + loss + 1e-5), 2)
            max_dd = round(1 - min(equity_curve) / max(equity_curve), 2)
            sharpe = round((np.mean(equity_curve) - starting_capital) / (np.std(equity_curve) + 1e-5), 2)

            result_data = {
                "name": mod["name"],
                "strategy_name": mod["strategy_name"],
                "profit": profit_pct,
                "win_rate": win_rate,
                "drawdown": max_dd,
                "sharpe": sharpe,
                "score": profit_pct - max_dd * 5 + sharpe * 3 + win_rate * 2,
                "capital_used": starting_capital
            }

            output_path = os.path.join(output_dir, mod["name"] + ".json")
            with open(output_path, "w") as outf:
                json.dump(result_data, outf, indent=2)
            results.append(result_data)

        except Exception:
            continue

    return len(results), output_dir

if __name__ == "__main__":
    count, path = run_logic_based_sandbox()
    print(f"[v03] 成功模擬：{count} 隻模組，輸出於：{path}")
