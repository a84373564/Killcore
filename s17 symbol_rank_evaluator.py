import os
import json
from collections import defaultdict

POOL_PATH = "/mnt/data/killcore/symbol_pool.json"
SANDBOX_DIR = "/mnt/data/killcore/sandbox_results"
RANK_OUTPUT = "/mnt/data/killcore/symbol_rank.json"

def load_symbol_pool():
    try:
        with open(POOL_PATH, "r") as f:
            data = json.load(f)
            return data.get("symbol_pool", [])
    except:
        return []

def evaluate_symbols(symbols):
    score_map = defaultdict(list)
    file_list = os.listdir(SANDBOX_DIR)

    for fname in file_list:
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(SANDBOX_DIR, fname), "r") as f:
                mod = json.load(f)
            sym = mod.get("symbol")
            score = mod.get("score")
            if sym in symbols and isinstance(score, (int, float)):
                score_map[sym].append(score)
        except:
            continue

    result = {}
    for sym in symbols:
        scores = score_map.get(sym, [])
        if scores:
            result[sym] = round(sum(scores) / len(scores), 4)

    sorted_syms = sorted(result.items(), key=lambda x: x[1], reverse=True)
    ranked = [s[0] for s in sorted_syms]

    output = {
        "symbol_ranking": ranked,
        "symbol_scores": result,
        "total_symbols": len(ranked)
    }

    with open(RANK_OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print(f"[S17] 幣別強度已排序，共 {len(ranked)} 幣別")

if __name__ == "__main__":
    syms = load_symbol_pool()
    evaluate_symbols(syms)
