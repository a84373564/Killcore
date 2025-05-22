# [S17] 幣別強度排行器（根據 sandbox_results 分數統計）

import os
import json
from collections import defaultdict

SANDBOX_DIR = "/mnt/data/killcore/sandbox_results"
RANK_PATH = "/mnt/data/killcore/symbol_rank.json"
MIN_MODULES = 3  # 至少幾隻模組才納入統計
KING_BONUS = 1.2  # 王者模組加權倍數

def evaluate_symbols():
    scores = defaultdict(list)

    for fname in os.listdir(SANDBOX_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(SANDBOX_DIR, fname), "r") as f:
                data = json.load(f)
            symbol = data.get("symbol")
            score = data.get("score", 0)
            is_king = data.get("is_king", False)
            if not symbol:
                continue
            if is_king:
                score *= KING_BONUS
            scores[symbol].append(score)
        except Exception as e:
            print(f"[S17] 無法解析 {fname}：{e}")

    ranked = []
    for sym, lst in scores.items():
        if len(lst) < MIN_MODULES:
            continue
        avg = sum(lst) / len(lst)
        ranked.append((sym, avg))

    ranked.sort(key=lambda x: x[1], reverse=True)
    result = {
        "symbol_ranking": [r[0] for r in ranked],
        "symbol_scores": {r[0]: round(r[1], 3) for r in ranked},
        "total_symbols": len(ranked)
    }

    os.makedirs(os.path.dirname(RANK_PATH), exist_ok=True)
    with open(RANK_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[S17] 幣別強度已排序，共 {len(ranked)} 幣別")

if __name__ == "__main__":
    evaluate_symbols()
