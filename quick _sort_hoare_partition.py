def hoare_partition(arr, low, high):
    pivot = arr[low]  # Choose the first element as pivot
    i = low - 1
    j = high + 1

    while True:
        # Move i to the right until arr[i] >= pivot
        i += 1
        while arr[i] < pivot:
            i += 1

        # Move j to the left until arr[j] <= pivot
        j -= 1
        while arr[j] > pivot:
            j -= 1

        # If pointers crossed, return partition index
        if i >= j:
            return j

        # Swap elements at i and j
        arr[i], arr[j] = arr[j], arr[i]

def quick_sort(arr, low, high):
    if low < high:
        p = hoare_partition(arr, low, high)
        quick_sort(arr, low, p)
        quick_sort(arr, p + 1, high)

# Example usage
arr = [29, 10, 14, 37, 13]
quick_sort(arr, 0, len(arr) - 1)
print("Sorted array:", arr)
