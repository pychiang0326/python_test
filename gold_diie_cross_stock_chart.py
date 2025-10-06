import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings

# 过滤掉无害的警告
warnings.filterwarnings("ignore", category=FutureWarning)


# 设置中文字体支持
def set_chinese_font():
    try:
        # 尝试使用系统中已有的中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    except:
        print("警告: 中文字体设置可能不完整，图表中的中文可能无法正常显示")


def simple_stock_analysis():
    # 设置中文字体
    set_chinese_font()

    # 获取数据
    stock_code = "2891.TW"
    #stock_code = "00878.TW"
    years = 10
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    print("正在下载中信金历史数据...")
    try:
        # 明确设置auto_adjust参数以避免警告
        data = yf.download(stock_code, start=start_date, end=end_date, auto_adjust=True)
        print(f"成功下载 {len(data)} 条数据")
    except Exception as e:
        print(f"下载数据时出错: {e}")
        return

    if data.empty:
        print("数据为空")
        return

    # 如果数据是多级列索引，简化列名
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)  # 删除第二级索引（股票代码）

    print(f"数据列: {data.columns.tolist()}")
    print(f"数据前5行:")
    print(data.head())

    # 计算移动平均线
    data['5MA'] = data['Close'].rolling(window=5).mean()
    data['20MA'] = data['Close'].rolling(window=20).mean()
    data = data.dropna()  # 删除NaN值

    # 识别交叉信号
    data['Position'] = 0
    data.loc[data['5MA'] > data['20MA'], 'Position'] = 1
    data['Cross'] = data['Position'].diff()

    buy_signals = data[data['Cross'] == 1]
    sell_signals = data[data['Cross'] == -1]

    # 创建图表
    plt.figure(figsize=(15, 10))

    # 绘制价格和移动平均线
    plt.plot(data.index, data['Close'], label='收盘价', color='black', linewidth=1)
    plt.plot(data.index, data['5MA'], label='5日均线', color='blue', linewidth=1)
    plt.plot(data.index, data['20MA'], label='20日均线', color='red', linewidth=1)

    # 标记买卖信号
    if not buy_signals.empty:
        plt.scatter(buy_signals.index, buy_signals['Low'] * 0.98,
                    marker='^', color='green', s=100, label='黄金交叉 (B)')

    if not sell_signals.empty:
        plt.scatter(sell_signals.index, sell_signals['High'] * 1.02,
                    marker='v', color='red', s=100, label='死亡交叉 (S)')

    # 添加文字标记
    for date, row in buy_signals.iterrows():
        # 使用iloc[0]避免FutureWarning
        low_value = row['Low'] if isinstance(row['Low'], (int, float)) else row['Low'].iloc[0]
        plt.annotate('B', xy=(date, low_value * 0.98), xytext=(0, 10),
                     textcoords='offset points', ha='center', va='bottom',
                     color='green', fontweight='bold')

    for date, row in sell_signals.iterrows():
        # 使用iloc[0]避免FutureWarning
        high_value = row['High'] if isinstance(row['High'], (int, float)) else row['High'].iloc[0]
        plt.annotate('S', xy=(date, high_value * 1.02), xytext=(0, -10),
                     textcoords='offset points', ha='center', va='top',
                     color='red', fontweight='bold')

    #plt.title(f'中信金 (2891.TW) 近10年股价走势 - 移动平均线交叉信号')
    plt.title(f'{stock_code}近{years}年股价走势 - 移动平均线交叉信号')
    plt.xlabel('日期')
    plt.ylabel('价格 (TWD)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # 打印统计信息
    print(f"分析完成!")
    print(f"黄金交叉次数: {len(buy_signals)}")
    print(f"死亡交叉次数: {len(sell_signals)}")
    print(f"数据期间: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")


# 执行函数
if __name__ == "__main__":
    simple_stock_analysis()