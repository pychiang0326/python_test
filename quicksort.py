def quicksort(arr):
    # 如果陣列長度小於等於1，直接回傳（已排序）
    if len(arr) <= 1:
        return arr

    # 選擇基準點，這裡以陣列第一個元素為基準
    pivot = arr[0]

    # 分割成三個子陣列：小於基準、等於基準、大於基準
    less = [x for x in arr[1:] if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr[1:] if x > pivot]

    # 遞迴排序 less 和 greater，並合併結果
    return quicksort(less) + equal + quicksort(greater)


# 範例測試
#sample = [33, 10, 55, 71, 29, 3, 18]
sample = [33, 10, 55]
sorted_list = quicksort(sample)
print("排序前:", sample)
print("排序後:", sorted_list)
