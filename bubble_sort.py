def bubble_sort(arr):
    n = len(arr)  # Get the number of elements in the array
    for i in range(n):  # Loop through each element
        swapped = False
        for j in range(0, n - i - 1):  # Loop to compare adjacent elements
            if arr[j] > arr[j + 1]:  # If the current element is greater than the next
                arr[j], arr[j + 1] = arr[j + 1], arr[j]  # Swap them
                swapped = True
                # print(f"{i} {j} ,{arr}")
        if not swapped:
            # print(f"i= {i} {arr}")
            break
    return arr

# Example usage
data = [64, 34, 25, 12, 22, 11, 90]
sorted_data = bubble_sort(data)
print("Sorted array is:", sorted_data)