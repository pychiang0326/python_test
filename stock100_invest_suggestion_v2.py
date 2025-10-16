import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from matplotlib import font_manager
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def read_and_process_data(file_path):
    """读取并处理股票数据"""
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        print(f"正在读取文件: {file_path}")

        # 根据文件扩展名选择引擎
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.xls':
            # 对于.xls文件，尝试使用xlrd引擎
            try:
                df = pd.read_excel(file_path, sheet_name='Sheet1', engine='xlrd')
            except ImportError:
                print("请安装xlrd库: pip install xlrd")
                return None
            except Exception as e:
                print(f"使用xlrd读取失败: {e}")
                # 尝试使用openpyxl作为备选
                try:
                    df = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')
                except Exception as e2:
                    print(f"使用openpyxl读取也失败: {e2}")
                    return None
        elif file_ext == '.xlsx':
            # 对于.xlsx文件，使用openpyxl引擎
            try:
                df = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')
            except ImportError:
                print("请安装openpyxl库: pip install openpyxl")
                return None
        else:
            print(f"不支持的文件格式: {file_ext}")
            return None

        print(f"成功读取 {len(df)} 只股票数据")
        print(f"实际列名: {df.columns.tolist()}")

        # 数据清洗和处理
        df = df.replace('-', np.nan)
        df = df.replace('', np.nan)

        # 标准化列名 - 处理特殊字符和空格
        column_mapping = {}
        for col in df.columns:
            # 移除特殊字符并标准化列名
            clean_col = re.sub(r'[?]', '', col)  # 移除问号
            clean_col = clean_col.strip()  # 移除前后空格
            column_mapping[col] = clean_col

        # 应用列名映射
        df = df.rename(columns=column_mapping)
        print(f"标准化后列名: {df.columns.tolist()}")

        # 转换数值列
        numeric_columns = ['成交', 'PER', 'PEG▼', 'PBR', '最新年度營收增減(%)',
                           '最新年度每股盈餘增減(%)', '最新年度ROE(%)', '最新年度毛利率(%)',
                           '最新年度營益率(%)', '最新年度自由金流(億)', '最新年度負債總額佔比(%)',
                           '最新年度流動資產對流動負債(%)', '最新年度利息保障倍數']

        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 确保代號列是字符串类型
        if '代號' in df.columns:
            df['代號'] = df['代號'].astype(str)

        return df

    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None


def calculate_investment_score(df):
    """计算投资评分"""
    scores = []

    for _, stock in df.iterrows():
        score = 0

        # PEG评分 (越低越好，负值扣分)
        # 使用标准化的列名 'PEG▼'
        if pd.notna(stock['PEG▼']):
            if stock['PEG▼'] > 0 and stock['PEG▼'] < 1:
                score += 30
            elif stock['PEG▼'] >= 1 and stock['PEG▼'] < 2:
                score += 15
            elif stock['PEG▼'] < 0:
                score -= 10

        # 营收增长评分
        if pd.notna(stock['最新年度營收增減(%)']):
            if stock['最新年度營收增減(%)'] > 20:
                score += 20
            elif stock['最新年度營收增減(%)'] > 10:
                score += 10
            elif stock['最新年度營收增減(%)'] < 0:
                score -= 5

        # EPS增长评分
        if pd.notna(stock['最新年度每股盈餘增減(%)']):
            if stock['最新年度每股盈餘增減(%)'] > 30:
                score += 20
            elif stock['最新年度每股盈餘增減(%)'] > 10:
                score += 10
            elif stock['最新年度每股盈餘增減(%)'] < 0:
                score -= 5

        # ROE评分
        if pd.notna(stock['最新年度ROE(%)']):
            if stock['最新年度ROE(%)'] > 20:
                score += 15
            elif stock['最新年度ROE(%)'] > 10:
                score += 8
            elif stock['最新年度ROE(%)'] < 0:
                score -= 10

        # 自由现金流评分
        if pd.notna(stock['最新年度自由金流(億)']):
            if stock['最新年度自由金流(億)'] > 0:
                score += 10
            else:
                score -= 5

        # 负债比率评分 (越低越好)
        if pd.notna(stock['最新年度負債總額佔比(%)']):
            if stock['最新年度負債總額佔比(%)'] < 40:
                score += 10
            elif stock['最新年度負債總額佔比(%)'] > 60:
                score -= 5

        scores.append(score)

    df['投资评分'] = scores
    return df


