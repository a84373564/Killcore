#!/bin/bash

# Killcore v08｜背景掛機巡邏守護版（防重啟、防多開、穩定巡邏）

KILLCORE_LOG="/mnt/data/killcore/logs/killcore.log"
LOCKFILE="/tmp/killcore_v08.lock"

mkdir -p "$(dirname "$KILLCORE_LOG")"

log() {
    echo "[v08] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$KILLCORE_LOG"
}

# 防呆 1：已有背景巡邏進行中，禁止重複啟動
if [ -f "$LOCKFILE" ] && kill -0 "$(cat $LOCKFILE)" 2>/dev/null; then
    echo "[v08] 檢測到已有掛機進程 (PID $(cat $LOCKFILE))，本次不再重啟。"
    exit 1
fi

# 寫入目前腳本 PID
echo $$ > "$LOCKFILE"

# 防呆 2：發生錯誤時自我重啟
trap 'log "異常中止，重啟掛機巡邏"; exec $0' ERR

while true; do
    log "==== 開始新一輪 Killcore 進化流程 ===="

    python3 /mnt/data/killcore/v01_strategy_generator.py
    python3 /mnt/data/killcore/v02_price_generator.py
    python3 /mnt/data/killcore/v03_sandbox_engine.py
    python3 /mnt/data/killcore/v04_evaluation_ruleset.py
    python3 /mnt/data/killcore/v05_core_engine.py
    python3 /mnt/data/killcore/v06_memory_bank.py
    python3 /mnt/data/killcore/v07_king_pool.py

    log "==== 本輪完成，休息 60 秒 ===="
    sleep 60
done
