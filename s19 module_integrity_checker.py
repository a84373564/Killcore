# S19 – 模組完整性檢查器（自動刪除異常模組）
import os
import json

MODULE_DIR = "/mnt/data/killcore/v01_modules"
REQUIRED_FIELDS = ["name", "symbol", "parameters", "strategy_label", "signature"]

def is_valid_module(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        for field in REQUIRED_FIELDS:
            if field not in data:
                print(f"[S19] 模組缺欄位 '{field}'，刪除：{os.path.basename(path)}")
                return False
        return True
    except Exception as e:
        print(f"[S19] 無法讀取模組 {os.path.basename(path)}，錯誤：{e}")
        return False

def clean_invalid_modules():
    count = 0
    for fname in os.listdir(MODULE_DIR):
        if not fname.endswith(".json"):
            continue
        full_path = os.path.join(MODULE_DIR, fname)
        if not is_valid_module(full_path):
            os.remove(full_path)
            count += 1
    print(f"[S19] 清理完成，共移除 {count} 筆異常模組")

if __name__ == "__main__":
    clean_invalid_modules()
