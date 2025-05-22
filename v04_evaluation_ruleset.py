import os
import json

def evaluate_modules_v04(
    sandbox_dir="/mnt/data/killcore/sandbox_results",
    output_path="/mnt/data/killcore/module_scores.json",
    log_path="/mnt/data/killcore/logs/evaluation_log.txt",
    weights=None
):
    if weights is None:
        weights = {
            "profit": 1,
            "drawdown": -5,
            "sharpe": 3,
            "win_rate": 2
        }

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    module_scores = {}
    for fname in os.listdir(sandbox_dir):
        if not fname.endswith(".json"):
            continue

        full_path = os.path.join(sandbox_dir, fname)
        with open(full_path, "r") as f:
            data = json.load(f)

        name = data["name"]
        if name not in module_scores:
            module_scores[name] = {
                "scores": [],
                "details": []
            }

        score = (
            data.get("profit", 0) * weights["profit"] +
            data.get("drawdown", 0) * weights["drawdown"] +
            data.get("sharpe", 0) * weights["sharpe"] +
            data.get("win_rate", 0) * weights["win_rate"]
        )

        module_scores[name]["scores"].append(score)
        module_scores[name]["details"].append(data)

    ranked_modules = []
    log_lines = []

    for name, info in module_scores.items():
        all_scores = info["scores"]
        avg_score = round(sum(all_scores) / len(all_scores), 2)
        max_score = round(max(all_scores), 2)
        total_tests = len(all_scores)

        ranked_modules.append({
            "name": name,
            "average_score": avg_score,
            "max_score": max_score,
            "tests_run": total_tests,
            "details": info["details"]
        })

        log_lines.append(f"{name}: avg={avg_score}, max={max_score}, runs={total_tests}")

    ranked_modules = sorted(ranked_modules, key=lambda x: x["average_score"], reverse=True)

    with open(output_path, "w") as f:
        json.dump(ranked_modules, f, indent=2)

    with open(log_path, "w") as lf:
        lf.write("\n".join(log_lines))

    return ranked_modules

if __name__ == "__main__":
    results = evaluate_modules_v04()
    print(f"[v04] 評分完成，模組數量：{len(results)}，已儲存至 module_scores.json")
