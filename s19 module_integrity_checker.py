# S19｜模組完整性檢查器：自動刪除結構異常模組
import os
import json

MODULE_DIR = "/mnt/data/killcore/v01_modules"
DELETED = 0

print("[S19] 開始檢查模組完整性...")

for fname in os.listdir(MODULE_DIR):
    if not fname.endswith(".json"):
        continue
    fpath = os.path.join(MODULE_DIR, fname)
    try:
        with open(fpath, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "name" not in data:
            raise ValueError("缺少必要欄位")
    except Exception as e:
        print(f"[S19] 模組異常：{fname}，原因：{e} → 已刪除")
        os.remove(fpath)
        DELETED += 1

print(f"[S19] 清理完成，共刪除 {DELETED} 筆異常模組")
