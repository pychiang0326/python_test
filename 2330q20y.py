import mplfinance as mpf
import yfinance as yf
import matplotlib.pyplot as plt

# ==== 强制中文字体配置 ====
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # Windows系统
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac系统
plt.rcParams['axes.unicode_minus'] = False

# 获取台积电（2330）的历史数据
data = yf.download('2330.TW', start='2005-01-01', end='2025-02-23')

# 检查数据结构
print(data.head())
print(data.columns)

# 重置多级索引，将多级索引转换为单级索引
data.columns = data.columns.get_level_values(0)  # 取第一层索引作为列名

# 自定义样式（强制指定字体）
style = mpf.make_mpf_style(
    base_mpf_style='yahoo',
    facecolor='#fafafa',
    gridcolor='#e0e0e0',
    rc={'font.family': 'Microsoft YaHei'}
)

# 将日线数据转换为季线数据
quarterly_data = data.resample('QE').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

# 删除空值行
quarterly_data = quarterly_data.dropna()

# 绘图
mpf.plot(quarterly_data, type='candle', title='台积电（2330）近20年季K线图', style= style, volume=True, mav=(3, 6, 9))