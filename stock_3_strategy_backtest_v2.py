import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import numpy as np

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


def backtest_strategy(data, initial_capital=1000000, transaction_cost=0.0015):
    """
    回测移动平均线交叉策略
    """
    # 初始化变量
    cash = initial_capital
    shares = 0
    trades = []
    portfolio_values = []
    buy_hold_values = []  # 买入持有策略的对比

    # 买入持有策略的初始状态
    bh_shares = initial_capital / data.iloc[0]['Close']  # 第一天就全仓买入
    bh_value = bh_shares * data.iloc[0]['Close']

    # 遍历每一天
    for i, (date, row) in enumerate(data.iterrows()):
        current_price = row['Close']
        signal = row['Cross']

        # 计算当前投资组合价值
        current_value = cash + shares * current_price
        portfolio_values.append(current_value)

        # 计算买入持有策略的价值
        bh_value = bh_shares * current_price
        buy_hold_values.append(bh_value)

        # 黄金交叉信号 - 买入
        if signal == 1 and cash > 0:
            # 计算可买入的股数（考虑交易成本）
            available_cash = cash * (1 - transaction_cost)
            shares_to_buy = available_cash // current_price

            if shares_to_buy > 0:
                # 执行买入
                cost = shares_to_buy * current_price
                cash -= cost * (1 + transaction_cost)  # 扣除交易成本
                shares += shares_to_buy

                trades.append({
                    'date': date,
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy,
                    'value': cost,
                    'portfolio_value': current_value
                })

        # 死亡交叉信号 - 卖出
        elif signal == -1 and shares > 0:
            # 执行卖出
            proceeds = shares * current_price
            cash += proceeds * (1 - transaction_cost)  # 扣除交易成本

            trades.append({
                'date': date,
                'action': 'SELL',
                'price': current_price,
                'shares': shares,
                'value': proceeds,
                'portfolio_value': cash + proceeds
            })

            shares = 0

    # 回测结束，计算最终价值
    final_value = cash + shares * data.iloc[-1]['Close']

    # 计算回测指标
    total_return = (final_value - initial_capital) / initial_capital * 100
    bh_final_value = buy_hold_values[-1]
    bh_total_return = (bh_final_value - initial_capital) / initial_capital * 100

    # 计算年化回报率
    years = len(data) / 252  # 假设一年有252个交易日
    annual_return = (final_value / initial_capital) ** (1 / years) - 1 if years > 0 else 0
    annual_return_pct = annual_return * 100

    bh_annual_return = (bh_final_value / initial_capital) ** (1 / years) - 1 if years > 0 else 0
    bh_annual_return_pct = bh_annual_return * 100

    # 计算最大回撤
    portfolio_series = pd.Series(portfolio_values, index=data.index)
    rolling_max = portfolio_series.expanding().max()
    drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdowns.min()

    bh_series = pd.Series(buy_hold_values, index=data.index)
    bh_rolling_max = bh_series.expanding().max()
    bh_drawdowns = (bh_series - bh_rolling_max) / bh_rolling_max * 100
    bh_max_drawdown = bh_drawdowns.min()

    return {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return_pct,
        'max_drawdown': max_drawdown,
        'trades': trades,
        'num_trades': len([t for t in trades if t['action'] == 'BUY']),
        'portfolio_values': portfolio_values,
        'buy_hold_final': bh_final_value,
        'buy_hold_return': bh_total_return,
        'buy_hold_annual': bh_annual_return_pct,
        'buy_hold_max_drawdown': bh_max_drawdown,
        'buy_hold_values': buy_hold_values
    }


