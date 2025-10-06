import mplfinance as mpf
import yfinance as yf

# 获取台积电（TSM）的历史数据
data = yf.download('2330.TW', start='2005-01-01', end='2025-02-21')  # 调整结束日期为当前日期

# 重置多级索引，将多级索引转换为单级索引
data.columns = data.columns.get_level_values(0)  # 取第一层索引作为列名

# 将日线数据转换为季线数据
quarterly_data = data.resample('QE').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# 确保列名正确（首字母大写）
print("季度数据列名:", quarterly_data.columns)

# 自定义样式（强制指定字体）
style = mpf.make_mpf_style(
    base_mpf_style='yahoo',
    facecolor='#fafafa',
    gridcolor='#e0e0e0',
    rc={'font.family': 'Microsoft YaHei'}
)

# 绘制季K线图（逐步调试参数）
mpf.plot(
    quarterly_data,
    type='candle',
    title='台积电（TSM）近20年季K线图',
    style=style,
    volume=True,
    #mav=(3, 6, 9),
    show_nontrading=False  # 确保不显示非交易日
)