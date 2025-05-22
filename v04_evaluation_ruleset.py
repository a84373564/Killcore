# [v04] 評分規則模組｜計算總分，回傳排序結果（防爆版）

import os
import json

SANDBOX_DIR = "/mnt/data/killcore/sandbox_results"
OUTPUT_PATH = "/mnt/data/killcore/module_scores.json"

WEIGHTS = {
    "profit": 3.0,
    "sharpe": 2.0,
    "win_rate": 1.5,
    "drawdown": -2.0
}

def evaluate_modules_v04():
    results = []
    for fname in os.listdir(SANDBOX_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(SANDBOX_DIR, fname)
        try:
            with open(fpath, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[v04] 讀取錯誤：{fname} → {e}")
            continue

        # 防爆補丁：缺欄位直接跳過
        try:
            name = data["name"]
            profit = data.get("profit", 0)
            sharpe = data.get("sharpe", 0)
            win_rate = data.get("win_rate", 0)
            drawdown = data.get("drawdown", 0)
        except KeyError as e:
            print(f"[v04] 模組缺欄位 {e}，跳過 {fname}")
            continue

        # 計算分數
        score = (
            profit * WEIGHTS["profit"] +
            sharpe * WEIGHTS["sharpe"] +
            win_rate * WEIGHTS["win_rate"] +
            drawdown * WEIGHTS["drawdown"]
        )

        results.append({
            "name": name,
            "score": round(score, 4),
            "profit": profit,
            "sharpe": sharpe,
            "win_rate": win_rate,
            "drawdown": drawdown
        })

    # 依分數排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

if __name__ == "__main__":
    results = evaluate_modules_v04()
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[v04] 評分完成，總計 {len(results)} 模組已排序")
