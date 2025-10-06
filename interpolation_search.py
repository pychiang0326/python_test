def interpolation_search(arr, key):
    low = 0
    high = len(arr) - 1

    while low <= high and key >= arr[low] and key <= arr[high]:
        if low == high:
            if arr[low] == key:
                return low
            return -1

        # 使用插值公式計算中間索引
        mid = low + (high - low) * (key - arr[low]) // (arr[high] - arr[low])

        if arr[mid] == key:
            return mid
        elif arr[mid] < key:
            low = mid + 1
        else:
            high = mid - 1

    return -1  # 未找到

# 測試代碼
if __name__ == "__main__":
    import random

    # 生成隨機數組並排序
    data = [random.randint(1, 150) for _ in range(50)]
    data.sort()

    print("排序後的數組:", data)

    while True:
        key = int(input("請輸入搜尋值(1-150)，輸入-1結束: "))
        if key < 0:
            break

        index = interpolation_search(data, key)
        if index >= 0:
            print(f"在第 {index} 個位置找到 (data[{index}]={data[index]}).")
        else:
            print(f"##### 沒有找到 {key} #####")