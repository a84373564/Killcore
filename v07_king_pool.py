import os
import json
import time

def create_king_pool_v07(
    king_data,
    king_path="/mnt/data/killcore/v07_king_pool.json"
):
    # 無敵版欄位補齊（即使當下無用，也需存在）
    king_data.setdefault("created_at", time.time())
    king_data.setdefault("survival_rounds", 1)
    king_data.setdefault("kill_log", [])
    king_data.setdefault("strategy_tag", [])

    # 寫入封存資料
    with open(king_path, "w") as f:
        json.dump(king_data, f, indent=2)

    return king_data

if __name__ == "__main__":
    # 測試範例（實際執行時由 v05 提供 king_data）
    sample_king = {
        "name": "A-031",
        "strategy_name": "trend_follow",
        "strategy_label": "順勢追擊",
        "parameters": {
            "ma_window": 10,
            "threshold": 0.02
        },
        "signature": "trend_follow_10_0.02",
        "from_retry": False,
        "score": 36.27,
        "max_score": 38.90,
        "was_king": True,
        "king_count": 2
    }
    create_king_pool_v07(sample_king)
    print("[v07] 王者封存已建立。")
