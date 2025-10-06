def insertion_sort(arr, n):
    # Base case: if array has 1 or fewer elements, it's already sorted
    if n <= 1:
        return

    # Recursively sort the first n-1 elements
    insertion_sort(arr, n - 1)

    # Insert the nth element into the sorted part
    anchor = arr[n - 1]
    j = n - 2

    # Move elements greater than last one position ahead
    while j >= 0 and arr[j] > anchor:
        arr[j + 1] = arr[j]
        j -= 1

    arr[j + 1] = anchor

# Example usage:
# array = [9, 1, 7, 3, 5]
array = [9, 1, 7]
print("Original array:", array)
insertion_sort(array, len(array))
print("Sorted array:", array)
