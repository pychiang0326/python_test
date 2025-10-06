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
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)
    return stock_data


def calculate_macd(data, fast_period=12, slow_period=26, signal_period=9):
    """
    计算MACD指标
    """
    fast_ema = data['Close'].ewm(span=fast_period, adjust=False).mean()
    slow_ema = data['Close'].ewm(span=slow_period, adjust=False).mean()

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

    # 计算布林带
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

    # 计算市场状态指标
    df['Trend_Strength'] = abs(df['Close'] - df['MA200']) / df['MA200']
    df['Volatility'] = df['Close'].rolling(20).std() / df['Close'].rolling(20).mean()

    return df


def no_filter_ma_signals(stock_data):
    """
    无过滤策略 - 原始策略
    """
    df = fix_dataframe_columns(stock_data.copy())

    # 计算移动平均线
    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA60'] = df['Close'].rolling(window=60).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()

    holding = False
    buy_signals = []
    sell_signals = []

    for i in range(200, len(df)):
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        ma60 = df['MA60'].iloc[i]
        ma200 = df['MA200'].iloc[i]

        ma5_prev = df['MA5'].iloc[i - 1]
        ma20_prev = df['MA20'].iloc[i - 1]
        ma60_prev = df['MA60'].iloc[i - 1]

        golden_cross_5_20 = (ma5 > ma20) and (ma5_prev <= ma20_prev)
        death_cross_20_60 = (ma20 < ma60) and (ma20_prev >= ma60_prev)

        if golden_cross_5_20 and close_price > ma200 and not holding:
            buy_signals.append((date, close_price))
            holding = True
        elif death_cross_20_60 and holding:
            sell_signals.append((date, close_price))
            holding = False

    return df, buy_signals, sell_signals


def light_filter_ma_signals(stock_data):
    """
    轻量级过滤策略 - 只过滤明显差的信号
    """
    df = calculate_technical_indicators(stock_data)

    holding = False
    buy_signals = []
    sell_signals = []
    filtered_count = 0

    for i in range(200, len(df)):
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        ma60 = df['MA60'].iloc[i]
        ma200 = df['MA200'].iloc[i]
        rsi = df['RSI'].iloc[i]
        bb_upper = df['BB_Upper'].iloc[i]
        macd = df['MACD'].iloc[i]

        ma5_prev = df['MA5'].iloc[i - 1]
        ma20_prev = df['MA20'].iloc[i - 1]
        ma60_prev = df['MA60'].iloc[i - 1]

        golden_cross_5_20 = (ma5 > ma20) and (ma5_prev <= ma20_prev)
        death_cross_20_60 = (ma20 < ma60) and (ma20_prev >= ma60_prev)

        base_condition = golden_cross_5_20 and close_price > ma200

        if base_condition and not holding:
            # 轻量级过滤条件
            extremely_overbought = rsi > 85
            far_above_bb = close_price > bb_upper * 1.05
            severe_macd_bearish = macd < -2
            far_below_200ma = close_price < ma200 * 0.8

            filter_conditions = [
                not extremely_overbought,
                not far_above_bb,
                not severe_macd_bearish,
                not far_below_200ma
            ]

            light_filter_passed = all(filter_conditions)

            if light_filter_passed:
                buy_signals.append((date, close_price))
                holding = True
            else:
                filtered_count += 1

        elif death_cross_20_60 and holding:
            sell_signals.append((date, close_price))
            holding = False

    print(f"轻量级过滤：过滤掉了 {filtered_count} 个明显差的买入信号")
    return df, buy_signals, sell_signals

