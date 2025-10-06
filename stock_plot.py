import twstock
import pandas as pd
# 導入twstock及pandas模組，pandas模組縮寫為pd
import matplotlib
import mplfinance as mpf
# 導入pandas、matplotlib、mplfinance模組，將mplfinance模組縮寫為mpf
# 這邊要導入matplotlib的原因是因為mplfinance繪圖時需要調用mptplotlib模組
import sys


# 檢查是否有股票代號
if len(sys.argv) < 2:
    print("請輸入股票代號")
    sys.exit("程式結束")
    
target_stock=sys.argv[1]
  
#target_stock = '00929'  #股票代號變數
stock = twstock.Stock(target_stock)  #告訴twstock我們要查詢的股票
target_price = stock.fetch_from(2023, 5)  #取用2020/05至今每天的交易資料

name_attribute = [
    'Date', 'Capacity', 'Turnover', 'Open', 'High', 'Low', 'Close', 'Change',
    'Transcation'
]  #幫收集到的資料設定表頭[日期 總成交股數 總成交金額(Volume) 開 高 低 收 漲跌幅 成交量]

df = pd.DataFrame(columns=name_attribute, data=target_price)
#將twstock抓到的清單轉成Data Frame格式的資料表

filename = f'./data/{target_stock}.csv'
#指定Data Frame轉存csv檔案的檔名與路徑

df.to_csv(filename)
#將Data Frame轉存為csv檔案

df = pd.read_csv(f'./data/{target_stock}.csv', parse_dates=True, index_col=1) #讀取目標股票csv檔的位置

df.rename(columns={'Turnover':'Volume'}, inplace = True)
#這裡針對資料表做一下修正，因為交易量(Turnover)在mplfinance中須被改為Volume才能被認出來

mc = mpf.make_marketcolors(up='r',down='g',inherit=True)
s  = mpf.make_mpf_style(base_mpf_style='yahoo',marketcolors=mc)
#針對線圖的外觀微調，將上漲設定為紅色，下跌設定為綠色，符合台股表示習慣
#接著把自訂的marketcolors放到自訂的style中，而這個改動是基於預設的yahoo外觀

kwargs = dict(type='candle', mav=(5,20,60), volume=True, figratio=(10,8), figscale=0.75, title=target_stock, style=s)
#設定可變參數kwargs，並在變數中填上繪圖時會用到的設定值

mpf.plot(df, **kwargs)
#選擇df資料表為資料來源，帶入kwargs參數，畫出目標股票的走勢圖