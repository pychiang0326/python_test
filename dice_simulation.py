import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --- 模擬參數 ---
num_dice = 100       # 每次實驗擲骰子的數量 (使用者指定的100次)
num_simulations = 10000 # 總共重複實驗的次數
num_sides = 6        # 骰子的面數

# --- 執行模擬 ---
# 建立一個空列表來儲存每次實驗的結果 (總和)
sums = []

# 迴圈執行 N 次模擬
for _ in range(num_simulations):
# 一次擲出 num_dice 顆骰子，結果是一個包含每個骰子點數的陣列
     rolls = np.random.randint(1, num_sides + 1, size=num_dice)
# 計算這100顆骰子的總和並存入列表中
     sums.append(np.sum(rolls))

# --- 繪製結果 ---
# 設定中文字體，以避免亂碼 (如果您的系統沒有 'Microsoft JhengHei'，可以換成 'SimHei'或其他支援中文的字體)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
plt.rcParams['axes.unicode_minus'] = False
# 使用 seaborn 來繪製直方圖和核密度估計曲線 (KDE)
plt.figure(figsize=(12, 7))
sns.histplot(sums, kde=True, stat="density", bins=30)

# 計算理論上的平均值和標準差
mean = np.mean(sums)
std_dev = np.std(sums)

# 加上標題和標籤
plt.title(f'擲 {num_dice} 顆骰子 {num_simulations} 次的點數總和分佈')
plt.xlabel(f'{num_dice} 顆骰子的點數總和')
plt.ylabel('機率密度')
plt.grid(True)

# 在圖上標示平均值和標準差
plt.axvline(mean, color='r', linestyle='--', label=f'平均值: {mean:.2f}')
plt.legend()

# 顯示圖表
plt.show()