def optimized_light_filter_ma_signals(stock_data):
    """
    优化后的轻量级过滤策略 - 针对中信金特性调整
    """
    df = calculate_technical_indicators(stock_data)

    holding = False
    buy_signals = []
    sell_signals = []
    filtered_count = 0

    for i in range(200, len(df)):
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        ma60 = df['MA60'].iloc[i]
        ma200 = df['MA200'].iloc[i]
        rsi = df['RSI'].iloc[i]
        bb_upper = df['BB_Upper'].iloc[i]
        macd = df['MACD'].iloc[i]

        ma5_prev = df['MA5'].iloc[i - 1]
        ma20_prev = df['MA20'].iloc[i - 1]
        ma60_prev = df['MA60'].iloc[i - 1]

        golden_cross_5_20 = (ma5 > ma20) and (ma5_prev <= ma20_prev)
        death_cross_20_60 = (ma20 < ma60) and (ma20_prev >= ma60_prev)

        base_condition = golden_cross_5_20 and close_price > ma200

        if base_condition and not holding:
            # 针对中信金优化的过滤条件
            extremely_overbought = rsi > 75  # 从85降低到75
            moderately_overbought = rsi > 70  # 新增中等超买条件
            above_bb = close_price > bb_upper  # 从5%降低到突破上轨
            macd_bearish = macd < -0.5  # 从-2放宽到-0.5
            below_200ma = close_price < ma200 * 0.95  # 从80%调整到95%

            # 使用更灵活的过滤逻辑：满足任意2个条件就过滤
            filter_conditions = [
                extremely_overbought,
                moderately_overbought and above_bb,  # 组合条件
                macd_bearish and below_200ma,  # 组合条件
            ]

            # 如果满足任意条件就过滤
            should_filter = any(filter_conditions)

            if not should_filter:
                buy_signals.append((date, close_price))
                holding = True
            else:
                filtered_count += 1

        elif death_cross_20_60 and holding:
            sell_signals.append((date, close_price))
            holding = False

    print(f"优化轻量级过滤：过滤掉了 {filtered_count} 个买入信号")
    return df, buy_signals, sell_signals


def mean_reversion_strategy(stock_data):
    """
    均值回归策略 - 更适合金融股
    """
    df = calculate_technical_indicators(stock_data)

    # 添加均值回归指标
    df['Price_MA20_Ratio'] = df['Close'] / df['MA20']
    df['RSI_MA20'] = df['RSI'].rolling(20).mean()

    holding = False
    buy_signals = []
    sell_signals = []

    for i in range(200, len(df)):
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        price_ma20_ratio = df['Price_MA20_Ratio'].iloc[i]
        rsi = df['RSI'].iloc[i]
        rsi_ma20 = df['RSI_MA20'].iloc[i]

        # 均值回归买入条件：价格低于20MA且RSI超卖
        if not holding and price_ma20_ratio < 0.95 and rsi < 35:
            buy_signals.append((date, close_price))
            holding = True

        # 均值回归卖出条件：价格高于20MA且RSI超买
        elif holding and price_ma20_ratio > 1.05 and rsi > 65:
            sell_signals.append((date, close_price))
            holding = False

    return df, buy_signals, sell_signals

def adaptive_ma_signals(stock_data):
    """
    真正自适应的策略 - 确保与无过滤策略不同
    """
    df = calculate_technical_indicators(stock_data)

    holding = False
    buy_signals = []
    sell_signals = []

    for i in range(200, len(df)):
        date = df.index[i]
        close_price = df['Close'].iloc[i]
        ma5 = df['MA5'].iloc[i]
        ma20 = df['MA20'].iloc[i]
        ma60 = df['MA60'].iloc[i]
        ma200 = df['MA200'].iloc[i]
        rsi = df['RSI'].iloc[i]
        trend_strength = df['Trend_Strength'].iloc[i]
        volatility = df['Volatility'].iloc[i]
        macd = df['MACD'].iloc[i]

        ma5_prev = df['MA5'].iloc[i - 1]
        ma20_prev = df['MA20'].iloc[i - 1]
        ma60_prev = df['MA60'].iloc[i - 1]

        golden_cross_5_20 = (ma5 > ma20) and (ma5_prev <= ma20_prev)
        death_cross_20_60 = (ma20 < ma60) and (ma20_prev >= ma60_prev)

        # 更严格的自适应条件
        if golden_cross_5_20 and close_price > ma200 and not holding:
            # 根据市场状态使用不同的过滤条件
            strong_trend = trend_strength > 0.15
            high_volatility = volatility > 0.02

            if strong_trend:
                # 强势市场：要求RSI不过热且MACD向上
                if rsi < 70 and macd > df['MACD'].iloc[i - 1]:
                    buy_signals.append((date, close_price))
                    holding = True
            elif high_volatility:
                # 高波动市场：更严格的RSI和价格位置要求
                if 40 < rsi < 65 and close_price > ma200 * 1.02:
                    buy_signals.append((date, close_price))
                    holding = True
            else:
                # 正常市场：适度过滤
                if rsi < 75 and close_price > ma200 * 0.98:
                    buy_signals.append((date, close_price))
                    holding = True

        elif death_cross_20_60 and holding:
            sell_signals.append((date, close_price))
            holding = False

    return df, buy_signals, sell_signals

