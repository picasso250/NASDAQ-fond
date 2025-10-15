# =========================================================================
# ===                  基金数据处理总执行入口 (Master Runner)            ===
# =========================================================================
#
#  如何使用:
#  1. 确认 `config.py` 文件中的配置信息正确无误。
#  2. 直接运行此脚本: `python run_all.py`
#
#  它会按照以下顺序，为配置文件中定义的每一个指数基金组，
#  自动、依次地执行完整的处理流程：
#
#  流程:
#  (1) scraper.py   -> 抓取最新的净值、规模等动态数据。
#  (2) combiner.py  -> 将抓取到的新数据合并到基础数据文件中。
#  (3) reporter.py  -> 基于更新后的数据，生成最终的HTML报告。
#
# =========================================================================

import time
from config import CONFIGS
from scraper import scrape_for_config
from combiner import combine_for_config
from reporter import report_for_config

def main():
    """
    主执行函数，遍历所有配置并运行完整流程。
    """
    start_time = time.time()
    print("##################################################")
    print("#######      开始执行全量基金数据处理流程      #######")
    print("##################################################")
    
    # 遍历在 config.py 中定义的所有配置项
    for config_name, config_data in CONFIGS.items():
        print(f"\n\n========== 处理指数: {config_name.upper()} ==========")
        
        # --- 第1步：执行数据抓取 ---
        scrape_for_config(config_data)
        
        # --- 第2步：执行数据合并 ---
        combine_for_config(config_data)
        
        # --- 第3步：执行报告生成 ---
        report_for_config(config_data)
        
        print(f"========== 指数: {config_name.upper()} 处理完成 ==========")

    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n\n##################################################")
    print("#######      所有任务已成功执行完毕！      #######")
    print(f"#######      总耗时: {total_time:.2f} 秒                #######")
    print("##################################################")


if __name__ == '__main__':
    main()