def backtest_phased_strategy(data, total_investment=1000000, phases=10, transaction_cost=0.0015):
    """
    回测分批买入策略
    每期投入固定金额，共分多期投入
    """
    # 计算每期投入金额
    phase_amount = total_investment / phases

    # 初始化变量
    cash = 0  # 开始时没有现金，每期投入
    shares = 0
    trades = []
    portfolio_values = []
    phases_executed = 0
    next_phase_date = data.index[0]  # 从第一天开始第一期投入

    # 计算投入间隔（按交易日计算）
    total_days = len(data)
    days_between_phases = total_days // phases

    # 遍历每一天
    for i, (date, row) in enumerate(data.iterrows()):
        current_price = row['Close']

        # 执行分期投入
        if date >= next_phase_date and phases_executed < phases:
            # 投入一期资金
            cash += phase_amount
            phases_executed += 1
            # 计算下一期投入日期
            next_phase_date = data.index[min(i + days_between_phases, len(data) - 1)]

            # 记录投入
            trades.append({
                'date': date,
                'action': 'PHASE_IN',
                'price': current_price,
                'shares': 0,
                'value': phase_amount,
                'portfolio_value': cash + shares * current_price
            })

        # 用可用现金买入股票
        if cash > 0:
            # 计算可买入的股数（考虑交易成本）
            available_cash = cash * (1 - transaction_cost)
            shares_to_buy = available_cash // current_price

            if shares_to_buy > 0:
                # 执行买入
                cost = shares_to_buy * current_price
                cash -= cost * (1 + transaction_cost)  # 扣除交易成本
                shares += shares_to_buy

                trades.append({
                    'date': date,
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy,
                    'value': cost,
                    'portfolio_value': cash + shares * current_price
                })

        # 计算当前投资组合价值
        current_value = cash + shares * current_price
        portfolio_values.append(current_value)

    # 回测结束，计算最终价值
    final_value = cash + shares * data.iloc[-1]['Close']

    # 计算回测指标
    total_return = (final_value - total_investment) / total_investment * 100

    # 计算年化回报率
    years = len(data) / 252  # 假设一年有252个交易日
    annual_return = (final_value / total_investment) ** (1 / years) - 1 if years > 0 else 0
    annual_return_pct = annual_return * 100

    # 计算最大回撤
    portfolio_series = pd.Series(portfolio_values, index=data.index)
    rolling_max = portfolio_series.expanding().max()
    drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdowns.min()

    return {
        'total_investment': total_investment,
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return_pct,
        'max_drawdown': max_drawdown,
        'trades': trades,
        'num_phases': phases_executed,
        'portfolio_values': portfolio_values,
        'phase_amount': phase_amount
    }


