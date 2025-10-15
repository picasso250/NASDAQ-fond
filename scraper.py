# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Identity: 数据工程师-02 (Data Engineer-02)
# Mission:  抓取特定基金的动态数据，并生成一份纯粹、可追溯的TSV报告文件。
#           (模块化版本，由配置驱动)
# Version:  9.0
# Changelog:
#   - v9.0: 重构为可配置的模块化脚本，支持多指数。
# -------------------------------------------------------------------------
import requests
from bs4 import BeautifulSoup
import time
import os
import re
import csv
from config import CONFIGS # <-- 导入中央配置

# --- 全局配置 ---
CACHE_DIR = "cache"
CACHE_EXPIRATION_SECONDS = 3600

# --- 核心函数 (逻辑基本不变) ---
def get_page_html(fund_code: str) -> (str, str):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_filepath = os.path.join(CACHE_DIR, f"{fund_code}.html")

    if os.path.exists(cache_filepath):
        file_mod_time = os.path.getmtime(cache_filepath)
        if (time.time() - file_mod_time) < CACHE_EXPIRATION_SECONDS:
            with open(cache_filepath, 'r', encoding='utf-8') as f:
                return f.read(), 'cache'

    url = f"http://fund.eastmoney.com/{fund_code}.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html_content = response.text
        with open(cache_filepath, 'w', encoding='utf-8') as f: f.write(html_content)
        return html_content, 'network'
    except requests.exceptions.RequestException as e:
        return None, f"网络请求错误: {e}"

def parse_fund_data(html_content: str, expected_name: str, fund_code: str) -> dict:
    data = { "抓取到的标题": "", "近一年": "", "近三年": "", "规模及日期": "", "跟踪信息": "", "错误信息": None }
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        title_tag = soup.find('div', class_='fundDetail-tit')
        if not title_tag:
            data["错误信息"] = "页面结构错误 (未找到标题容器)"
            return data
        
        actual_title_text = title_tag.get_text(strip=True)
        data["抓取到的标题"] = actual_title_text
        
        if fund_code not in actual_title_text or not actual_title_text.startswith(expected_name):
            data["错误信息"] = f"标题校验失败"
            return data

        data_item01 = soup.find('dl', class_='dataItem01')
        if data_item01:
            match = re.search(r"近1年：\s*(-?[\d.]+%?)", data_item01.get_text())
            if match: data["近一年"] = match.group(1)
        
        data_item02 = soup.find('dl', class_='dataItem02')
        if data_item02:
            match = re.search(r"近3年：\s*(-?[\d.]+%?|--)", data_item02.get_text())
            if match: data["近三年"] = match.group(1)

        info_div = soup.find('div', class_='infoOfFund')
        if info_div:
            all_tds = info_div.find_all('td')
            for td in all_tds:
                if '规模' in td.get_text():
                    data['规模及日期'] = td.get_text(strip=True).replace('规模：', '')
                    break
            special_data_td = info_div.find('td', class_='specialData')
            if special_data_td:
                data['跟踪信息'] = special_data_td.get_text(strip=True)
        
        return data
    except Exception as e:
        data["错误信息"] = f"HTML解析时发生未知错误: {e}"
        return data

def scrape_for_config(config: dict):
    """
    根据传入的配置对象，执行抓取任务。
    """
    index_name = config["index_name"]
    output_tsv_file = config["source_file"]
    funds_details = config["funds_details"]
    
    print(f"--- 开始为 '{index_name}' 指数执行数据抓取 ---")
    
    headers = ["基金代码", "基金名称", "抓取到的标题", "近一年", "近三年", "规模及日期", "跟踪信息"]
    
    with open(output_tsv_file, 'w', newline='', encoding='utf-8-sig') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(headers)

        # 从配置中读取基金列表
        for fund_code, alipay_name, tiantian_name in funds_details:
            print(f"\n处理基金: {tiantian_name} ({fund_code})")
            
            html, source_or_error = get_page_html(fund_code)
            
            # 使用天天基金的名称作为写入TSV的“基金名称”列，用于后续匹配
            row_to_write = [fund_code, tiantian_name, '', '', '', '', ''] 
            
            if html:
                # 使用天天基金的名称进行页面校验
                parsed_data = parse_fund_data(html, tiantian_name, fund_code)
                
                row_to_write[2] = parsed_data['抓取到的标题']
                if parsed_data.get("错误信息"):
                    error_msg = parsed_data["错误信息"]
                    print(f"  - [错误] {error_msg}")
                    row_to_write[3] = f"抓取失败: {error_msg}"
                else:
                    print(f"  - [成功] 数据提取完成。")
                    row_to_write = [
                        fund_code,
                        tiantian_name,
                        parsed_data['抓取到的标题'],
                        parsed_data['近一年'],
                        parsed_data['近三年'],
                        parsed_data['规模及日期'],
                        parsed_data['跟踪信息']
                    ]
            else:
                error_msg = source_or_error
                print(f"  - [错误] {error_msg}")
                row_to_write[3] = f"网络错误: {error_msg}"

            writer.writerow(row_to_write)
            print(f"  - [写入] 已将记录写入到 {output_tsv_file}")

            if source_or_error == 'network':
                time.sleep(0.5)
    
    print(f"\n--- '{index_name}' 指数抓取任务执行完毕 ---")
    print(f"报告文件 '{output_tsv_file}' 已生成。")


if __name__ == '__main__':
    print("===== 执行全量数据抓取任务 (v9.0) =====")
    for config_name, config_data in CONFIGS.items():
        scrape_for_config(config_data)
        print("-" * 50)
    print("===== 所有抓取任务已完成 =====")