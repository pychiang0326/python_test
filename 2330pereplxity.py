import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

# 下載台積電的歷史股價資料
data = yf.download('2330.TW', period='20y')

# 檢查資料欄位名稱
print(data.columns)

# 重塑資料結構（如果需要）
close = data[('Close', '2330.TW')]
high = data[('High', '2330.TW')]
low = data[('Low', '2330.TW')]
open_price = data[('Open', '2330.TW')]
volume = data[('Volume', '2330.TW')]

# 建立新的DataFrame
data_new = pd.DataFrame({
    'Close': close,
    'High': high,
    'Low': low,
    'Open': open_price,
    'Volume': volume
})

# 計算季度資料
data_new['Quarter'] = data_new.index.to_period('Q')

# 將資料轉換為季度資料
quarterly_data = data_new.groupby('Quarter').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
}).reset_index()

# 設定正確的索引
quarterly_data['Quarter'] = pd.to_datetime(quarterly_data['Quarter'].apply(lambda x: x.to_timestamp()))
quarterly_data.set_index('Quarter', inplace=True)

# 設定中文字型
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 自定義樣式
s = mpf.make_mpf_style(base_mpf_style='yahoo', rc={
    'font.family': 'SimHei',
    'axes.unicode_minus': False
})

# 繪製季度K線圖
mpf.plot(quarterly_data, type='candle', title='台積電（2330.TW）近20年季度K線圖', ylabel='價格', ylabel_lower='交易量', volume=True, style=s)
