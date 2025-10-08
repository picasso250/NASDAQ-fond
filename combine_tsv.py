import pandas as pd
import io

# --- 计划第一步：环境准备与初始化 ---

# 定义文件名
source_file = 'scraped_fund_details.tsv'
target_file = 'fund.tsv'
output_file = 'fund.tsv' # 输出文件将覆盖原目标文件

# 基金名称映射关系
# 键 (key): scraped_fund_details.tsv 中的基金名称
# 值 (value): fund.tsv 中对应的A类基金名称
fund_name_mapping = {
    "华宝纳斯达克精选股票发起式(QDII)A": "华宝纳斯达克精选股票(QDII)A",
    "广发纳斯达克100ETF联接人民币(QDII)A": "广发纳斯达克100ETF联接(QDII)A",
    "天弘纳斯达克100指数发起(QDII)A": "天弘纳斯达克100指数(QDII)A",
    "博时纳斯达克100ETF发起式联接(QDII)A人民币": "博时纳斯达克100ETF联接(QDII)A",
    "嘉实纳斯达克100ETF发起联接(QDII)A人民币": "嘉实纳斯达克100ETF联接(QDII)A",
    "南方纳斯达克100指数发起(QDII)A": "南方纳斯达克100指数(QDII)A",
    "摩根纳斯达克100指数(QDII)人民币A": "摩根纳斯达克100指数(QDII)A",
    "建信纳斯达克100指数(QDII)A": "建信纳斯达克100指数(QDII)A",
    "易方达纳斯达克100ETF联接(QDII-LOF)A": "易方达纳斯达克100ETF联接(QDII-LOF)A", # <-- 新增映射
}

print("--- 脚本开始执行 ---")

try:
    # --- 计划第二步：加载数据 ---
    
    # 使用UTF-8编码读取TSV文件
    source_df = pd.read_csv(source_file, sep='\t', encoding='utf-8')
    target_df = pd.read_csv(target_file, sep='\t', encoding='utf-8')
    print("步骤 1/5: 成功读取源文件和目标文件。")

    # --- 计划第三步：数据预处理 ---
    
    # 1. 在源数据中创建映射列，作为后续匹配的“桥梁”
    #    我们直接使用 '基金名称' 列进行映射
    source_df['target_name'] = source_df['基金名称'].map(fund_name_mapping)
    
    # 筛选出有有效映射的行，避免空值干扰
    source_df_mapped = source_df.dropna(subset=['target_name'])
    
    # 2. 准备用于更新的数据，并重命名列以匹配目标文件
    update_data = source_df_mapped[['target_name', '近一年', '近三年', '规模及日期']].copy()
    update_data.rename(columns={
        '近一年': '一年涨幅(%)',
        '近三年': '三年涨幅(%)',
        '规模及日期': '规模(亿元)'
    }, inplace=True)
    
    # 将 'target_name' 设置为索引，以便进行高效更新
    update_data.set_index('target_name', inplace=True)
    
    # 3. 将目标DataFrame的'名称'列设置为索引
    target_df.set_index('名称', inplace=True)
    print("步骤 2/5: 数据预处理完成，已准备好用于更新的数据。")

    # --- 计划第四步：核心数据更新 ---
    
    # 使用 update() 方法，这是一个高效且原地修改的操作
    # 它会根据索引（基金名称）自动对齐数据，并用 update_data 中的值更新 target_df
    # 此方法会自动忽略 C 类基金，因为它们在 update_data 的索引中不存在
    target_df.update(update_data)
    
    # 更新完成后，重置索引，使'名称'列回到原来的位置
    target_df.reset_index(inplace=True)
    print("步骤 3/5: 核心数据更新完成，A类基金的相关字段已更新。")
    print("         (C类基金被自动忽略，保持不变)")

    # --- 计划第五步：输出结果 ---
    
    # 将更新后的完整DataFrame保存回原文件
    # index=False 防止写入多余的行号索引
    target_df.to_csv(output_file, sep='\t', encoding='utf-8', index=False)
    print(f"步骤 4/5: 成功将更新后的数据写入到文件: '{output_file}'")
    
    print("\n--- 脚本执行完毕 ---")
    print("更新后的 fund.tsv 内容预览:")
    # 使用 to_string() 来确保所有列都能被打印出来
    print(target_df.to_string())

except FileNotFoundError as e:
    print(f"错误：文件未找到 - {e}")
except Exception as e:
    print(f"执行过程中发生错误: {e}")