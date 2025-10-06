import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

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


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    计算MACD指标
    """
    # 计算快慢EMA
    fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()

    # 计算MACD线和信号线
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    macd_histogram = macd_line - signal_line

    return macd_line, signal_line, macd_histogram


def calculate_rsi(data, period=14):
    """
    计算RSI指标
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_technical_indicators(stock_data):
    """
    计算所有技术指标
    """
    # 修复列名问题
    df = fix_dataframe_columns(stock_data.copy())

    # 计算移动平均线
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    # 计算MACD
    df['MACD'], df['MACD_Signal'], df['MACD_Histogram'] = calculate_macd(df)

    # 计算RSI
    df['RSI'] = calculate_rsi(df)

    # 计算成交量均线（用于成交量确认）
    df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()

    return df


def optimized_ma_signals(stock_data):
    """
    优化后的移动平均线信号，使用改进的MACD和RSI过滤条件
    """
    # 计算技术指标
    df = calculate_technical_indicators(stock_data)

    # 初始化持仓状态和信号列表
    holding = False
    buy_signals = []
    sell_signals = []
    signal_details = []  # 存储信号详情用于分析

    # 找出买卖信号
    for i in range(200, len(df)):
        # 使用.iloc确保获取标量值
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        ma60 = df['MA60'].iloc[i]
        ma200 = df['MA200'].iloc[i]
        macd = df['MACD'].iloc[i]
        macd_signal = df['MACD_Signal'].iloc[i]
        macd_histogram = df['MACD_Histogram'].iloc[i]
        rsi = df['RSI'].iloc[i]
        volume = df['Volume'].iloc[i]
        volume_ma20 = df['Volume_MA20'].iloc[i]

        # 前一天的MA值
        ma5_prev = df['MA5'].iloc[i - 1]
        ma20_prev = df['MA20'].iloc[i - 1]
        ma60_prev = df['MA60'].iloc[i - 1]

        # 计算黄金交叉和死亡交叉
        golden_cross_5_20 = (ma5 > ma20) and (ma5_prev <= ma20_prev)
        death_cross_20_60 = (ma20 < ma60) and (ma20_prev >= ma60_prev)

        # ========== 优化后的过滤条件 ==========

        # 1. MACD条件优化：更宽松但有效的条件
        # - MACD在零轴上方或刚刚金叉
        # - 或者MACD柱状图正在改善（当前值大于前一天）
        macd_prev = df['MACD'].iloc[i - 1] if i > 0 else 0
        macd_signal_prev = df['MACD_Signal'].iloc[i - 1] if i > 0 else 0
        macd_histogram_prev = df['MACD_Histogram'].iloc[i - 1] if i > 0 else 0

        macd_golden_cross = (macd > macd_signal) and (macd_prev <= macd_signal_prev)
        macd_improving = macd_histogram > macd_histogram_prev

        # 优化后的MACD条件：允许在零轴附近且趋势向上
        macd_optimized = (macd > -0.5) and (macd_improving or macd_golden_cross or macd > 0)

        # 2. RSI条件优化：动态调整阈值
        # - 在强势市场中允许更高的RSI
        # - 考虑价格相对200MA的位置来调整RSI阈值
        price_vs_200ma = (close_price - ma200) / ma200 * 100

        if price_vs_200ma > 20:  # 远高于200MA，强势市场
            rsi_min, rsi_max = 40, 80  # 允许更高的RSI
        elif price_vs_200ma > 10:  # 中等强势
            rsi_min, rsi_max = 35, 78
        elif price_vs_200ma > -5:  # 正常范围
            rsi_min, rsi_max = 30, 75
        else:  # 弱势市场
            rsi_min, rsi_max = 25, 70

        rsi_optimized = (rsi > rsi_min) and (rsi < rsi_max)

        # 3. 成交量确认：突破时成交量放大
        volume_confirm = volume > volume_ma20 * 0.8  # 成交量不低于均线的80%

        # 买入条件：5MA与20MA黄金交叉且在200MA之上 + 优化后的过滤条件 + 未持仓
        if (golden_cross_5_20 and close_price > ma200 and
                macd_optimized and rsi_optimized and volume_confirm and not holding):

            buy_signals.append((date, close_price))
            holding = True

            # 记录信号详情
            signal_details.append({
                'date': date,
                'type': 'BUY',
                'price': close_price,
                'ma5': ma5,
                'ma20': ma20,
                'ma200': ma200,
                'macd': macd,
                'macd_signal': macd_signal,
                'rsi': rsi,
                'volume_ratio': volume / volume_ma20,
                'price_vs_200ma': price_vs_200ma
            })

        # 卖出条件：20MA与60MA死亡交叉且已持仓
        elif death_cross_20_60 and holding:
            sell_signals.append((date, close_price))
            holding = False

            # 记录信号详情
            signal_details.append({
                'date': date,
                'type': 'SELL',
                'price': close_price,
                'ma20': ma20,
                'ma60': ma60
            })

    return df, buy_signals, sell_signals, signal_details