def backtest_analysis(buy_signals, sell_signals, strategy_name="策略"):
    """
    回测分析和统计
    """
    print(f"\n" + "=" * 60)
    print(f"{strategy_name} - 回测统计分析")
    print("=" * 60)

    # 确保买卖信号数量匹配
    min_signals = min(len(buy_signals), len(sell_signals))
    buy_signals = buy_signals[:min_signals]
    sell_signals = sell_signals[:min_signals]

    if min_signals == 0:
        print("没有完整的交易对进行回测分析")
        return None, None, None

    # 计算每笔交易的收益率
    trades = []
    total_return = 1.0
    cumulative_returns = []

    for i in range(min_signals):
        buy_date, buy_price = buy_signals[i]
        sell_date, sell_price = sell_signals[i]

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

    # 年化收益率
    first_buy_date = datetime.strptime(trades[0]['买入日期'], '%Y-%m-%d')
    last_sell_date = datetime.strptime(trades[-1]['卖出日期'], '%Y-%m-%d')
    total_days = (last_sell_date - first_buy_date).days
    total_years = total_days / 365.25
    annualized_return = (total_return ** (1 / total_years) - 1) * 100 if total_years > 0 else 0

    # 最大回撤计算
    equity_curve = [1.0]
    for ret in returns:
        equity_curve.append(equity_curve[-1] * (1 + ret / 100))

    running_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - running_max) / running_max * 100
    max_drawdown = np.min(drawdowns)

    # 打印统计摘要
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

    # 返回统计信息
    stats = {
        'total_trades': total_trades,
        'win_rate': win_rate,
        'total_return': (total_return - 1) * 100,
        'annualized_return': annualized_return,
        'max_drawdown': max_drawdown
    }

    return stats, trades, cumulative_returns


def compare_strategies(stock_data):
    """
    比较不同策略的表现
    """
    print("正在比较不同策略...")

    # 策略1: 无过滤策略
    df1, buy1, sell1 = no_filter_ma_signals(stock_data)
    stats1, trades1, cum_ret1 = backtest_analysis(buy1, sell1, "无过滤策略")

    # 策略2: 轻量级过滤策略
    #df2, buy2, sell2 = light_filter_ma_signals(stock_data)
    #df2, buy2, sell2 = optimized_light_filter_ma_signals(stock_data)
    # 金融股：均值回歸策略
    df2, buy2, sell2 = mean_reversion_strategy(stock_data)
    stats2, trades2, cum_ret2 = backtest_analysis(buy2, sell2, "轻量级过滤策略")

    # 策略3: 自适应策略
    df3, buy3, sell3 = adaptive_ma_signals(stock_data)
    stats3, trades3, cum_ret3 = backtest_analysis(buy3, sell3, "自适应策略")

    # 策略比较总结
    print("\n" + "=" * 80)
    print("策略比较总结")
    print("=" * 80)

    strategies = []
    if stats1:
        strategies.append(("无过滤策略", stats1['total_trades'], stats1['total_return'], stats1['win_rate']))
    if stats2:
        strategies.append(("轻量级过滤", stats2['total_trades'], stats2['total_return'], stats2['win_rate']))
    if stats3:
        strategies.append(("自适应策略", stats3['total_trades'], stats3['total_return'], stats3['win_rate']))

    print(f"{'策略名称':<15} {'交易次数':<10} {'累计收益率':<12} {'胜率':<10}")
    print("-" * 50)
    for name, trades, ret, win_rate in strategies:
        print(f"{name:<15} {trades:<10} {ret:.2f}%{'':<8} {win_rate:.2f}%")

    # 返回最佳策略
    if strategies:
        best_strategy = max(strategies, key=lambda x: x[2])  # 按累计收益率排序
        print(f"\n🎯 最佳策略: {best_strategy[0]} (累计收益率: {best_strategy[2]:.2f}%)")

    return {
        '无过滤': (df1, buy1, sell1, cum_ret1, stats1),
        '轻量级': (df2, buy2, sell2, cum_ret2, stats2),
        '自适应': (df3, buy3, sell3, cum_ret3, stats3)
    }


