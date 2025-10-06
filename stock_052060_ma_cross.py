import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft JhengHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def fix_dataframe_columns(stock_data):
    """
    修复多层列名问题，将MultiIndex转换为单层Index
    """
    # 如果列是MultiIndex，则转换为单层
    if isinstance(stock_data.columns, pd.MultiIndex):
        # 提取第一层作为列名
        stock_data.columns = stock_data.columns.get_level_values(0)
    return stock_data


def calculate_ma_signals(stock_data):
    """
    计算移动平均线和买卖信号
    """
    # 修复列名问题
    df = fix_dataframe_columns(stock_data.copy())

    # 计算移动平均线
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # 初始化持仓状态和信号列表
    holding = False
    buy_signals = []
    sell_signals = []

    # 找出买卖信号
    for i in range(200, len(df)):
        # 使用.iloc确保获取标量值
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        ma60 = df['MA60'].iloc[i]
        ma200 = df['MA200'].iloc[i]

        # 前一天的MA值
        ma5_prev = df['MA5'].iloc[i - 1]
        ma20_prev = df['MA20'].iloc[i - 1]
        ma60_prev = df['MA60'].iloc[i - 1]

        # 计算黄金交叉和死亡交叉
        golden_cross_5_20 = (ma5 > ma20) and (ma5_prev <= ma20_prev)
        death_cross_20_60 = (ma20 < ma60) and (ma20_prev >= ma60_prev)

        # 买入条件：5MA与20MA黄金交叉且在200MA之上且未持仓
        if golden_cross_5_20 and close_price > ma200 and not holding:
            buy_signals.append((date, close_price))
            holding = True

        # 卖出条件：20MA与60MA死亡交叉且已持仓
        elif death_cross_20_60 and holding:
            sell_signals.append((date, close_price))
            holding = False

    return df, buy_signals, sell_signals


def plot_stock_chart(stock_data, buy_signals, sell_signals):
    """
    使用matplotlib绘制股票图表
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [3, 1]})

    # 过滤掉移动平均线的NaN值
    valid_data = stock_data.dropna(subset=['MA5', 'MA20', 'MA60', 'MA200'])

    # 绘制股价和移动平均线
    ax1.plot(valid_data.index, valid_data['Close'], label='收盘价', linewidth=1, color='black')
    ax1.plot(valid_data.index, valid_data['MA5'], label='5MA', linewidth=1, color='purple')
    ax1.plot(valid_data.index, valid_data['MA20'], label='20MA', linewidth=1, color='blue')
    ax1.plot(valid_data.index, valid_data['MA60'], label='60MA', linewidth=1, color='orange')
    ax1.plot(valid_data.index, valid_data['MA200'], label='200MA', linewidth=1.5, color='red')

    # 标记买卖信号
    if buy_signals:
        buy_dates = [signal[0] for signal in buy_signals]
        buy_prices = [signal[1] for signal in buy_signals]
        ax1.scatter(buy_dates, buy_prices, color='green', marker='^', s=100, label='买入(B)', zorder=5)

    if sell_signals:
        sell_dates = [signal[0] for signal in sell_signals]
        sell_prices = [signal[1] for signal in sell_signals]
        ax1.scatter(sell_dates, sell_prices, color='red', marker='v', s=100, label='卖出(S)', zorder=5)

    ax1.set_title('台积电(2330.TW) - 股价与移动平均线', fontsize=16)
    ax1.set_ylabel('价格 (TWD)', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 绘制成交量
    ax2.bar(valid_data.index, valid_data['Volume'], alpha=0.3, color='gray')
    ax2.set_ylabel('成交量', fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    """
    主函数
    """
    # 设置时间范围（近10年）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 10)

    print("正在获取台积电股价数据...")

    try:
        # 获取台积电股价数据（台股代码：2330.TW）
        stock = yf.download('2330.TW', start=start_date, end=end_date, auto_adjust=True)

        if stock.empty:
            print("无法获取数据，请检查网络连接或股票代码")
            return

        print(f"成功获取数据：{len(stock)} 个交易日")

        # 计算移动平均线和信号
        stock_with_ma, buy_signals, sell_signals = calculate_ma_signals(stock)

        # 打印信号统计
        print(f"\n信号统计：")
        print(f"买入信号 (B): {len(buy_signals)} 次")
        print(f"卖出信号 (S): {len(sell_signals)} 次")

        if buy_signals:
            print(f"\n买入信号日期：")
            for date, price in buy_signals:
                print(f"  {date.strftime('%Y-%m-%d')}: {price:.2f} TWD")

        if sell_signals:
            print(f"\n卖出信号日期：")
            for date, price in sell_signals:
                print(f"  {date.strftime('%Y-%m-%d')}: {price:.2f} TWD")

        # 绘制图表
        print("\n正在生成图表...")
        plot_stock_chart(stock_with_ma, buy_signals, sell_signals)

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        print("请检查网络连接或安装必要的库")


if __name__ == "__main__":
    # 安装必要库的提示
    try:
        import yfinance
    except ImportError:
        print("请先安装必要的库：")
        print("pip install yfinance pandas matplotlib")

    main()