def create_investment_portfolio(df):
    """创建投资组合"""

    # 定义各类别股票
    ai_semiconductor = ['2330', '2454', '2303', '3711', '3034', '2379']
    green_energy = ['6806', '6443', '1513', '1519', '8374']
    electronic_components = ['2308', '2327', '6271', '3044', '2313']
    value_stocks = ['2891', '2886', '5880', '2890', '2603']

    # old
    # ai_semiconductor = ['2330', '2454', '3017', '2382', '3711']
    # green_energy = ['1519', '1513', '6806']
    # electronic_components = ['3044', '2308', '2313']
    # value_stocks = ['2603', '2618', '2891']

    portfolio = {}

    # 核心持仓筛选 (AI/半导体)
    core_stocks = df[df['代號'].astype(str).isin(ai_semiconductor)].copy()
    if len(core_stocks) > 0:
        core_stocks = core_stocks.nlargest(max(3, len(core_stocks)), '投资评分')
        portfolio['核心持仓'] = core_stocks

    # 辅助持仓筛选 (绿能+电子零组件)
    auxiliary_stocks = df[df['代號'].astype(str).isin(green_energy + electronic_components)].copy()
    if len(auxiliary_stocks) > 0:
        auxiliary_stocks = auxiliary_stocks.nlargest(max(3, len(auxiliary_stocks)), '投资评分')
        portfolio['辅助持仓'] = auxiliary_stocks

    # 价值型持仓筛选
    value_stocks_df = df[df['代號'].astype(str).isin(value_stocks)].copy()
    if len(value_stocks_df) > 0:
        value_stocks_df = value_stocks_df.nlargest(max(2, len(value_stocks_df)), '投资评分')
        portfolio['价值型持仓'] = value_stocks_df

    return portfolio


def plot_radar_chart(portfolio):
    """绘制投资组合雷达图"""

    if not portfolio:
        print("投资组合为空，无法绘制雷达图")
        return

    # 准备数据
    categories = ['估值吸引力', '成长性', '盈利能力', '财务健康', '现金流']

    # 计算需要多少个子图
    num_categories = len(portfolio)
    if num_categories == 0:
        return

    fig, axes = plt.subplots(1, num_categories, figsize=(5 * num_categories, 5))
    if num_categories == 1:
        axes = [axes]

    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']

    for idx, (category, stocks) in enumerate(portfolio.items()):
        ax = axes[idx]

        for stock_idx, (_, stock) in enumerate(stocks.iterrows()):
            if stock_idx >= 3:  # 每个类别只显示前3只股票
                break

            # 计算各项指标 (标准化到0-1)
            values = []

            # 估值吸引力 (基于PEG和PER)
            # 使用标准化的列名 'PEG▼'
            if pd.notna(stock['PEG▼']) and stock['PEG▼'] > 0:
                peg_score = max(0, min(1, 1 / stock['PEG▼']))
            else:
                peg_score = 0
            values.append(peg_score)

            # 成长性 (基于营收和EPS增长)
            growth_score = 0
            if pd.notna(stock['最新年度營收增減(%)']):
                growth_score += min(1, stock['最新年度營收增減(%)'] / 50)
            if pd.notna(stock['最新年度每股盈餘增減(%)']):
                growth_score += min(1, stock['最新年度每股盈餘增減(%)'] / 50)
            values.append(min(1, growth_score / 2))

            # 盈利能力 (基于ROE和毛利率)
            profit_score = 0
            if pd.notna(stock['最新年度ROE(%)']):
                profit_score += min(1, stock['最新年度ROE(%)'] / 30)
            if pd.notna(stock['最新年度毛利率(%)']):
                profit_score += min(1, stock['最新年度毛利率(%)'] / 50)
            values.append(min(1, profit_score / 2))

            # 财务健康 (基于负债比率和流动比率)
            health_score = 0
            if pd.notna(stock['最新年度負債總額佔比(%)']):
                health_score += max(0, 1 - stock['最新年度負債總額佔比(%)'] / 100)
            if pd.notna(stock['最新年度流動資產對流動負債(%)']):
                health_score += min(1, stock['最新年度流動資產對流動負債(%)'] / 200)
            values.append(min(1, health_score / 2))

            # 现金流
            if pd.notna(stock['最新年度自由金流(億)']):
                cashflow_score = min(1, max(0, stock['最新年度自由金流(億)'] / 100))
            else:
                cashflow_score = 0
            values.append(cashflow_score)

            # 闭合雷达图
            values = values + [values[0]]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]

            ax.plot(angles, values, 'o-', linewidth=2,
                    label=f"{stock['名稱']}({stock['代號']})", color=colors[stock_idx])
            ax.fill(angles, values, alpha=0.1, color=colors[stock_idx])

        ax.set_ylim(0, 1)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_title(f'{category} - 特性分析', size=14, fontweight='bold')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

    plt.tight_layout()
    plt.show()


