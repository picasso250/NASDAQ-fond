import pandas as pd
import os

# --- 计划第一步：环境准备与初始化 ---
INPUT_FILE = 'fund.tsv'
OUTPUT_FILE = 'fund_report.html'

print("--- 开始生成HTML报告 ---")

# --- 计划第二步：定义HTML样式 (CSS) ---
# 这段CSS代码将被内嵌到HTML文件中，使其无需外部文件即可拥有漂亮的样式
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
    # --- 计划第三步：加载数据并生成HTML表格片段 ---
    
    # 检查输入文件是否存在
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"错误：输入文件未找到 -> {INPUT_FILE}")

    # 读取TSV数据
    df = pd.read_csv(INPUT_FILE, sep='\t', encoding='utf-8')
    print(f"步骤 1/4: 成功从 '{INPUT_FILE}' 读取 {len(df)} 条记录。")

    # 将DataFrame转换为HTML表格字符串
    # index=False 避免写入行号
    # classes='fund-table' 用于链接我们的CSS样式
    # border=0 因为我们用CSS来定义更美观的边框
    html_table = df.to_html(index=False, classes='fund-table', border=0)
    print("步骤 2/4: 已将数据转换为HTML表格格式。")

    # --- 计划第四步：组装完整的HTML文档 ---

    # 创建一个包含占位符的完整HTML文档模板
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
    print("步骤 3/4: 已将CSS样式和HTML表格组装成完整文档。")

    # --- 计划第五步：写入文件并完成 ---

    # 使用UTF-8编码将完整的HTML内容写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(full_html_content)
    
    # 获取生成文件的绝对路径以便用户点击
    absolute_path = os.path.abspath(OUTPUT_FILE)
    print(f"步骤 4/4: HTML报告已成功生成！")
    print(f"--> 文件位置: file://{absolute_path}")
    print("\n--- 任务完成 ---")

except FileNotFoundError as e:
    print(f"\n操作失败: {e}")
except Exception as e:
    print(f"\n执行过程中发生未知错误: {e}")