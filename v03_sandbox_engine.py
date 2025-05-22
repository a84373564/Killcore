import os
import json
import math
import random
import numpy as np

MODULE_PATH = "/mnt/data/killcore/v01_modules"
PRICE_PATH = "/mnt/data/killcore/v02_prices"
RESULT_PATH = "/mnt/data/killcore/sandbox_results"
os.makedirs(RESULT_PATH, exist_ok=True)

def load_price(symbol, days=100):
    try:
        with open(f"{PRICE_PATH}/{symbol}.json", "r") as f:
            data = json.load(f)
        return data[-days:]  # 取最後 N 天
    except:
        return []

def logic_run(strategy_name, params, data):
    signal_history = []
    for i in range(len(data)):
        price = data[i]
        signal = None
        try:
            if strategy_name == "trend_follow":
                ma = np.mean(data[max(0, i - params["ma_window"]):i+1])
                if ma > price * (1 + params["threshold"]):
                    signal = "buy"
            elif strategy_name == "mean_revert":
                ma = np.mean(data[max(0, i - params["ma_window"]):i+1])
                if price < ma - params["threshold"]:
                    signal = "buy"
            elif strategy_name == "breakout":
                if i > params["break_window"]:
                    highest = max(data[i - params["break_window"]:i])
                    if price > highest * (1 + params["threshold"]):
                        signal = "buy"
            elif strategy_name == "volatility_spike":
                if i > params["vol_window"]:
                    std = np.std(data[i - params["vol_window"]:i])
                    if std > params["spike_threshold"]:
                        signal = "buy"
            elif strategy_name == "resistance_rebound":
                if i > params["res_window"]:
                    local_max = max(data[i - params["res_window"]:i])
                    if price < local_max * (1 - params["fail_ratio"]):
                        signal = "buy"
            elif strategy_name == "range_break":
                if i > params["range_window"]:
                    low = min(data[i - params["range_window"]:i])
                    high = max(data[i - params["range_window"]:i])
                    if (high - low) > 0 and (price - low)/(high - low) > params["confirm_ratio"]:
                        signal = "buy"
            elif strategy_name == "highlow_reversal":
                if i > params["lookback"]:
                    low = min(data[i - params["lookback"]:i])
                    high = max(data[i - params["lookback"]:i])
                    if price <= low * (1 + params["reversal_ratio"]):
                        signal = "buy"
            elif strategy_name == "volume_accumulation":
                if i > params["vol_window"]:
                    avg = np.mean(data[i - params["vol_window"]:i])
                    if price > avg * (1 + params["threshold"]):
                        signal = "buy"
            elif strategy_name == "unilateral_trend":
                if i > 10:
                    past = data[i - 10:i]
                    slope = (past[-1] - past[0]) / 10
                    if slope > params["trend_strength"]:
                        signal = "buy"
            elif strategy_name == "mixed_warfare":
                if i > params["long_ma"]:
                    short_ma = np.mean(data[i - params["short_ma"]:i])
                    long_ma = np.mean(data[i - params["long_ma"]:i])
                    if short_ma > long_ma * (1 + params["bias"]):
                        signal = "buy"
        except:
            signal = None
        signal_history.append(signal)
    return signal_history

def evaluate_performance(data, signals):
    capital = 1000
    position = 0
    entry_price = 0
    trades = 0
    pnl = []
    for i in range(len(data)):
        price = data[i]
        signal = signals[i]
        if signal == "buy" and position == 0:
            entry_price = price
            position = capital / price
        elif position > 0 and signal != "buy":
            capital = position * price
            pnl.append(capital)
            position = 0
            trades += 1
    if position > 0:
        capital = position * data[-1]
        pnl.append(capital)
    profit = capital - 1000
    returns = [p / 1000 - 1 for p in pnl] if pnl else [0]
    win_rate = sum(1 for r in returns if r > 0) / len(returns) if returns else 0
    max_drawdown = 0
    peak = 1000
    balance = 1000
    for p in pnl:
        peak = max(peak, p)
        dd = (peak - p) / peak
        max_drawdown = max(max_drawdown, dd)
    sharpe = np.mean(returns) / np.std(returns) if len(returns) > 1 else 0
    score = profit - max_drawdown * 5 + sharpe * 3 + win_rate * 2
    return {
        "profit": round(profit, 2),
        "drawdown": round(max_drawdown, 4),
        "sharpe": round(sharpe, 4),
        "win_rate": round(win_rate, 4),
        "score": round(score, 2),
        "trades": trades,
    }

def run_sandbox():
    module_files = [f for f in os.listdir(MODULE_PATH) if f.endswith(".json")]
    for f in module_files:
        try:
            with open(f"{MODULE_PATH}/{f}", "r") as mf:
                mod = json.load(mf)
            symbol = mod.get("symbol")
            if not symbol:
                continue
            price_data = load_price(symbol)
            if not price_data:
                continue
            prices = [float(p) for p in price_data]
            signals = logic_run(mod["strategy_name"], mod["parameters"], prices)
            result = evaluate_performance(prices, signals)
            mod.update(result)
            mod["log"] = signals
            mod["history"] = prices
            with open(f"{RESULT_PATH}/{f}", "w") as outf:
                json.dump(mod, outf, indent=2)
        except Exception as e:
            print(f"模組 {f} 失敗：{e}")

if __name__ == "__main__":
    run_sandbox()
    print("[v03] 沙盤模擬已完成，結果寫入 sandbox_results/")
