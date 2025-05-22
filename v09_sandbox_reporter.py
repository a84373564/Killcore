import json
import os
from termcolor import colored

KING_PATH = "/mnt/data/killcore/v07_king_pool.json"

def load_king_data(path=KING_PATH):
    if not os.path.exists(path):
        print(colored("[v09] 錯誤：找不到王者封存檔案。", "red"))
        return None

    with open(path, "r") as f:
        return json.load(f)

def print_king_report(data):
    print("\n========== 王者績效報表 ==========\n")
    print(f"策略名稱    ：{data.get('name')} ({data.get('strategy_label')})")
    print(f"類型        ：{data.get('strategy_name')}")
    print(f"參數        ：{data.get('parameters')}")
    print(f"是否重生者  ：{'是' if data.get('from_retry') else '否'}")
    print(f"策略標籤    ：{data.get('strategy_tag')}")

    print("\n---------- 績效指標 ----------")

    sharpe = data.get("sharpe", 0)
    profit = data.get("profit", 0)
    drawdown = data.get("drawdown", 0)
    survival = data.get("survival_rounds", 1)

    if sharpe > 5 or survival > 10:
        print(colored(f"Sharpe Ratio ：{sharpe}", "red"))
    else:
        print(f"Sharpe Ratio ：{sharpe}")

    print(f"總獲利       ：{profit}")
    print(f"最大回撤     ：{drawdown}")
    print(f"存活輪數     ：{survival}")
    print(f"策略指紋     ：{data.get('signature')}")
    print("\n===============================\n")

def main():
    king = load_king_data()
    if king:
        print_king_report(king)

if __name__ == "__main__":
    main()
