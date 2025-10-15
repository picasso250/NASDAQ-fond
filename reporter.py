import pandas as pd
import os
from config import CONFIGS

def report_for_config(config: dict):
    """
    根据传入的配置对象，生成HTML报告。
    """
    input_file = config["target_file"]
    output_file = config["output_report_file"]
    report_title = config["report_title"]
    index_name = config["index_name"]

    print(f"--- 开始为 '{index_name}' 指数生成HTML报告 ---")

    CSS_STYLES = """
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 14px; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
    h1 { color: #2c5e2e; text-align: center; margin-bottom: 25px; }
    .table-container { overflow-x: auto; }
    .fund-table { width: 95%; margin: 0 auto; border-collapse: collapse; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); background-color: #ffffff; }
    .fund-table th, .fund-table td { padding: 12px 15px; border: 1px solid #ddd; text-align: left; }
    .fund-table th { background-color: #347a38; color: #ffffff; font-weight: bold; text-align: center; }
    .fund-table tr:nth-child(even) { background-color: #f9f9f9; }
    .fund-table tr:hover { background-color: #e8f5e9; cursor: pointer; }
    """

    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"错误：输入文件未找到 -> {input_file}")

        df = pd.read_csv(input_file, sep='\t', encoding='utf-8')
        print(f"步骤 1/6: 成功从 '{input_file}' 读取 {len(df)} 条记录。")

        if '规模(亿元)' in df.columns:
            df['规模(亿元)'] = df['规模(亿元)'].astype(str).str.split('（').str[0]
            print("步骤 2/6: 已清理'规模(亿元)'列。")

        if '买入费率(%)' in df.columns:
            df['买入费率(%)'] = df['买入费率(%)'].astype(str) + '%'
            print("步骤 3/6: 已格式化'买入费率'列。")
        
        if '运作费率(年，%)' in df.columns:
            df['运作费率(年，%)'] = df['运作费率(年，%)'].astype(str) + '%'
            print("步骤 4/6: 已格式化'运作费率'列。")

        rename_mapping = {
            '一年涨幅(%)': '一年涨幅', '三年涨幅(%)': '三年涨幅', '规模(亿元)': '规模',
            '买入费率(%)': '买入费率', '运作费率(年，%)': '运作费率', '零成本持有天数': '天数'
        }
        df.rename(columns=rename_mapping, inplace=True)
        print("步骤 5/6: 已更新表格标题。")

        html_table = df.to_html(index=False, classes='fund-table', border=0)
        print("步骤 6/6: 已将数据转换为HTML表格。")

        full_html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_title}</title>
    <style>{CSS_STYLES}</style>
</head>
<body>
    <h1>{report_title}</h1>
    <div class="table-container">{html_table}</div>
</body>
</html>
"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html_content)
        
        absolute_path = os.path.abspath(output_file)
        print(f"\nHTML报告已成功生成！")
        print(f"--> 文件位置: file://{absolute_path}")
        print(f"\n--- '{index_name}' 指数报告任务完成 ---")

    except FileNotFoundError as e:
        print(f"\n操作失败: {e}")
    except Exception as e:
        print(f"\n执行过程中发生未知错误: {e}")

if __name__ == '__main__':
    print("===== 执行全量HTML报告生成任务 =====")
    for config_name, config_data in CONFIGS.items():
        report_for_config(config_data)
        print("-" * 50)
    print("===== 所有报告生成任务已完成 =====")