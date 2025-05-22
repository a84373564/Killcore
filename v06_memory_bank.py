import os
import json

def clean_memory_bank_v06(
    memory_path="/mnt/data/killcore/memory_bank.json",
    output_path="/mnt/data/killcore/memory_bank.json",
    log_path="/mnt/data/killcore/logs/memory_summary.txt",
    max_entries=300
):
    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
    except Exception:
        memory = []

    cleaned = []
    seen_signatures = set()
    stats = {}

    for entry in sorted(memory, key=lambda x: x.get("score", -999), reverse=True):
        sig = entry.get("strategy_signature")
        if not sig or sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        cleaned.append(entry)

        # 統計策略類型分布
        strategy = entry.get("strategy_name", "unknown")
        stats[strategy] = stats.get(strategy, 0) + 1

        if len(cleaned) >= max_entries:
            break

    with open(output_path, "w") as wf:
        json.dump(cleaned, wf, indent=2)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as lf:
        lf.write(f"[v06] 已保留記憶數量：{len(cleaned)}（最多 {max_entries} 筆）\n\n")
        lf.write("策略死亡分布統計：\n")
        for k, v in sorted(stats.items(), key=lambda x: -x[1]):
            lf.write(f" - {k}: {v} 次死亡\n")

    return len(cleaned), stats

if __name__ == "__main__":
    total, distribution = clean_memory_bank_v06()
    print(f"[v06] 清理完成：共保留 {total} 筆記憶")
