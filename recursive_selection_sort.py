def recursive_selection_sort(arr, start=0):
    n = len(arr)
    if start >= n - 1:
        return
    # Find the index of the minimum element in arr[start:]
    min_index = start
    for i in range(start + 1, n):
        if arr[i] < arr[min_index]:
            min_index = i
    # Swap the found minimum element with the first element
    arr[start], arr[min_index] = arr[min_index], arr[start]
    # Recursively call selection sort on the remaining list
    recursive_selection_sort(arr, start + 1)

# Example usage:
arr = [64, 25, 12, 22, 11]
recursive_selection_sort(arr)
print("Sorted array:", arr)
