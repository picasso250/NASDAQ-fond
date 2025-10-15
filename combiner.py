import pandas as pd
from config import CONFIGS

def combine_for_config(config: dict):
    """
    根据传入的配置对象，执行数据合并任务。
    """
    index_name = config["index_name"]
    source_file = config["source_file"]
    target_file = config["target_file"]
    output_file = config["target_file"] # 覆盖原目标文件
    funds_details = config["funds_details"]

    # 从配置动态生成名称映射关系
    # 键 (key): 天天基金名称 (来自 scraped_... or source_file)
    # 值 (value): 支付宝名称 (来自 ..._fund_data or target_file)
    fund_name_mapping = {tiantian: alipay for code, alipay, tiantian in funds_details}

    print(f"--- 开始为 '{index_name}' 指数执行数据合并 ---")

    try:
        source_df = pd.read_csv(source_file, sep='\t', encoding='utf-8')
        target_df = pd.read_csv(target_file, sep='\t', encoding='utf-8')
        print("步骤 1/4: 成功读取源文件和目标文件。")

        # 数据预处理
        # 1. 在源数据中创建映射列，作为后续匹配的“桥梁”
        source_df['target_name'] = source_df['基金名称'].map(fund_name_mapping)
        source_df_mapped = source_df.dropna(subset=['target_name'])
        
        # 2. 准备用于更新的数据
        update_data = source_df_mapped[['target_name', '近一年', '近三年', '规模及日期']].copy()
        update_data.rename(columns={
            '近一年': '一年涨幅(%)',
            '近三年': '三年涨幅(%)',
            '规模及日期': '规模(亿元)'
        }, inplace=True)
        update_data.set_index('target_name', inplace=True)
        
        # 3. 准备目标数据
        target_df.set_index('名称', inplace=True)
        print("步骤 2/4: 数据预处理完成。")

        # 核心数据更新
        target_df.update(update_data)
        target_df.reset_index(inplace=True)
        print("步骤 3/4: 核心数据更新完成。")
        
        # 输出结果
        target_df.to_csv(output_file, sep='\t', encoding='utf-8', index=False)
        print(f"步骤 4/4: 成功将更新后的数据写入到文件: '{output_file}'")
        
        print(f"\n--- '{index_name}' 指数合并任务执行完毕 ---")

    except FileNotFoundError as e:
        print(f"错误：文件未找到 - {e}")
        print("请确认对应的基础数据文件是否存在。")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")

if __name__ == '__main__':
    print("===== 执行全量数据合并任务 =====")
    for config_name, config_data in CONFIGS.items():
        combine_for_config(config_data)
        print("-" * 50)
    print("===== 所有合并任务已完成 =====")