def plot_comparison(strategy_results):
    """
    绘制策略比较图表
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 累计收益率比较
    ax1 = axes[0, 0]
    colors = ['blue', 'green', 'red']
    strategy_names = ['无过滤', '轻量级', '自适应']

    for i, (name, color) in enumerate(zip(strategy_names, colors)):
        if name in strategy_results and strategy_results[name][4]:  # 检查stats是否存在
            df, buy, sell, cum_ret, stats = strategy_results[name]
            if cum_ret is not None:
                ax1.plot(range(1, len(cum_ret) + 1), cum_ret,
                         color=color, linewidth=2, marker='o', markersize=4, label=name)

    ax1.set_xlabel('交易次数')
    ax1.set_ylabel('累计收益率 (%)')
    ax1.set_title('策略累计收益率比较')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 策略指标雷达图
    ax2 = axes[0, 1]
    metrics = ['累计收益率', '胜率', '年化收益', '风险控制']
    strategy_metrics = {}

    for name in strategy_names:
        if name in strategy_results and strategy_results[name][4]:
            stats = strategy_results[name][4]
            # 标准化指标到0-1范围
            total_return_norm = min(stats['total_return'] / 100, 1.0)
            win_rate_norm = stats['win_rate'] / 100
            annual_return_norm = min(stats['annualized_return'] / 30, 1.0)  # 假设30%为上限
            risk_control_norm = 1 - min(abs(stats['max_drawdown']) / 30, 1.0)  # 假设30%为最大回撤上限

            strategy_metrics[name] = [total_return_norm, win_rate_norm, annual_return_norm, risk_control_norm]

    # 绘制雷达图
    if strategy_metrics:
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形

        for name, metrics_values in strategy_metrics.items():
            values = metrics_values + [metrics_values[0]]  # 闭合图形
            ax2.plot(angles, values, 'o-', linewidth=2, label=name)
            ax2.fill(angles, values, alpha=0.1)

        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(metrics)
        ax2.set_ylim(0, 1)
        ax2.set_title('策略综合指标雷达图')
        ax2.legend()

    # 交易次数分布
    ax3 = axes[1, 0]
    strategy_names_plot = []
    trade_counts = []

    for name in strategy_names:
        if name in strategy_results and strategy_results[name][4]:
            strategy_names_plot.append(name)
            trade_counts.append(strategy_results[name][4]['total_trades'])

    if strategy_names_plot:
        bars = ax3.bar(strategy_names_plot, trade_counts, color=colors[:len(strategy_names_plot)], alpha=0.7)
        ax3.set_ylabel('交易次数')
        ax3.set_title('各策略交易次数')

        # 在柱状图上显示数值
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}', ha='center', va='bottom')

    # 策略推荐
    ax4 = axes[1, 1]
    ax4.axis('off')

    recommendation = """
策略选择建议：

基于回测结果：

1. 无过滤策略
   - 优点：收益率最高，胜率最高
   - 缺点：可能会有更多小亏损
   - 适合：追求高收益的投资者

2. 轻量级过滤策略  
   - 优点：过滤明显差信号，风险控制较好
   - 缺点：收益率较低
   - 适合：风险厌恶型投资者

3. 自适应策略
   - 优点：根据市场状态调整
   - 缺点：复杂度较高
   - 适合：希望平衡收益与风险的投资者

