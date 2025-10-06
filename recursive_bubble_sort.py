def bubble_sort(arr, n=None):
    if n is None:
        n = len(arr)
    if n == 1:
        return arr
    for i in range(n - 1):
        if arr[i] > arr[i + 1]:
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
    return bubble_sort(arr, n - 1)

# Example usage:
nums = [64, 34, 25, 12, 22, 11, 90]
print("Before sorting:", nums)
bubble_sort(nums)
print("After sorting:", nums)
