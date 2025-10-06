import os
import datetime

# 設定搜尋的根目錄
root_dir = 'C:\\Users\\Raymond\\Desktop'  # 替換為你的目錄路徑

# 設定特定日期
specific_date = datetime.datetime(2024, 12, 28)  # 替換為你想要的日期

# 遍歷目錄及子目錄
for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        try:
            # 獲取檔案的最後修改時間
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            # 檢查檔案是否在特定日期之後被修改
            if mod_time > specific_date:
                print(f'檔案: {file_path}, 異動時間: {mod_time}')
        except FileNotFoundError:
            print(f'檔案未找到: {file_path}')
        except Exception as e:
            print(f'處理檔案 {file_path} 時發生錯誤: {e}')
