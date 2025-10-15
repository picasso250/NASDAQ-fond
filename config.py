# FILE: config.py
# V2 - 项目“控制中心”，采用更优化的配置结构

# 定义基金详细信息的结构：
# 每个元素是一个元组 (Tuple):
# (基金代码, 最终报告显示的名称 (支付宝名称), 抓取源的名称 (天天基金名称))

# --- 纳斯达克100基金配置 ---
NASDAQ_FUNDS = [
    ("017436", "华宝纳斯达克精选股票(QDII)A", "华宝纳斯达克精选股票发起式(QDII)A"),
    ("270042", "广发纳斯达克100ETF联接(QDII)A", "广发纳斯达克100ETF联接人民币(QDII)A"),
    ("018043", "天弘纳斯达克100指数(QDII)A", "天弘纳斯达克100指数发起(QDII)A"),
    ("016055", "博时纳斯达克100ETF联接(QDII)A", "博时纳斯达克100ETF发起式联接(QDII)A人民币"),
    ("016532", "嘉实纳斯达克100ETF联接(QDII)A", "嘉实纳斯达克100ETF发起联接(QDII)A人民币"),
    ("016452", "南方纳斯达克100指数(QDII)A", "南方纳斯达克100指数发起(QDII)A"),
    ("019172", "摩根纳斯达克100指数(QDII)A", "摩根纳斯达克100指数(QDII)人民币A"),
    ("539001", "建信纳斯达克100指数(QDII)A", "建信纳斯达克100指数(QDII)A"),
    ("161130", "易方达纳斯达克100ETF联接(QDII-LOF)A", "易方达纳斯达克100ETF联接(QDII-LOF)A"),
]

# --- 标普500基金配置 ---
SP500_FUNDS = [
    ("017028", "国泰标普500ETF发起联接(QDII)A", "国泰标普500ETF发起联接(QDII)A人民币"),
    ("007721", "天弘标普500(QDII-FOF)A", "天弘标普500发起(QDII-FOF)A"),
    ("018064", "华夏标普500ETF联接(QDII)A", "华夏标普500ETF发起式联接(QDII)A"),
    ("017641", "摩根标普500指数(QDII)A", "摩根纳斯达克100指数(QDII)人民币A"),
    ("096001", "大成标普500等权重指数(QDII)A", "大成标普500等权重指数(QDII)A人民币"),
]

# --- 整合为统一的配置对象 ---
CONFIGS = {
    "nasdaq": {
        "index_name": "nasdaq",
        "report_title": "纳斯达克100基金数据每日报告",
        "funds_details": NASDAQ_FUNDS,
        "source_file": "nasdaq_scraped_details.tsv", # 抓取数据的输出文件
        "target_file": "nasdaq_fund_data.tsv",      # 手动维护的核心数据文件
        "output_report_file": "nasdaq_report.html"  # 最终生成的HTML报告
    },
    "sp500": {
        "index_name": "sp500",
        "report_title": "标普500基金数据每日报告",
        "funds_details": SP500_FUNDS,
        "source_file": "sp500_scraped_details.tsv",
        "target_file": "sp500_fund_data.tsv",
        "output_report_file": "sp500_report.html"
    }
}