def backtest_analysis(buy_signals, sell_signals, signal_details=None):
    """
    回测分析和统计
    """
    print("\n" + "=" * 50)
    print("回测统计分析")
    print("=" * 50)

    # 确保买卖信号数量匹配
    min_signals = min(len(buy_signals), len(sell_signals))
    buy_signals = buy_signals[:min_signals]
    sell_signals = sell_signals[:min_signals]

    if min_signals == 0:
        print("没有完整的交易对进行回测分析")
        return

    # 计算每笔交易的收益率
    trades = []
    total_return = 1.0
    cumulative_returns = []

    for i in range(min_signals):
        buy_date, buy_price = buy_signals[i]
        sell_date, sell_price = sell_signals[i]

        # 计算持有期和收益率
        holding_days = (sell_date - buy_date).days
        return_rate = (sell_price - buy_price) / buy_price * 100
        profit = sell_price - buy_price

        trade_info = {
            '序号': i + 1,
            '买入日期': buy_date.strftime('%Y-%m-%d'),
            '买入价格': buy_price,
            '卖出日期': sell_date.strftime('%Y-%m-%d'),
            '卖出价格': sell_price,
            '持有天数': holding_days,
            '收益率%': return_rate,
            '盈亏金额': profit
        }
        trades.append(trade_info)

        # 计算累计收益率
        total_return *= (1 + return_rate / 100)
        cumulative_returns.append((total_return - 1) * 100)

    # 计算统计指标
    returns = [trade['收益率%'] for trade in trades]
    profits = [trade['盈亏金额'] for trade in trades]
    holding_periods = [trade['持有天数'] for trade in trades]

    # 基本统计
    total_trades = len(trades)
    winning_trades = len([r for r in returns if r > 0])
    losing_trades = len([r for r in returns if r < 0])
    win_rate = winning_trades / total_trades * 100

    avg_return = np.mean(returns)
    max_return = np.max(returns)
    min_return = np.min(returns)

    total_profit = sum(profits)
    avg_profit = np.mean(profits)

    avg_holding_days = np.mean(holding_periods)

    # 年化收益率（假设平均每年有250个交易日）
    first_buy_date = datetime.strptime(trades[0]['买入日期'], '%Y-%m-%d')
    last_sell_date = datetime.strptime(trades[-1]['卖出日期'], '%Y-%m-%d')
    total_days = (last_sell_date - first_buy_date).days
    total_years = total_days / 365.25

    annualized_return = (total_return ** (1 / total_years) - 1) * 100 if total_years > 0 else 0

    # 最大回撤计算
    equity_curve = [1.0]  # 初始资金为1
    for ret in returns:
        equity_curve.append(equity_curve[-1] * (1 + ret / 100))

    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - running_max) / running_max * 100
    max_drawdown = np.min(drawdowns)

    # 打印详细交易记录
    print(f"\n详细交易记录 (共{total_trades}笔交易):")
    print("-" * 120)
    print(
        f"{'序号':<4} {'买入日期':<12} {'买入价':<8} {'卖出日期':<12} {'卖出价':<8} {'持有天数':<8} {'收益率%':<10} {'盈亏金额':<10}")
    print("-" * 120)

    for trade in trades:
        color = '\033[92m' if trade['收益率%'] > 0 else '\033[91m'  # 绿色表示盈利，红色表示亏损
        reset = '\033[0m'
        print(f"{trade['序号']:<4} {trade['买入日期']:<12} {trade['买入价格']:<8.2f} "
              f"{trade['卖出日期']:<12} {trade['卖出价格']:<8.2f} {trade['持有天数']:<8} "
              f"{color}{trade['收益率%']:<10.2f}{reset} {color}{trade['盈亏金额']:<10.2f}{reset}")

    # 打印统计摘要
    print("\n" + "=" * 50)
    print("回测统计摘要")
    print("=" * 50)
    print(f"总交易次数: {total_trades}")
    print(f"盈利交易: {winning_trades}次")
    print(f"亏损交易: {losing_trades}次")
    print(f"胜率: {win_rate:.2f}%")
    print(f"平均持有天数: {avg_holding_days:.1f}天")
    print(f"单次交易平均收益率: {avg_return:.2f}%")
    print(f"最佳单次收益率: {max_return:.2f}%")
    print(f"最差单次收益率: {min_return:.2f}%")
    print(f"累计总收益率: {(total_return - 1) * 100:.2f}%")
    print(f"年化收益率: {annualized_return:.2f}%")
    print(f"总盈亏金额: {total_profit:.2f} TWD")
    print(f"平均每笔盈亏: {avg_profit:.2f} TWD")
    print(f"最大回撤: {max_drawdown:.2f}%")

    # 打印过滤条件效果
    if signal_details:
        print("\n" + "=" * 50)
        print("过滤条件效果分析")
        print("=" * 50)
        buy_signals_count = len([s for s in signal_details if s['type'] == 'BUY'])
        print(f"优化后买入信号数量: {buy_signals_count}")

        # 分析RSI动态阈值效果
        rsi_ranges = {}
        for signal in signal_details:
            if signal['type'] == 'BUY':
                rsi_range = f"{signal['price_vs_200ma']:.1f}%"
                if rsi_range not in rsi_ranges:
                    rsi_ranges[rsi_range] = 0
                rsi_ranges[rsi_range] += 1

        print("不同价格位置(相对200MA)的买入信号分布:")
        for range_key, count in sorted(rsi_ranges.items()):
            print(f"  价格在200MA {range_key} 以上: {count}次")

    return trades, cumulative_returns


