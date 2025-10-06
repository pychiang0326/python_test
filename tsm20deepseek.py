import mplfinance as mpf
import yfinance as yf
import matplotlib.pyplot as plt

# 1. 獲取數據（使用台積電美股代碼 TSM）
data = yf.download('2330.TW', start='2005-01-01', end='2025-02-21')

# 2. 重置多级索引，将多级索引转换为单级索引
data.columns = data.columns.get_level_values(0)  # 取第一层索引作为列名

#檢查列名（無需重置索引）
print("原始數據列名:", data.columns)

# 3. 轉換日線數據為季線數據
quarterly_data = data.resample('QE').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).dropna()

# 4. 檢查季度數據列名和內容
print("季度數據列名:", quarterly_data.columns)
print("季度數據前5行:\n", quarterly_data.head())

# 5. 配置中文字體（使用 SimHei）
plt.rcParams['font.sans-serif'] = ['SimHei']  # 通用中文字體
plt.rcParams['axes.unicode_minus'] = False    # 解決負號顯示問題

# 6. 自定義樣式
style = mpf.make_mpf_style(
    base_mpf_style='yahoo',
    facecolor='#fafafa',
    gridcolor='#e0e0e0',
    rc={'font.family': 'SimHei'}  # 同步修改字體
)

# 7. 繪製季K線圖
mpf.plot(
    quarterly_data,
    type='candle',
    title='台積電（2330.TW）近20年季K線圖',
    style=style,
    volume=True,
    mav=(3, 6, 9),
    show_nontrading=False
)