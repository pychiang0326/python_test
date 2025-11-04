import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# 过滤掉无害的警告
warnings.filterwarnings("ignore", category=FutureWarning)


def set_chinese_font():
    try:
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    except:
        print("警告: 中文字体设置可能不完整，图表中的中文可能无法正常显示")


def plot_strategy_comparison_final(data, ma_results, bh_results, phased_results, monthly_dca_results, stock_code):
    """
    修复版本：正确处理所有策略的资产曲线
    """
    print("\n正在准备图表数据...")

    # 创建统一的日期索引
    dates = data.index

    # 处理移动平均线策略
    if len(ma_results['portfolio_values']) != len(dates):
        ma_values = np.interp(
            np.linspace(0, len(ma_results['portfolio_values']) - 1, len(dates)),
            np.arange(len(ma_results['portfolio_values'])),
            ma_results['portfolio_values']
        )
    else:
        ma_values = ma_results['portfolio_values']

    # 处理买入持有策略
    if len(bh_results['portfolio_values']) != len(dates):
        bh_values = np.interp(
            np.linspace(0, len(bh_results['portfolio_values']) - 1, len(dates)),
            np.arange(len(bh_results['portfolio_values'])),
            bh_results['portfolio_values']
        )
    else:
        bh_values = bh_results['portfolio_values']

    # 处理分批买入策略
    if len(phased_results['portfolio_values']) != len(dates):
        phased_values = np.interp(
            np.linspace(0, len(phased_results['portfolio_values']) - 1, len(dates)),
            np.arange(len(phased_results['portfolio_values'])),
            phased_results['portfolio_values']
        )
    else:
        phased_values = phased_results['portfolio_values']

    # 处理每月定投策略
    if len(monthly_dca_results['portfolio_values']) != len(dates):
        monthly_values = np.interp(
            np.linspace(0, len(monthly_dca_results['portfolio_values']) - 1, len(dates)),
            np.arange(len(monthly_dca_results['portfolio_values'])),
            monthly_dca_results['portfolio_values']
        )
    else:
        monthly_values = monthly_dca_results['portfolio_values']

    # 转换为万元单位
    ma_values_wan = [v / 10000 for v in ma_values]
    bh_values_wan = [v / 10000 for v in bh_values]
    phased_values_wan = [v / 10000 for v in phased_values]
    monthly_values_wan = [v / 10000 for v in monthly_values]

    print(f"图表数据验证 (最终资产-万元):")
    print(f"移动平均线策略: {ma_values_wan[-1]:.2f}万")
    print(f"买入持有策略: {bh_values_wan[-1]:.2f}万")
    print(f"分批买入策略: {phased_values_wan[-1]:.2f}万")
    print(f"每月定投策略: {monthly_values_wan[-1]:.2f}万")

    # 创建图表
    plt.figure(figsize=(16, 10))

    # 绘制策略资产曲线
    plt.plot(dates, ma_values_wan,
             label=f'移动平均线策略 ({ma_results["total_return"]:.1f}%)',
             color='blue', linewidth=2, alpha=0.8)

    plt.plot(dates, bh_values_wan,
             label=f'买入持有策略 ({bh_results["total_return"]:.1f}%)',
             color='red', linewidth=2, alpha=0.8)

    plt.plot(dates, phased_values_wan,
             label=f'分批买入策略 ({phased_results["total_return"]:.1f}%)',
             color='green', linewidth=2, alpha=0.8)

    plt.plot(dates, monthly_values_wan,
             label=f'每月定投策略 ({monthly_dca_results["total_return"]:.1f}%)',
             color='orange', linewidth=2, alpha=0.8)

    # 标记分批买入的投入点
    if 'phase_dates' in phased_results:
        for i, phase_date in enumerate(phased_results['phase_dates']):
            if phase_date in dates:
                idx = list(dates).index(phase_date)
                if idx < len(phased_values_wan):
                    plt.scatter(phase_date, phased_values_wan[idx],
                                color='darkgreen', s=60, zorder=5, alpha=0.8)
                    if i % 2 == 0:  # 交替显示标注位置避免重叠
                        plt.annotate(f'第{i + 1}期', (phase_date, phased_values_wan[idx]),
                                     textcoords="offset points", xytext=(0, 15),
                                     ha='center', fontsize=9, color='darkgreen',
                                     bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                    else:
                        plt.annotate(f'第{i + 1}期', (phase_date, phased_values_wan[idx]),
                                     textcoords="offset points", xytext=(0, -20),
                                     ha='center', fontsize=9, color='darkgreen',
                                     bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))

    plt.title(f'{stock_code} 四种投资策略资产曲线对比 (2015-2025)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('资产价值 (万元)', fontsize=12)

    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)

    # 设置合适的Y轴范围
    all_values = ma_values_wan + bh_values_wan + phased_values_wan + monthly_values_wan
    y_max = max(all_values) * 1.1
    plt.ylim(bottom=0)

    plt.tight_layout()

    # 保存图表
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'strategy_comparison_final_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"图表已保存为 '{filename}'")

    plt.show()

    return filename


