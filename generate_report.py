import pandas as pd
import os

# --- 计划第一步：环境准备与初始化 ---
INPUT_FILE = 'fund.tsv'
OUTPUT_FILE = 'fund_report.html'

print("--- 开始生成HTML报告 ---")

# --- 计划第二步：定义HTML样式 (CSS) ---
# (CSS样式保持不变)
CSS_STYLES = """
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 14px;
        background-color: #f4f7f6;
        color: #333;
        margin: 0;
        padding: 20px;
    }
    h1 {
        color: #2c5e2e; /* A professional green */
        text-align: center;
        margin-bottom: 25px;
    }
    .table-container {
        overflow-x: auto; /* Adds horizontal scroll for small screens */
    }
    .fund-table {
        width: 95%;
        margin: 0 auto;
        border-collapse: collapse;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        background-color: #ffffff;
    }
    .fund-table th, .fund-table td {
        padding: 12px 15px;
        border: 1px solid #ddd;
        text-align: left;
    }
    .fund-table th {
        background-color: #347a38; /* A darker, professional green */
        color: #ffffff;
        font-weight: bold;
        text-align: center;
    }
    .fund-table tr:nth-child(even) {
        background-color: #f9f9f9; /* Zebra striping for readability */
    }
    .fund-table tr:hover {
        background-color: #e8f5e9; /* Highlight row on hover */
        cursor: pointer;
    }
"""

try:
    # --- 计划第三步：加载数据并进行格式化 ---
    
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"错误：输入文件未找到 -> {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE, sep='\t', encoding='utf-8')
    print(f"步骤 1/6: 成功从 '{INPUT_FILE}' 读取 {len(df)} 条记录。")

    # 1. 清理“规模(亿元)”列的数据，去除括号及内部内容
    if '规模(亿元)' in df.columns:
        df['规模(亿元)'] = df['规模(亿元)'].astype(str).str.split('（').str[0]
        print("步骤 2/6: 已清理'规模(亿元)'列的数据格式。")

    # 2. 将费率列的 '%' 添加到数据中
    if '买入费率(%)' in df.columns:
        df['买入费率(%)'] = df['买入费率(%)'].astype(str) + '%'
        print("步骤 3/6: 已将'%'符号添加到'买入费率'数据中。")
    
    if '运作费率(年，%)' in df.columns:
        df['运作费率(年，%)'] = df['运作费率(年，%)'].astype(str) + '%'
        print("步骤 4/6: 已将'%'符号添加到'运作费率'数据中。")

    # 3. 统一重命名所有需要修改的列标题
    rename_mapping = {
        '一年涨幅(%)': '一年涨幅',
        '三年涨幅(%)': '三年涨幅',
        '规模(亿元)': '规模',
        '买入费率(%)': '买入费率',
        '运作费率(年，%)': '运作费率(年)',
        '零成本持有天数': '卖出天数'
    }
    df.rename(columns=rename_mapping, inplace=True)
    print("步骤 5/6: 已根据要求更新所有表格标题。")

    # --- 计划第四步：生成HTML表格片段 ---
    html_table = df.to_html(index=False, classes='fund-table', border=0)
    print("步骤 6/6: 已将格式化后的数据转换为HTML表格。")

    # --- 计划第五步：组装完整的HTML文档 ---
    full_html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>基金数据报告</title>
    <style>
        {CSS_STYLES}
    </style>
</head>
<body>

    <h1>基金数据每日报告</h1>
    
    <div class="table-container">
        {html_table}
    </div>

</body>
</html>
"""

    # --- 计划第六步：写入文件并完成 ---
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_html_content)
    
    absolute_path = os.path.abspath(OUTPUT_FILE)
    print(f"\nHTML报告已成功生成并更新！")
    print(f"--> 文件位置: file://{absolute_path}")
    print("\n--- 任务完成 ---")

except FileNotFoundError as e:
    print(f"\n操作失败: {e}")
except Exception as e:
    print(f"\n执行过程中发生未知错误: {e}")