def simple_stock_analysis():
    # 设置中文字体
    set_chinese_font()

    # 获取数据
    stock_code = "2330.TW"
    # stock_code = "2891.TW"
    years = 10
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    print(f"正在下载{stock_code}历史数据...")
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

    plt.title(f'{stock_code}近{years}年股价走势 - 移动平均线交叉信号')
    plt.xlabel('日期')
    plt.ylabel('价格 (TWD)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # 执行回测
    print("\n开始回测移动平均线交叉策略...")
    backtest_results = backtest_strategy(data)

    # 执行分批买入策略回测
    print("\n开始回测分批买入策略...")
    phased_results = backtest_phased_strategy(data, total_investment=1000000, phases=10)

    # 打印回测结果
    print("\n" + "=" * 70)
    print("回测结果总结")
    print("=" * 70)
    print(f"回测期间: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")

    print(f"\n1. 移动平均线交叉策略:")
    print(f"初始资金: {backtest_results['initial_capital']:,.0f} 元")
    print(f"最终资产: {backtest_results['final_value']:,.0f} 元")
    print(f"总收益率: {backtest_results['total_return']:.2f}%")
    print(f"年化收益率: {backtest_results['annual_return']:.2f}%")
    print(f"最大回撤: {backtest_results['max_drawdown']:.2f}%")
    print(f"交易次数: {backtest_results['num_trades']} 次")

    print(f"\n2. 分批买入策略 (10期，每期100,000元):")
    print(f"总投入资金: {phased_results['total_investment']:,.0f} 元")
    print(f"最终资产: {phased_results['final_value']:,.0f} 元")
    print(f"总收益率: {phased_results['total_return']:.2f}%")
    print(f"年化收益率: {phased_results['annual_return']:.2f}%")
    print(f"最大回撤: {phased_results['max_drawdown']:.2f}%")
    print(f"执行期数: {phased_results['num_phases']} 期")

    print(f"\n3. 买入持有策略对比:")
    print(f"最终资产: {backtest_results['buy_hold_final']:,.0f} 元")
    print(f"总收益率: {backtest_results['buy_hold_return']:.2f}%")
    print(f"年化收益率: {backtest_results['buy_hold_annual']:.2f}%")
    print(f"最大回撤: {backtest_results['buy_hold_max_drawdown']:.2f}%")

    # 计算策略相对于买入持有的超额收益
    excess_return_ma = backtest_results['total_return'] - backtest_results['buy_hold_return']
    excess_annual_ma = backtest_results['annual_return'] - backtest_results['buy_hold_annual']

    excess_return_phased = phased_results['total_return'] - backtest_results['buy_hold_return']
    excess_annual_phased = phased_results['annual_return'] - backtest_results['buy_hold_annual']

    print(f"\n4. 策略相对买入持有的表现:")
    print(f"移动平均线策略超额总收益: {excess_return_ma:.2f}%")
    print(f"移动平均线策略超额年化收益: {excess_annual_ma:.2f}%")
    print(f"分批买入策略超额总收益: {excess_return_phased:.2f}%")
    print(f"分批买入策略超额年化收益: {excess_annual_phased:.2f}%")

    if excess_return_ma > 0:
        print("移动平均线交叉策略表现优于买入持有策略")
    else:
        print("移动平均线交叉策略表现不如买入持有策略")

    if excess_return_phased > 0:
        print("分批买入策略表现优于买入持有策略")
    else:
        print("分批买入策略表现不如买入持有策略")

    # 绘制资产曲线对比图
    plt.figure(figsize=(15, 10))

    # 计算资产曲线的索引
    dates = data.index

    # 绘制策略资产曲线
    plt.plot(dates, backtest_results['portfolio_values'],
             label='移动平均线策略', color='blue', linewidth=2)

    # 绘制分批买入策略资产曲线
    plt.plot(dates, phased_results['portfolio_values'],
             label='分批买入策略 (10期)', color='green', linewidth=2)

    # 绘制买入持有策略资产曲线
    plt.plot(dates, backtest_results['buy_hold_values'],
             label='买入持有策略', color='red', linewidth=2)

    # 标记移动平均线策略的买卖点
    buy_dates = [t['date'] for t in backtest_results['trades'] if t['action'] == 'BUY']
    sell_dates = [t['date'] for t in backtest_results['trades'] if t['action'] == 'SELL']

    # 获取买卖点的资产价值
    buy_values = [backtest_results['portfolio_values'][data.index.get_loc(date)] for date in buy_dates]
    sell_values = [backtest_results['portfolio_values'][data.index.get_loc(date)] for date in sell_dates]

    plt.scatter(buy_dates, buy_values, marker='^', color='blue', s=100, label='移动平均线买入点', zorder=5)
    plt.scatter(sell_dates, sell_values, marker='v', color='blue', s=100, label='移动平均线卖出点', zorder=5)

    # 标记分批买入策略的投入点
    phase_dates = [t['date'] for t in phased_results['trades'] if t['action'] == 'PHASE_IN']
    phase_values = [phased_results['portfolio_values'][data.index.get_loc(date)] for date in phase_dates]

    plt.scatter(phase_dates, phase_values, marker='o', color='green', s=100, label='分批投入点', zorder=5)

    plt.title(f'{stock_code} 三种投资策略资产曲线对比')
    plt.xlabel('日期')
    plt.ylabel('资产价值 (元)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    # 打印策略比较分析
    print("\n" + "=" * 70)
    print("策略比较分析")
    print("=" * 70)

    # 计算各策略最终资产排序
    strategies = {
        '买入持有策略': backtest_results['buy_hold_final'],
        '移动平均线策略': backtest_results['final_value'],
        '分批买入策略': phased_results['final_value']
    }

    sorted_strategies = sorted(strategies.items(), key=lambda x: x[1], reverse=True)

    print("按最终资产排序:")
    for i, (name, value) in enumerate(sorted_strategies, 1):
        print(f"{i}. {name}: {value:,.0f} 元")

    # 风险收益分析
    print(f"\n风险收益分析:")
    print(
        f"买入持有策略: 收益率 {backtest_results['buy_hold_return']:.2f}%, 最大回撤 {backtest_results['buy_hold_max_drawdown']:.2f}%")
    print(
        f"移动平均线策略: 收益率 {backtest_results['total_return']:.2f}%, 最大回撤 {backtest_results['max_drawdown']:.2f}%")
    print(f"分批买入策略: 收益率 {phased_results['total_return']:.2f}%, 最大回撤 {phased_results['max_drawdown']:.2f}%")

    # 计算风险调整后收益 (夏普比率简化版)
    def calculate_simple_sharpe(return_pct, max_drawdown):
        # 简化版夏普比率：收益率/最大回撤（绝对值）
        if max_drawdown == 0:
            return float('inf')
        return return_pct / abs(max_drawdown)

    sharpe_bh = calculate_simple_sharpe(backtest_results['buy_hold_return'], backtest_results['buy_hold_max_drawdown'])
    sharpe_ma = calculate_simple_sharpe(backtest_results['total_return'], backtest_results['max_drawdown'])
    sharpe_phased = calculate_simple_sharpe(phased_results['total_return'], phased_results['max_drawdown'])

    print(f"\n风险调整后收益 (收益率/最大回撤):")
    print(f"买入持有策略: {sharpe_bh:.2f}")
    print(f"移动平均线策略: {sharpe_ma:.2f}")
    print(f"分批买入策略: {sharpe_phased:.2f}")

    # 投资建议
    print(f"\n投资建议:")
    if sharpe_phased > sharpe_bh and sharpe_phased > sharpe_ma:
        print("分批买入策略在风险调整后收益方面表现最佳，适合风险厌恶型投资者")
    elif sharpe_bh > sharpe_ma:
        print("买入持有策略在风险调整后收益方面表现最佳，适合长期投资者")
    else:
        print("移动平均线策略在风险调整后收益方面表现最佳，适合主动型投资者")

    # 打印交易详情
    if backtest_results['trades']:
        print(f"\n移动平均线策略交易详情 (前10笔):")
        print("-" * 100)
        print(f"{'日期':<12} {'操作':<6} {'价格':<8} {'股数':<10} {'金额':<12} {'组合价值':<12}")
        print("-" * 100)

        for i, trade in enumerate(backtest_results['trades'][:10]):
            print(f"{trade['date'].strftime('%Y-%m-%d'):<12} {trade['action']:<6} {trade['price']:<8.2f} "
                  f"{trade['shares']:<10.0f} {trade['value']:<12.0f} {trade['portfolio_value']:<12.0f}")

        if len(backtest_results['trades']) > 10:
            print(f"... 还有 {len(backtest_results['trades']) - 10} 笔交易未显示")

    if phased_results['trades']:
        print(f"\n分批买入策略投入详情:")
        print("-" * 80)
        print(f"{'日期':<12} {'操作':<10} {'价格':<8} {'投入金额':<12} {'组合价值':<12}")
        print("-" * 80)

        phase_in_trades = [t for t in phased_results['trades'] if t['action'] == 'PHASE_IN']
        for i, trade in enumerate(phase_in_trades):
            print(f"{trade['date'].strftime('%Y-%m-%d'):<12} {trade['action']:<10} {trade['price']:<8.2f} "
                  f"{trade['value']:<12.0f} {trade['portfolio_value']:<12.0f}")

    # 打印统计信息
    print(f"\n策略信号统计:")
    print(f"黄金交叉次数: {len(buy_signals)}")
    print(f"死亡交叉次数: {len(sell_signals)}")
    print(f"数据期间: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")


# 执行函数
if __name__ == "__main__":
    simple_stock_analysis()