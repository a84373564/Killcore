#!/bin/bash

# Killcore v08 最終無敵版｜背景自動巡邏流程

KILLCORE_LOG="/mnt/data/killcore/logs/killcore.log"
mkdir -p "$(dirname "$KILLCORE_LOG")"

log() {
    echo "[v08] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$KILLCORE_LOG"
}

while true; do
    log "==== 開始新一輪 Killcore 進化流程 ===="

    # 執行 v01～v07 全流程
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
