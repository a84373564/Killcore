#!/bin/bash

# Killcore v08｜最終版掛機巡邏流程（整合 S19、自我修復、防呆再強化）

KILLCORE_LOG="/mnt/data/killcore/logs/killcore.log"
LOCKFILE="/tmp/killcore_v08.lock"
SYMBOL_POOL="/mnt/data/killcore/symbol_pool.json"

mkdir -p "$(dirname "$KILLCORE_LOG")"

log() {
    echo "[v08] $(date '+%Y-%m-%d %H:%M:%S') $1" >> "$KILLCORE_LOG"
}

# 防呆 1：已有背景巡邏進程存在，禁止重複啟動
if [ -f "$LOCKFILE" ]; then
    PID=$(cat "$LOCKFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "[v08] 檢測到已有掛機進程 (PID $PID)，本次不再重啟。"
        exit 1
    else
        echo "[v08] lock 存在但無對應進程，清除 lock。"
        rm -f "$LOCKFILE"
    fi
fi

# 寫入當前腳本 PID
echo $$ > "$LOCKFILE"

# 防呆 2：錯誤時自我重啟
trap 'log "異常中止，重啟掛機流程"; exec $0' ERR

while true; do
    log "==== 新一輪 Killcore Omega 進化流程開始 ===="

    # === S16：建構幣池 ===
    python3 /mnt/data/killcore/symbol_pool_builder.py

    # 防呆 3：幣池存在且非空
    if [ ! -f "$SYMBOL_POOL" ] || ! grep -q '[A-Z]USDT' "$SYMBOL_POOL"; then
        log "[v08] 幣池為空，略過此輪流程"
        sleep 60
        continue
    fi

    # === S17：評估強幣排行 ===
    python3 /mnt/data/killcore/symbol_rank_evaluator.py

    # === S18：過濾黑名單 ===
    python3 /mnt/data/killcore/dead_symbol_filter.py

    # === v01：生成模組 ===
    python3 /mnt/data/killcore/v01_strategy_generator.py

    # === S19：清理異常模組（防止卡死）===
    python3 /mnt/data/killcore/module_integrity_checker.py

    # === v02～v07 主流程 ===
    python3 /mnt/data/killcore/v02_price_generator.py
    python3 /mnt/data/killcore/v03_sandbox_engine.py
    python3 /mnt/data/killcore/v04_evaluation_ruleset.py
    python3 /mnt/data/killcore/v05_core_engine.py
    python3 /mnt/data/killcore/v06_memory_bank.py
    python3 /mnt/data/killcore/v07_king_pool.py

    log "==== 本輪演化完成，等待下輪 ===="
    sleep 60
done