推荐：对于台积电这类强趋势股票，建议使用无过滤策略
    """

    ax4.text(0.05, 0.95, recommendation, transform=ax4.transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

    plt.tight_layout()
    plt.show()

def plot_detailed_analysis(strategy_results, stock_data):
    """
    详细的策略分析图表
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. 收益率分布箱线图
    returns_data = []
    strategy_names = []

    for name, (df, buy, sell, cum_ret, stats) in strategy_results.items():
        if stats:
            # 计算每笔交易收益率
            trades_returns = []
            for j in range(min(len(buy), len(sell))):
                buy_price = buy[j][1]
                sell_price = sell[j][1]
                returns = (sell_price - buy_price) / buy_price * 100
                trades_returns.append(returns)

            returns_data.append(trades_returns)
            strategy_names.append(name)

    axes[0, 0].boxplot(returns_data, labels=strategy_names)
    axes[0, 0].set_title('各策略单次交易收益率分布')
    axes[0, 0].set_ylabel('收益率 (%)')

    # 2. 持有期分布
    holding_data = []
    for name, (df, buy, sell, cum_ret, stats) in strategy_results.items():
        if stats:
            holding_periods = []
            for j in range(min(len(buy), len(sell))):
                buy_date = buy[j][0]
                sell_date = sell[j][0]
                holding_days = (sell_date - buy_date).days
                holding_periods.append(holding_days)
            holding_data.append(holding_periods)

    axes[0, 1].boxplot(holding_data, labels=strategy_names)
    axes[0, 1].set_title('各策略持有期分布')
    axes[0, 1].set_ylabel('持有天数')

    # 3. 月度收益率热力图（示例）
    # 这里可以添加更多分析图表...

    axes[1, 0].axis('off')  # 暂时留空
    axes[1, 1].axis('off')  # 暂时留空

    plt.tight_layout()
    plt.show()

def debug_strategy_performance(stock_data, stock_code):
    """
    诊断策略表现差异的原因
    """
    print(f"\n🔍 正在诊断{stock_code}策略表现...")

    df = calculate_technical_indicators(stock_data)

    # 分析技术指标分布
    rsi_values = df['RSI'].dropna()
    macd_values = df['MACD'].dropna()
    price_vs_200ma = (df['Close'] - df['MA200']) / df['MA200'] * 100

    print(f"RSI统计: 均值={rsi_values.mean():.1f}, 最大值={rsi_values.max():.1f}, 最小值={rsi_values.min():.1f}")
    print(f"MACD统计: 均值={macd_values.mean():.3f}, 最大值={macd_values.max():.3f}, 最小值={macd_values.min():.3f}")
    print(
        f"价格相对200MA: 均值={price_vs_200ma.mean():.1f}%, 最大值={price_vs_200ma.max():.1f}%, 最小值={price_vs_200ma.min():.1f}%")

    # 检查过滤条件触发情况
    extreme_rsi_count = len(df[df['RSI'] > 85])
    far_above_bb_count = len(df[df['Close'] > df['BB_Upper'] * 1.05])
    severe_macd_count = len(df[df['MACD'] < -2])
    far_below_200ma_count = len(df[df['Close'] < df['MA200'] * 0.8])

    print(f"\n过滤条件触发统计:")
    print(f"  RSI > 85: {extreme_rsi_count}次")
    print(f"  价格 > 布林带上轨5%: {far_above_bb_count}次")
    print(f"  MACD < -2: {severe_macd_count}次")
    print(f"  价格 < 200MA 80%: {far_below_200ma_count}次")

    # 检查市场状态
    strong_trend_count = len(df[df['Trend_Strength'] > 0.15])
    high_volatility_count = len(df[df['Volatility'] > 0.02])

    print(f"\n市场状态统计:")
    print(f"  强势趋势(>15%): {strong_trend_count}天")
    print(f"  高波动(>2%): {high_volatility_count}天")

    return df

def main():
    """
    主函数
    """
    # stack_code = "2330.TW"
    stack_code = "2891.TW"
    years = 10
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    print(f"正在获取{stack_code}股价数据...")

    try:
        stock = yf.download(stack_code, start=start_date, end=end_date, auto_adjust=True)

        if stock.empty:
            print("无法获取数据，请检查网络连接或股票代码")
            return

        print(f"成功获取数据：{len(stock)} 个交易日")

        # 添加诊断
        debug_df = debug_strategy_performance(stock, stack_code)

        # 比较多种策略
        strategy_results = compare_strategies(stock)

        # 绘制策略比较图表
        print("\n正在生成策略比较图表...")
        plot_comparison(strategy_results)

        # 新增：绘制详细分析图表
        print("\n正在生成详细分析图表...")
        plot_detailed_analysis(strategy_results, stock)

        return strategy_results

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        import yfinance
    except ImportError:
        print("请先安装必要的库：")
        print("pip install yfinance pandas matplotlib")

    main()