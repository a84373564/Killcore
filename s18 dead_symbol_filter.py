# [S18] 幣別黑名單篩選器：找出長期表現低劣、值得封殺的幣種

import os
import json
from collections import defaultdict

SANDBOX_DIR = "/mnt/data/killcore/sandbox_results"
BLACKLIST_PATH = "/mnt/data/killcore/dead_symbol_list.json"

MIN_FAIL_COUNT = 5        # 低於此數量不處理
MAX_AVG_SCORE = 5         # 若平均分數小於此值，列入黑名單
KING_REQUIRED = True      # 若無王者出現，視為失敗幣

def build_blacklist():
    stats = defaultdict(lambda: {"scores": [], "fail_count": 0, "king_count": 0})

    for file in os.listdir(SANDBOX_DIR):
        if not file.endswith(".json"):
            continue
        try:
            with open(os.path.join(SANDBOX_DIR, file), "r") as f:
                data = json.load(f)
            symbol = data.get("symbol")
            score = data.get("score", 0)
            is_king = data.get("is_king", False)
            success = data.get("success", True)

            if symbol:
                stats[symbol]["scores"].append(score)
                if not success:
                    stats[symbol]["fail_count"] += 1
                if is_king:
                    stats[symbol]["king_count"] += 1
        except:
            continue

    blacklist = []
    for symbol, val in stats.items():
        avg_score = sum(val["scores"]) / len(val["scores"])
        fail = val["fail_count"]
        king = val["king_count"]
        if fail >= MIN_FAIL_COUNT and avg_score < MAX_AVG_SCORE:
            if KING_REQUIRED and king == 0:
                blacklist.append(symbol)

    result = {
        "blacklisted_symbols": blacklist,
        "total_filtered": len(blacklist)
    }

    os.makedirs(os.path.dirname(BLACKLIST_PATH), exist_ok=True)
    with open(BLACKLIST_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[S18] 黑名單已完成，共 {len(blacklist)} 幣")

if __name__ == "__main__":
    build_blacklist()
