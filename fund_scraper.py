# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Identity: 数据工程师-01 (Data Engineer-01)
# Mission:  抓取特定基金的动态数据，并生成一份纯粹、可追溯的TSV报告文件。
# Version:  8.0
# Changelog:
#   - v8.0: 遵照舰长最终指令进行精炼。
#   - v8.0: 1. 【新增】增加“抓取到的标题”列，用于数据校验与追溯。
#   - v8.0: 2. 【修正】将列名“一年涨幅”等修正为“近一年”，与源文案严格一致。
#   - v7.0: 回归纯粹的数据抓取与导出任务。
# -------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
import time
import os
import re
import csv

# --- 全局配置 ---
TARGET_FUNDS = {
    "017436": "华宝纳斯达克精选股票发起式(QDII)A",
    "270042": "广发纳斯达克100ETF联接人民币(QDII)A",
    "018043": "天弘纳斯达克100指数发起(QDII)A",
    "016055": "博时纳斯达克100ETF发起式联接(QDII)A人民币",
    "016532": "嘉实纳斯达克100ETF发起联接(QDII)A人民币",
    "016452": "南方纳斯达克100指数发起(QDII)A",
    "019172": "摩根纳斯达克100指数(QDII)人民币A",
    "539001": "建信纳斯达克100指数(QDII)A",
    "161130": "易方达纳斯达克100ETF联接(QDII-LOF)A", # <-- 新增基金
}

CACHE_DIR = "cache"
CACHE_EXPIRATION_SECONDS = 3600
OUTPUT_TSV_FILE = "scraped_fund_details.tsv"

def get_page_html(fund_code: str) -> (str, str):
    """
    获取基金页面的HTML内容，优先从缓存读取。（逻辑保持不变）
    """
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
    """
    v8.0 解析逻辑：提取所有需要的动态数据，包括原始标题。
    """
    data = {
        "抓取到的标题": "",
        "近一年": "",
        "近三年": "",
        "规模及日期": "",
        "跟踪信息": "",
        "错误信息": None
    }
    try:
        soup = BeautifulSoup(html_content, 'lxml')

        # 第一步：提取并校验标题
        title_tag = soup.find('div', class_='fundDetail-tit')
        if not title_tag:
            data["错误信息"] = "页面结构错误 (未找到标题容器)"
            return data
        
        actual_title_text = title_tag.get_text(strip=True)
        data["抓取到的标题"] = actual_title_text # 无论校验成功与否，都记录下来
        
        if fund_code not in actual_title_text or not actual_title_text.startswith(expected_name):
            data["错误信息"] = f"标题校验失败" # 简化错误信息，因为标题本身已被记录
            return data

        # 第二步：提取“近一年”和“近三年”
        data_item01 = soup.find('dl', class_='dataItem01')
        if data_item01:
            match = re.search(r"近1年：\s*(-?[\d.]+%?)", data_item01.get_text())
            if match: data["近一年"] = match.group(1)
        
        data_item02 = soup.find('dl', class_='dataItem02')
        if data_item02:
            match = re.search(r"近3年：\s*(-?[\d.]+%?|--)", data_item02.get_text())
            if match: data["近三年"] = match.group(1)

        # 第三步：提取“规模及日期”和“跟踪信息”
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

if __name__ == '__main__':
    print("--- 开始执行数据抓取与导出任务 (v8.0) ---")
    
    # 【已更新】定义TSV文件的表头
    headers = ["基金代码", "基金名称", "抓取到的标题", "近一年", "近三年", "规模及日期", "跟踪信息"]
    
    with open(OUTPUT_TSV_FILE, 'w', newline='', encoding='utf-8-sig') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerow(headers)

        for code, name in TARGET_FUNDS.items():
            print(f"\n处理基金: {name} ({code})")
            
            html, source_or_error = get_page_html(code)
            
            # 【已更新】初始化一行数据以匹配新的列数
            row_to_write = [code, name, '', '', '', '', ''] 
            
            if html:
                parsed_data = parse_fund_data(html, name, code)
                
                # 总是先填充抓取到的标题，即使后续有错误
                row_to_write[2] = parsed_data['抓取到的标题']

                if parsed_data.get("错误信息"):
                    error_msg = parsed_data["错误信息"]
                    print(f"  - [错误] {error_msg}")
                    # 将错误信息填入第一个数据列
                    row_to_write[3] = f"抓取失败: {error_msg}"
                else:
                    print(f"  - [成功] 数据提取完成。")
                    # 【已更新】按新顺序填充数据行
                    row_to_write = [
                        code,
                        name,
                        parsed_data['抓取到的标题'],
                        parsed_data['近一年'],
                        parsed_data['近三年'],
                        parsed_data['规模及日期'],
                        parsed_data['跟踪信息']
                    ]
            else: # 网络请求失败
                error_msg = source_or_error
                print(f"  - [错误] {error_msg}")
                row_to_write[3] = f"网络错误: {error_msg}"

            writer.writerow(row_to_write)
            print(f"  - [写入] 已将记录写入到 {OUTPUT_TSV_FILE}")

            if source_or_error == 'network':
                time.sleep(0.5)
        
    print(f"\n--- 任务执行完毕 ---")
    print(f"报告文件 '{OUTPUT_TSV_FILE}' 已在当前目录生成。")