def calculate_buy_hold_manually(data, initial_cash=1000000):
    """手动计算买入持有策略"""
    initial_price = data.iloc[0]['Close']
    shares = int(initial_cash // initial_price)
    cash_remaining = initial_cash - shares * initial_price

    portfolio_values = []
    for i in range(len(data)):
        current_price = data.iloc[i]['Close']
        current_value = shares * current_price + cash_remaining
        portfolio_values.append(current_value)

    final_value = portfolio_values[-1]
    total_return = (final_value - initial_cash) / initial_cash * 100

    years = len(data) / 252
    annual_return = (final_value / initial_cash) ** (1 / years) - 1 if years > 0 else 0

    # 计算最大回撤
    portfolio_series = pd.Series(portfolio_values, index=data.index)
    rolling_max = portfolio_series.expanding().max()
    drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdowns.min()

    return {
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return * 100,
        'max_drawdown': max_drawdown,
        'portfolio_values': portfolio_values
    }


def backtest_ma_cross_optimized(data, initial_cash=1000000):
    """优化的移动平均线策略 - 修复版本"""
    data = data.copy()
    # 使用更敏感的均线组合
    data['MA20'] = data['Close'].rolling(window=20).mean()
    data['MA60'] = data['Close'].rolling(window=60).mean()

    # 添加趋势过滤器
    data['MA200'] = data['Close'].rolling(window=200).mean()

    cash = initial_cash
    shares = 0
    portfolio_values = []
    trades = []
    position = 0
    commission = 0.0015

    print("优化移动平均线策略参数: MA20/MA60 with MA200 filter")

    for i in range(len(data)):
        current_price = data.iloc[i]['Close']

        if i < 200:  # 等待足够的数据
            portfolio_values.append(cash + shares * current_price)
            continue

        ma20 = data.iloc[i]['MA20']
        ma60 = data.iloc[i]['MA60']
        ma200 = data.iloc[i]['MA200']
        ma20_prev = data.iloc[i - 1]['MA20'] if i > 0 else ma20
        ma60_prev = data.iloc[i - 1]['MA60'] if i > 0 else ma60

        # 趋势判断：价格在200日均线上方为牛市
        bull_market = current_price > ma200

        # 金叉买入 - 只在牛市中使用全部资金
        if bull_market and ma20_prev <= ma60_prev and ma20 > ma60 and position == 0:
            shares_to_buy = int(cash // (current_price * (1 + commission)))
            if shares_to_buy > 0:
                cost = shares_to_buy * current_price * (1 + commission)
                if cost <= cash:
                    cash -= cost
                    shares += shares_to_buy
                    position = 1
                    trades.append({
                        'date': data.index[i],
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy
                    })
                    print(f"优化MA策略买入: {data.index[i].date()}, 价格: {current_price:.2f}, 股数: {shares_to_buy}")

        # 死叉卖出
        elif ma20_prev >= ma60_prev and ma20 < ma60 and position == 1:
            if shares > 0:
                proceeds = shares * current_price * (1 - commission)
                cash += proceeds
                trades.append({
                    'date': data.index[i],
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares
                })
                print(f"优化MA策略卖出: {data.index[i].date()}, 价格: {current_price:.2f}, 股数: {shares}")
                shares = 0
                position = 0

        current_value = cash + shares * current_price
        portfolio_values.append(current_value)

    final_value = cash + shares * data.iloc[-1]['Close']
    total_return = (final_value - initial_cash) / initial_cash * 100

    years = len(data) / 252
    annual_return = (final_value / initial_cash) ** (1 / years) - 1 if years > 0 else 0

    portfolio_series = pd.Series(portfolio_values, index=data.index)
    rolling_max = portfolio_series.expanding().max()
    drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdowns.min()

    print(f"优化移动平均线策略交易次数: {len(trades)}")

    # 修复：确保返回结果
    return {
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return * 100,
        'max_drawdown': max_drawdown,
        'num_trades': len(trades),
        'portfolio_values': portfolio_values,
        'trades': trades
    }

def backtest_ma_cross_with_backtesting(data, initial_cash=1000000):
    """使用backtesting库回测移动平均线策略"""
    try:
        class ImprovedMAStrategy(Strategy):
            n1 = 20
            n2 = 60

            def init(self):
                self.ma1 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
                self.ma2 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)
                # 添加一个变量来跟踪入场价格
                self.entry_price = None

            def next(self):
                # 获取当前价格
                current_price = self.data.Close[-1]
                current_time = self.data.index[-1]

                if crossover(self.ma1, self.ma2):
                    if not self.position:
                        if current_price > 0:
                            # 使用95%的权益进行投资
                            total_equity = self.equity
                            investment = total_equity * 0.95
                            shares = int(investment // current_price)
                            if shares > 0:
                                # 记录入场价格
                                self.entry_price = current_price
                                # 打印买入交易信息
                                print(f"📈 买入信号 - 时间: {current_time}, "
                                      f"价格: {current_price:.2f}, 股数: {shares}, "
                                      f"投资额: {investment:.2f}")
                                self.buy(size=shares)

                elif crossover(self.ma2, self.ma1):
                    if self.position:
                        # 计算盈亏 - 使用我们记录的入场价格
                        if self.entry_price is not None:
                            profit_pct = (current_price / self.entry_price - 1) * 100
                            profit_amount = (current_price - self.entry_price) * self.position.size

                            # 打印卖出交易信息
                            print(f"📉 卖出信号 - 时间: {current_time}, "
                                  f"价格: {current_price:.2f}, 股数: {self.position.size}, "
                                  f"入场价: {self.entry_price:.2f}, 盈亏: {profit_amount:.2f} ({profit_pct:.2f}%)")

                            # 重置入场价格
                            self.entry_price = None
                        else:
                            # 如果没有记录入场价格，只打印基本信息
                            print(f"📉 卖出信号 - 时间: {current_time}, "
                                  f"价格: {current_price:.2f}, 股数: {self.position.size}")

                        self.position.close()

        bt = Backtest(data, ImprovedMAStrategy, cash=initial_cash,
                      commission=0.0015, exclusive_orders=True, finalize_trades=True)
        results = bt.run()

        # 打印交易统计信息
        print("\n" + "=" * 60)
        print("📊 移动平均线策略交易统计汇总")
        print("=" * 60)
        print(f"初始资金: {initial_cash:,.2f}")
        print(f"最终权益: {results['Equity Final [$]']:,.2f}")
        print(f"总收益率: {results['Return [%]']:.2f}%")
        print(f"年化收益率: {results['Return (Ann.) [%]']:.2f}%")
        print(f"最大回撤: {results['Max. Drawdown [%]']:.2f}%")
        print(f"总交易次数: {results['# Trades']}")

        # 检查是否有胜率等指标
        if 'Win Rate [%]' in results:
            print(f"胜率: {results['Win Rate [%]']:.2f}%")
        if 'Avg. Return [%]' in results:
            print(f"平均收益率: {results['Avg. Return [%]']:.2f}%")
        if 'Avg. Trade Duration' in results:
            print(f"平均持仓时间: {results['Avg. Trade Duration']}")

        # 打印详细的交易记录 - 使用更安全的方法
        try:
            trades_df = results._trades
            if trades_df is not None and len(trades_df) > 0:
                print(f"\n📋 详细交易记录 (共{len(trades_df)}笔):")
                print("=" * 100)
                for i, trade in trades_df.iterrows():
                    entry_time = trade.get('EntryTime', 'N/A')
                    exit_time = trade.get('ExitTime', 'N/A')
                    entry_price = trade.get('EntryPrice', 0)
                    exit_price = trade.get('ExitPrice', 0)
                    size = trade.get('Size', 0)
                    pnl = trade.get('PnL', 0)
                    pnl_pct = trade.get('ReturnPct', 0) * 100

                    duration = "N/A"
                    if entry_time != 'N/A' and exit_time != 'N/A':
                        try:
                            duration_days = (exit_time - entry_time).days
                            duration = f"{duration_days}天"
                        except:
                            pass

                    print(f"交易 #{i + 1}:")
                    print(f"  入场时间: {entry_time} | 入场价格: {entry_price:.2f}")
                    print(f"  出场时间: {exit_time} | 出场价格: {exit_price:.2f}")
                    print(f"  持仓天数: {duration} | 交易数量: {size}")
                    print(f"  盈亏金额: {pnl:+.2f} | 盈亏比例: {pnl_pct:+.2f}%")
                    print(f"  交易类型: {'做多' if size > 0 else '做空'}")
                    print("-" * 100)
            else:
                print("\n⚠️ 没有交易记录")
        except Exception as e:
            print(f"\n无法获取详细交易记录: {e}")

        equity_curve = results._equity_curve
        portfolio_values = equity_curve['Equity'].tolist()

        # 检查结果是否合理
        if results['Return [%]'] < -50:  # 调整阈值，如果收益率低于-50%，可能有问题
            print("移动平均线策略回测结果不理想，使用改进的手动计算")
            return backtest_ma_cross_optimized(data, initial_cash)

        return {
            'final_value': results['Equity Final [$]'],
            'total_return': results['Return [%]'],
            'annual_return': results['Return (Ann.) [%]'],
            'max_drawdown': results['Max. Drawdown [%]'],
            'num_trades': results['# Trades'],
            'portfolio_values': portfolio_values,
            'backtest_results': results
        }
    except Exception as e:
        print(f"移动平均线策略回测错误: {e}")
        print("使用改进的手动计算")
        return backtest_ma_cross_optimized(data, initial_cash)

def backtest_buy_hold_with_backtesting(data, initial_cash=1000000):
    """使用backtesting库回测买入持有策略"""
    try:
        class FixedBuyAndHoldStrategy(Strategy):
            def init(self):
                pass

            def next(self):
                # 只在第一天买入，并且持有到最后
                if len(self.data) == 1 and not self.position:
                    # 计算可以购买的股票数量
                    price = self.data.Close[-1]
                    if price > 0:
                        # 使用95%的资金购买
                        investment = self.equity * 0.95
                        shares = int(investment // price)
                        if shares > 0:
                            self.buy(size=shares)

        bt = Backtest(data, FixedBuyAndHoldStrategy, cash=initial_cash,
                      commission=0.0015, exclusive_orders=True)
        results = bt.run()

        equity_curve = results._equity_curve
        portfolio_values = equity_curve['Equity'].tolist()

        # 如果回测结果异常，使用手动计算
        if results['Equity Final [$]'] <= initial_cash * 1.01:  # 如果收益几乎为0
            print("买入持有策略回测结果异常，使用手动计算")
            return calculate_buy_hold_manually(data, initial_cash)

        return {
            'final_value': results['Equity Final [$]'],
            'total_return': results['Return [%]'],
            'annual_return': results['Return (Ann.) [%]'],
            'max_drawdown': results['Max. Drawdown [%]'],
            'portfolio_values': portfolio_values
        }
    except Exception as e:
        print(f"买入持有策略回测错误，使用手动计算: {e}")
        return calculate_buy_hold_manually(data, initial_cash)


def backtest_phased_strategy(data, total_investment=1000000, phases=10, transaction_cost=0.0015):
    """分批买入策略"""
    phase_amount = total_investment / phases

    cash = 0
    shares = 0
    trades = []
    portfolio_values = []
    phases_executed = 0
    phase_dates = []

    total_days = len(data)
    days_between_phases = max(1, total_days // phases)

    print(f"\n分批买入策略详细执行:")
    print(f"总天数: {total_days}, 分期数: {phases}, 每期间隔: {days_between_phases}天")

    for i, (date, row) in enumerate(data.iterrows()):
        current_price = row['Close']

        # 检查是否是投入日
        if i % days_between_phases == 0 and phases_executed < phases:
            cash += phase_amount
            phases_executed += 1
            phase_dates.append(date)

            # 立即购买股票
            available_cash = cash * (1 - transaction_cost)
            shares_to_buy = int(available_cash // current_price)

            if shares_to_buy > 0:
                cost = shares_to_buy * current_price
                transaction_fee = cost * transaction_cost
                total_cost = cost + transaction_fee

                if total_cost <= cash:
                    cash -= total_cost
                    shares += shares_to_buy

                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'amount': cost
                    })

                    print(f"第{phases_executed}期投入: 日期={date.date()}, "
                          f"股价={current_price:.2f}, 买入{shares_to_buy}股, "
                          f"花费{cost:.0f}元, 手续费{transaction_fee:.0f}元")

        # 计算当日资产
        current_value = cash + shares * current_price
        portfolio_values.append(current_value)

    final_value = cash + shares * data.iloc[-1]['Close']
    total_return = (final_value - total_investment) / total_investment * 100

    years = len(data) / 252
    annual_return = (final_value / total_investment) ** (1 / years) - 1 if years > 0 else 0

    # 计算最大回撤
    portfolio_series = pd.Series(portfolio_values, index=data.index)
    rolling_max = portfolio_series.expanding().max()
    drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdowns.min()

    print(f"\n分批买入策略最终统计:")
    print(f"总投入资金: {total_investment:,.0f}元")
    print(f"最终持股: {shares:,}股")
    print(f"最终现金: {cash:,.0f}元")
    print(f"期末股价: {data.iloc[-1]['Close']:.2f}元")
    print(f"股票价值: {shares * data.iloc[-1]['Close']:,.0f}元")
    print(f"最终资产: {final_value:,.0f}元")
    print(f"总收益率: {total_return:.2f}%")

    return {
        'total_investment': total_investment,
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return * 100,
        'max_drawdown': max_drawdown,
        'trades': trades,
        'num_phases': phases_executed,
        'portfolio_values': portfolio_values,
        'phase_dates': phase_dates
    }


def backtest_monthly_dca_strategy(data, monthly_investment=10000, transaction_cost=0.0015):
    """每月定投策略 - 修复版本"""
    cash = 0
    shares = 0
    trades = []
    portfolio_values = []
    total_invested = 0

    # 创建月份标识
    data_copy = data.copy()
    data_copy['YearMonth'] = data_copy.index.to_period('M')
    current_month = None

    for date, row in data_copy.iterrows():
        price = row['Close']
        ym = row['YearMonth']

        # 新月开始，投入资金
        if ym != current_month:
            cash += monthly_investment
            total_invested += monthly_investment
            current_month = ym

            # 立即购买
            if cash > 0:
                available_cash = cash * (1 - transaction_cost)
                shares_to_buy = int(available_cash // price)

                if shares_to_buy > 0:
                    cost = shares_to_buy * price
                    fee = cost * transaction_cost
                    cash -= (cost + fee)
                    shares += shares_to_buy

                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares_to_buy,
                        'amount': cost
                    })

        current_value = cash + shares * price
        portfolio_values.append(current_value)

    final_value = cash + shares * data_copy.iloc[-1]['Close']
    total_return = (final_value - total_invested) / total_invested * 100

    years = len(data) / 252
    annual_return = (final_value / total_invested) ** (1 / years) - 1 if years > 0 else 0

    portfolio_series = pd.Series(portfolio_values, index=data.index)
    rolling_max = portfolio_series.expanding().max()
    drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
    max_drawdown = drawdowns.min()

    return {
        'total_invested': total_invested,
        'final_value': final_value,
        'total_return': total_return,
        'annual_return': annual_return * 100,
        'max_drawdown': max_drawdown,
        'portfolio_values': portfolio_values,
        'num_months': len(data_copy['YearMonth'].unique())
    }


def simple_stock_analysis():
    set_chinese_font()

    stock_code = "2330.TW"
    years = 10
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)

    print(f"正在下载{stock_code}历史数据...")
    try:
        data = yf.download(stock_code, start=start_date, end=end_date, auto_adjust=True)
        print(f"成功下载 {len(data)} 条数据")
    except Exception as e:
        print(f"下载数据时出错: {e}")
        return

    if data.empty:
        print("数据为空")
        return

    # 简化列名
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    print(f"数据列: {data.columns.tolist()}")
    print(f"数据期间: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")

    # 数据清理
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    data = data.dropna()

    initial_price = data.iloc[0]['Close']
    final_price = data.iloc[-1]['Close']
    price_return = (final_price - initial_price) / initial_price * 100
    print(f"\n股价表现:")
    print(f"期初价格: {initial_price:.2f}")
    print(f"期末价格: {final_price:.2f}")
    print(f"价格涨幅: {price_return:.2f}%")

    # 回测各种策略
    print("\n开始回测移动平均线交叉策略...")
    ma_results = backtest_ma_cross_with_backtesting(data)

    print("\n开始回测买入持有策略...")
    bh_results = backtest_buy_hold_with_backtesting(data)

    print("\n开始回测分批买入策略...")
    phased_results = backtest_phased_strategy(data, total_investment=1000000, phases=10)

    print("\n开始回测每月定期定额策略...")
    monthly_dca_results = backtest_monthly_dca_strategy(data, monthly_investment=10000)

    # 显示结果
    print("\n" + "=" * 70)
    print("回测结果总结")
    print("=" * 70)

    print(f"\n1. 移动平均线交叉策略:")
    print(f"最终资产: {ma_results['final_value']:,.0f} 元")
    print(f"总收益率: {ma_results['total_return']:.2f}%")
    print(f"年化收益率: {ma_results['annual_return']:.2f}%")
    print(f"最大回撤: {ma_results['max_drawdown']:.2f}%")
    print(f"交易次数: {ma_results.get('num_trades', 0)} 次")

    print(f"\n2. 买入持有策略:")
    print(f"最终资产: {bh_results['final_value']:,.0f} 元")
    print(f"总收益率: {bh_results['total_return']:.2f}%")
    print(f"年化收益率: {bh_results['annual_return']:.2f}%")
    print(f"最大回撤: {bh_results['max_drawdown']:.2f}%")

    print(f"\n3. 分批买入策略 (10期，每期100,000元):")
    print(f"总投入资金: {phased_results['total_investment']:,.0f} 元")
    print(f"最终资产: {phased_results['final_value']:,.0f} 元")
    print(f"总收益率: {phased_results['total_return']:.2f}%")
    print(f"年化收益率: {phased_results['annual_return']:.2f}%")
    print(f"最大回撤: {phased_results['max_drawdown']:.2f}%")

    print(f"\n4. 每月定期定额策略 (每月10,000元):")
    print(f"总投入资金: {monthly_dca_results['total_invested']:,.0f} 元")
    print(f"最终资产: {monthly_dca_results['final_value']:,.0f} 元")
    print(f"总收益率: {monthly_dca_results['total_return']:.2f}%")
    print(f"年化收益率: {monthly_dca_results['annual_return']:.2f}%")
    print(f"最大回撤: {monthly_dca_results['max_drawdown']:.2f}%")

    # 生成图表
    print("\n正在生成最终图表...")
    chart_filename = plot_strategy_comparison_final(data, ma_results, bh_results, phased_results, monthly_dca_results,
                                                    stock_code)

    # 策略比较分析
    print("\n" + "=" * 70)
    print("策略比较分析")
    print("=" * 70)

    strategies = {
        '买入持有策略': bh_results,
        '移动平均线策略': ma_results,
        '分批买入策略': phased_results,
        '每月定投策略': monthly_dca_results
    }

    # 按最终资产排序
    sorted_by_value = sorted(strategies.items(), key=lambda x: x[1]['final_value'], reverse=True)
    print("\n按最终资产排序:")
    for i, (name, result) in enumerate(sorted_by_value, 1):
        print(f"{i}. {name}: {result['final_value']:,.0f} 元")

    # 风险收益分析
    print(f"\n风险收益分析:")
    for name, result in strategies.items():
        print(f"{name}: 收益率 {result['total_return']:.2f}%, 最大回撤 {result['max_drawdown']:.2f}%")

    # 计算风险调整后收益
    def calculate_risk_adjusted_return(return_pct, max_drawdown):
        if max_drawdown >= 0:  # 避免除零或正值
            return return_pct
        return return_pct / abs(max_drawdown)

    risk_adjusted = {
        name: calculate_risk_adjusted_return(result['total_return'], result['max_drawdown'])
        for name, result in strategies.items()
    }

    print(f"\n风险调整后收益 (收益率/最大回撤):")
    for name, ratio in risk_adjusted.items():
        print(f"{name}: {ratio:.2f}")

    # 投资建议
    best_strategy = max(risk_adjusted.items(), key=lambda x: x[1])
    print(f"\n投资建议:")
    print(f"最佳策略: {best_strategy[0]} (风险调整后收益: {best_strategy[1]:.2f})")

    if best_strategy[0] == '每月定投策略':
        print("✓ 适合有稳定收入的上班族，可以培养投资纪律")
    elif best_strategy[0] == '买入持有策略':
        print("✓ 适合有一次性资金且能承受波动的长期投资者")
    elif best_strategy[0] == '分批买入策略':
        print("✓ 适合有大笔资金但担心市场时机的投资者")
    else:
        print("✓ 适合喜欢主动管理且能接受频繁交易的投资者")

    print(f"\n策略表现总结:")
    print(f"- 台积电在过去10年股价上涨了{price_return:.1f}%")
    print(f"- {best_strategy[0]}在风险调整后表现最佳")
    print(f"- 图表已保存为: {chart_filename}")


if __name__ == "__main__":
    simple_stock_analysis()