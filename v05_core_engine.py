import os
import json
from v07_king_pool import create_king_pool_v07  # 封存模組載入

def run_v05_core_engine(
    scores_path="/mnt/data/killcore/module_scores.json",
    modules_dir="/mnt/data/killcore/v01_modules",
    memory_path="/mnt/data/killcore/memory_bank.json",
    sandbox_dir="/mnt/data/killcore/sandbox_results"
):
    with open(scores_path, "r") as f:
        ranked = json.load(f)

    new_king = ranked[0]
    king_name = new_king["name"]
    print(f"[v05] 王者模組為：{king_name}")

    king_file = os.path.join(modules_dir, f"{king_name}.json")
    with open(king_file, "r") as kf:
        king_data = json.load(kf)

    king_record = {
        "name": king_name,
        "score": new_king["average_score"],
        "max_score": new_king["max_score"],
        "strategy_name": king_data.get("strategy_name"),
        "strategy_label": king_data.get("strategy_label"),
        "parameters": king_data.get("parameters"),
        "signature": king_data.get("signature"),
        "from_retry": king_data.get("from_retry", False),
        "was_king": True,
        "king_count": king_data.get("king_count", 0) + 1
    }

    # 呼叫 v07 模組封存王者
    create_king_pool_v07(king_record)

    # 記憶庫更新
    losers = ranked[1:]
    memory_entries = []
    for loser in losers:
        loser_name = loser["name"]
        loser_file = os.path.join(modules_dir, f"{loser_name}.json")
        try:
            with open(loser_file, "r") as lf:
                loser_data = json.load(lf)
        except:
            continue

        memory_entries.append({
            "strategy_signature": loser_data.get("signature"),
            "strategy_name": loser_data.get("strategy_name"),
            "reason": "eliminated_by_v05",
            "score": round(loser["average_score"], 2),
            "drawdown": loser["details"][0].get("drawdown", 0),
            "was_king": False
        })

    if os.path.exists(memory_path):
        with open(memory_path, "r") as mf:
            old_memory = json.load(mf)
    else:
        old_memory = []

    memory_combined = old_memory + memory_entries
    memory_combined = sorted(memory_combined, key=lambda x: x.get("score", -999))[-300:]
    with open(memory_path, "w") as mf:
        json.dump(memory_combined, mf, indent=2)

    # 刪除模組（非王者）與沙盤結果
    for fname in os.listdir(modules_dir):
        if not fname.startswith(king_name) and fname.endswith(".json"):
            os.remove(os.path.join(modules_dir, fname))

    for sfile in os.listdir(sandbox_dir):
        os.remove(os.path.join(sandbox_dir, sfile))

    return king_record

if __name__ == "__main__":
    result = run_v05_core_engine()
    print(f"[v05] 王者產生完成：{result['name']}")