def plot_technical_analysis(stock_data, buy_signals, sell_signals, stack_code, cumulative_returns=None):
    """
    使用matplotlib绘制包含技术指标的股票图表
    """
    if cumulative_returns is not None:
        fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6)) = plt.subplots(3, 2, figsize=(20, 15))
    else:
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 12))
        ax5, ax6 = None, None

    # 过滤掉移动平均线的NaN值
    valid_data = stock_data.dropna(subset=['MA20', 'MA60', 'MA200', 'MACD', 'RSI'])

    # 第一个子图：股价和移动平均线
    ax1.plot(valid_data.index, valid_data['Close'], label='收盘价', linewidth=1, color='black')
    ax1.plot(valid_data.index, valid_data['MA5'], label='5MA', linewidth=1, color='purple', alpha=0.7)
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

    ax1.set_title(f'台积电({stack_code}) - 股价与移动平均线 (优化5MA/20MA策略)', fontsize=14)
    ax1.set_ylabel('价格 (TWD)', fontsize=12)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 第二个子图：成交量
    ax2.bar(valid_data.index, valid_data['Volume'], alpha=0.3, color='gray', label='成交量')
    ax2.plot(valid_data.index, valid_data['Volume_MA20'], color='red', linewidth=1, label='20日成交量均线')
    ax2.set_ylabel('成交量', fontsize=12)
    ax2.set_title('成交量与均线', fontsize=14)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    # 第三个子图：MACD
    ax3.plot(valid_data.index, valid_data['MACD'], label='MACD', linewidth=1, color='blue')
    ax3.plot(valid_data.index, valid_data['MACD_Signal'], label='Signal', linewidth=1, color='red')

    # 绘制MACD柱状图，用颜色区分正负
    colors = ['green' if x >= 0 else 'red' for x in valid_data['MACD_Histogram']]
    ax3.bar(valid_data.index, valid_data['MACD_Histogram'], color=colors, alpha=0.3, label='Histogram')

    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax3.axhline(y=-0.5, color='orange', linestyle='--', alpha=0.5, label='MACD阈值(-0.5)')
    ax3.set_ylabel('MACD', fontsize=12)
    ax3.set_title('MACD指标 (优化参数)', fontsize=14)
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)

    # 第四个子图：RSI
    ax4.plot(valid_data.index, valid_data['RSI'], label='RSI', linewidth=1, color='purple')
    ax4.axhline(y=80, color='red', linestyle='--', alpha=0.7, label='超买线 (80)')
    ax4.axhline(y=75, color='orange', linestyle='--', alpha=0.7, label='动态上限')
    ax4.axhline(y=40, color='orange', linestyle='--', alpha=0.7, label='动态下限')
    ax4.axhline(y=25, color='green', linestyle='--', alpha=0.7, label='超卖线 (25)')
    ax4.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='中线 (50)')
    ax4.set_ylabel('RSI', fontsize=12)
    ax4.set_title('RSI指标 (动态阈值)', fontsize=14)
    ax4.set_ylim(0, 100)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)

    # 第五个子图：累计收益率曲线
    if ax5 is not None and cumulative_returns is not None:
        ax5.plot(range(1, len(cumulative_returns) + 1), cumulative_returns,
                 color='blue', linewidth=2, marker='o', markersize=4)
        ax5.set_xlabel('交易次数', fontsize=12)
        ax5.set_ylabel('累计收益率 (%)', fontsize=12)
        ax5.set_title('策略累计收益率曲线', fontsize=14)
        ax5.grid(True, alpha=0.3)

        # 标记正负收益
        ax5.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax5.fill_between(range(1, len(cumulative_returns) + 1), cumulative_returns, 0,
                         where=np.array(cumulative_returns) >= 0, alpha=0.3, color='green')
        ax5.fill_between(range(1, len(cumulative_returns) + 1), cumulative_returns, 0,
                         where=np.array(cumulative_returns) < 0, alpha=0.3, color='red')

    # 第六个子图：优化策略说明
    if ax6 is not None:
        ax6.axis('off')
        strategy_info = """
优化策略规则：

买入条件：
1. 5MA与20MA黄金交叉
2. 收盘价在200MA之上
3. MACD优化条件：
   - MACD > -0.5 且
   - (柱状图改善 或 金叉 或 MACD > 0)
4. RSI动态阈值：
   - 根据价格相对200MA位置调整
   - 强势市场：40-80
   - 正常市场：30-75  
   - 弱势市场：25-70
5. 成交量确认：不低于20日均量80%

卖出条件：
1. 20MA与60MA死亡交叉

优化特点：
- 动态适应市场强度
- 避免过度过滤强势股
- 成交量确认提高信号质量
        """
        ax6.text(0.05, 0.95, strategy_info, transform=ax6.transAxes, fontsize=11,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.show()


def main():
    """
    主函数
    """
    stack_code = "2330.TW"
    # 设置时间范围（近10年）
    years = 10
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    print("正在获取台积电股价数据...")

    try:
        # 获取台积电股价数据（台股代码：2330.TW）
        stock = yf.download(stack_code, start=start_date, end=end_date, auto_adjust=True)

        if stock.empty:
            print("无法获取数据，请检查网络连接或股票代码")
            return

        print(f"成功获取数据：{len(stock)} 个交易日")

        # 计算移动平均线和信号（使用优化后的过滤条件）
        stock_with_indicators, buy_signals, sell_signals, signal_details = optimized_ma_signals(stock)

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

        # 回测分析
        trades, cumulative_returns = backtest_analysis(buy_signals, sell_signals, signal_details)

        # 绘制图表
        print("\n正在生成图表...")
        plot_technical_analysis(stock_with_indicators, buy_signals, sell_signals, stack_code, cumulative_returns)

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