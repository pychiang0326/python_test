# 安裝必要套件
# !pip install yfinance mplfinance pandas --upgrade

import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib as mpl
import shutil
import os

# ==== 强制中文字体配置 ====
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows系统
plt.rcParams['axes.unicode_minus'] = False

# ==== 手动清除字体缓存 ====
cache_dir = mpl.get_cachedir()
if os.path.exists(cache_dir):
    try:
        shutil.rmtree(cache_dir)
        print(f"已清除matplotlib缓存目录: {cache_dir}")
    except Exception as e:
        print(f"缓存清除失败: {str(e)}")

# ==== 数据获取 ====
STOCK_CODE = "2330.TW"
tsmc = yf.download(
    STOCK_CODE,
    start="2005-02-01",
    end='2025-02-21',
    auto_adjust=False,
    progress=False,
    timeout=10
)

# 列名标准化
tsmc.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']

# 季度重采样
quarterly = tsmc.resample('QE').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# 自定义样式（强制指定字体）
style = mpf.make_mpf_style(
    base_mpf_style='yahoo',
    facecolor='#fafafa',
    gridcolor='#e0e0e0',
    rc={'font.family': 'Microsoft YaHei'}
)

# 绘制图表
mpf.plot(
    quarterly,
    type='candle',
    style=style,
    title=f'台积电 ({STOCK_CODE}) 季K线图',
    ylabel='价格 (TWD)',
    volume=True,
    ylabel_lower='成交量',
    figratio=(12, 6),
    returnfig=True,
    update_width_config=dict(candle_linewidth=0.7)
)

# 显示图表
plt.subplots_adjust(bottom=0.2)
plt.show()