def plot_investment_pie_chart(portfolio):
    """绘制投资比例饼图"""

    if not portfolio:
        print("投资组合为空，无法绘制饼图")
        return {}

    # 设置投资比例
    allocation = {
        '核心持仓': 60,
        '辅助持仓': 30,
        '价值型持仓': 10
    }

    # 只保留有股票的类别
    allocation = {k: v for k, v in allocation.items() if k in portfolio}

    # 计算各股票在类别内的权重 (基于投资评分)
    stock_allocation = {}

    for category, stocks in portfolio.items():
        total_score = stocks['投资评分'].sum()
        category_weight = allocation.get(category, 0)

        for _, stock in stocks.iterrows():
            stock_key = f"{stock['名稱']}({stock['代號']})"
            stock_weight = (stock['投资评分'] / total_score) * category_weight
            stock_allocation[stock_key] = stock_weight

    # 绘制饼图
    if len(allocation) > 1:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    else:
        fig, ax2 = plt.subplots(1, 1, figsize=(8, 8))
        ax1 = None

    # 类别比例饼图 (如果有多个类别)
    if ax1 is not None:
        categories = list(allocation.keys())
        sizes = list(allocation.values())
        colors = ['#ff9999', '#66b3ff', '#99ff99']

        ax1.pie(sizes, labels=categories, autopct='%1.1f%%', colors=colors[:len(categories)], startangle=90)
        ax1.set_title('投资组合 - 类别分配比例', fontsize=14, fontweight='bold')

    # 个股比例饼图
    stock_labels = list(stock_allocation.keys())
    stock_sizes = list(stock_allocation.values())

    if ax1 is not None:
        ax2.pie(stock_sizes, labels=stock_labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title('投资组合 - 个股分配比例', fontsize=14, fontweight='bold')
    else:
        ax2.pie(stock_sizes, labels=stock_labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title('投资组合 - 个股分配比例', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.show()

    return stock_allocation


def display_portfolio_details(portfolio, stock_allocation):
    """显示投资组合详情"""

    print("=" * 80)
    print("2025年下半年台股投资组合建议")
    print("=" * 80)

    if not portfolio:
        print("投资组合为空")
        return

    total_investment = 0
    for category, stocks in portfolio.items():
        allocation_pct = get_allocation_percentage(category)
        print(f"\n{category} (目标比例: {allocation_pct}%):")
        print("-" * 50)

        for _, stock in stocks.iterrows():
            stock_key = f"{stock['名稱']}({stock['代號']})"
            allocation = stock_allocation.get(stock_key, 0)
            total_investment += allocation

            print(f"  股票: {stock['名稱']} ({stock['代號']})")
            print(f"  产业: {stock['產業別']}")
            print(f"  建议权重: {allocation:.1f}%")
            print(f"  投资评分: {stock['投资评分']}")

            # 显示关键指标
            key_metrics = []
            # 使用标准化的列名 'PEG▼'
            if pd.notna(stock['PEG▼']):
                key_metrics.append(f"PEG: {stock['PEG▼']:.2f}")
            if pd.notna(stock['最新年度營收增減(%)']):
                key_metrics.append(f"营收增长: {stock['最新年度營收增減(%)']:.1f}%")
            if pd.notna(stock['最新年度ROE(%)']):
                key_metrics.append(f"ROE: {stock['最新年度ROE(%)']:.1f}%")

            print(f"  关键指标: {', '.join(key_metrics)}")
            print()


def get_allocation_percentage(category):
    """获取类别分配百分比"""
    allocation_map = {
        '核心持仓': 60,
        '辅助持仓': 30,
        '价值型持仓': 10
    }
    return allocation_map.get(category, 0)


def main():
    """主函数"""

    # 读取数据 - 使用原始字符串避免转义问题
    file_path = r"C:\Users\Raymond\Desktop\D data\pytjhon_test\Stock.xls"
    df = read_and_process_data(file_path)

    if df is None:
        print("无法读取数据文件，请检查文件路径")
        return

    # 计算投资评分
    df = calculate_investment_score(df)

    # 创建投资组合
    portfolio = create_investment_portfolio(df)

    if not portfolio:
        print("无法创建投资组合，请检查数据")
        return

    # 绘制雷达图
    print("生成投资组合特性雷达图...")
    plot_radar_chart(portfolio)

    # 绘制饼图并获取分配比例
    print("生成投资比例饼图...")
    stock_allocation = plot_investment_pie_chart(portfolio)

    # 显示投资组合详情
    display_portfolio_details(portfolio, stock_allocation)

    # 显示整体统计数据
    print("\n" + "=" * 80)
    print("投资组合整体统计")
    print("=" * 80)

    all_stocks = []
    for category_stocks in portfolio.values():
        all_stocks.extend(category_stocks.to_dict('records'))

    if all_stocks:
        # 计算平均值，忽略NaN值
        # 使用标准化的列名 'PEG▼'
        peg_values = [s.get('PEG▼') for s in all_stocks if pd.notna(s.get('PEG▼'))]
        revenue_values = [s.get('最新年度營收增減(%)') for s in all_stocks if pd.notna(s.get('最新年度營收增減(%)'))]
        roe_values = [s.get('最新年度ROE(%)') for s in all_stocks if pd.notna(s.get('最新年度ROE(%)'))]

        if peg_values:
            avg_peg = np.mean(peg_values)
            print(f"平均PEG: {avg_peg:.2f}")
        else:
            print("平均PEG: 无数据")

        if revenue_values:
            avg_revenue_growth = np.mean(revenue_values)
            print(f"平均营收增长率: {avg_revenue_growth:.1f}%")
        else:
            print("平均营收增长率: 无数据")

        if roe_values:
            avg_roe = np.mean(roe_values)
            print(f"平均ROE: {avg_roe:.1f}%")
        else:
            print("平均ROE: 无数据")

        print(f"投资组合股票数量: {len(all_stocks)}")


if __name__ == "__main__":
    main()