# =========================================================================
# ===                  基金数据处理总执行入口 (Master Runner)            ===
# =========================================================================
#
#  如何使用:
#  1. 确认 `config.py` 文件中的配置信息正确无误。
#  2. 运行指令:
#     - 处理所有指数: `python run_all.py`
#     - 只处理纳斯达克: `python run_all.py --index nasdaq`
#     - 只处理标普500:  `python run_all.py -i sp500`
#
#  它会按照以下顺序，为指定的指数基金组 (或所有组)，
#  自动、依次地执行完整的处理流程：
#
#  流程:
#  (1) scraper.py   -> 抓取最新的净值、规模等动态数据。
#  (2) combiner.py  -> 将抓取到的新数据合并到基础数据文件中。
#  (3) reporter.py  -> 基于更新后的数据，生成最终的HTML报告。
#
# =========================================================================

import time
import argparse
from config import CONFIGS
from scraper import scrape_for_config
from combiner import combine_for_config
from reporter import report_for_config

def main():
    """
    主执行函数，根据命令行参数遍历并运行指定或所有配置的完整流程。
    """
    # --- 步骤 1: 设置和解析命令行参数 ---
    parser = argparse.ArgumentParser(description="基金数据处理总执行入口。")
    parser.add_argument(
        '-i', '--index',
        type=str,
        help="指定要处理的指数名称 (例如: 'nasdaq', 'sp500')。如果未提供，则处理所有指数。",
        choices=CONFIGS.keys(), # 确保传入的参数是有效的key
        required=False
    )
    args = parser.parse_args()

    start_time = time.time()
    print("##################################################")
    print("#######      开始执行基金数据处理流程      #######")
    print("##################################################")

    # --- 步骤 2: 决定要处理的目标 ---
    target_configs = {}
    if args.index:
        # 如果指定了单个指数
        print(f"\n模式: 单独处理指数 -> {args.index.upper()}")
        target_configs[args.index] = CONFIGS[args.index]
    else:
        # 如果未指定，则处理所有指数
        print("\n模式: 处理所有已配置的指数")
        target_configs = CONFIGS

    # --- 步骤 3: 遍历并执行任务 ---
    for config_name, config_data in target_configs.items():
        print(f"\n\n========== 处理指数: {config_name.upper()} ==========")
        
        # --- 流程1：执行数据抓取 ---
        scrape_for_config(config_data)
        
        # --- 流程2：执行数据合并 ---
        combine_for_config(config_data)
        
        # --- 流程3：执行报告生成 ---
        report_for_config(config_data)
        
        print(f"========== 指数: {config_name.upper()} 处理完成 ==========")

    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n\n##################################################")
    print("#######      所有指定任务已成功执行完毕！      #######")
    print(f"#######      总耗时: {total_time:.2f} 秒                #######")
    print("##################################################")

if __name__ == '__main__':
    main()