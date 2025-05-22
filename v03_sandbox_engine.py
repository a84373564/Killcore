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

def enhanced_sandbox_engine(
    modules_dir="/mnt/data/killcore/v01_modules",
    prices_dir="/mnt/data/killcore/prices",
    output_dir="/mnt/data/killcore/sandbox_results",
    capital_file="/mnt/data/hello/mexc_keys.json",
    memory_path="/mnt/data/killcore/memory_bank.json",
    log_path="/mnt/data/killcore/logs/sandbox_log.txt"
):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(capital_file, "r") as cf:
        capital_info = json.load(cf)
        starting_capital = capital_info.get("capital", 100)

    memory = []
    if os.path.exists(memory_path):
        with open(memory_path, "r") as mf:
            memory = json.load(mf)

    summary = []
    log_lines = []

    for mod_file in os.listdir(modules_dir):
        if not mod_file.endswith(".json"):
            continue

        with open(os.path.join(modules_dir, mod_file), "r") as mf:
            mod = json.load(mf)

        all_scores = []
        for price_file in os.listdir(prices_dir):
            if not price_file.endswith(".json"):
                continue

            with open(os.path.join(prices_dir, price_file), "r") as pf:
                prices = json.load(pf)

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
            score = profit_pct - max_dd * 5 + sharpe * 3 + win_rate * 2

            result_data = {
                "name": mod["name"],
                "strategy_name": mod["strategy_name"],
                "price_file": price_file,
                "profit": profit_pct,
                "win_rate": win_rate,
                "drawdown": max_dd,
                "sharpe": sharpe,
                "score": round(score, 2),
                "capital_used": starting_capital
            }

            out_path = os.path.join(output_dir, f"{mod['name']}__{price_file}")
            with open(out_path, "w") as outf:
                json.dump(result_data, outf, indent=2)

            log_lines.append(f"[{mod['name']} - {price_file}] score={score:.2f} profit={profit_pct}% dd={max_dd} sharpe={sharpe}")

            if score < -10 or max_dd > 0.5:
                memory.append({
                    "strategy_signature": mod["signature"],
                    "strategy_name": mod["strategy_name"],
                    "reason": "poor_score",
                    "score": round(score, 2),
                    "drawdown": max_dd
                })

        avg_score = round(np.mean(all_scores), 2) if all_scores else 0
        summary.append((mod["name"], avg_score))

    with open(log_path, "w") as logf:
        logf.write("\n".join(log_lines))

    memory = sorted(memory, key=lambda x: x.get("score", -999))
    with open(memory_path, "w") as mf:
        json.dump(memory[-300:], mf, indent=2)

    return len(summary), output_dir

if __name__ == "__main__":
    count, path = enhanced_sandbox_engine()
    print(f"[v03] 多情境模擬完成，共處理模組：{count}，結果儲存於：{path}")
