def find_min(arr):
    min_index = 0
    for i in range(len(arr) - 1):
        if arr[i] < arr[min_index]:
            min_index = i
    return min_index


list1 = [10, 6, 5, 4, 2, 11]
m_index = find_min(list1)
print(f"minimal index = {m_index}")
min_value = list1[m_index]
print(f"minimal value = {min_value}")
