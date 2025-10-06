# def bubbleSort(arr):
#     size = len(arr)
#     for i in range(size):
#         for j in range(0, size-i-1):
#             if arr[j] > arr[j+1]:
#                 arr[j],arr[j+1] = arr[j+1],arr[j]


def selection_sort(arr):
    size = len(arr)
    for i in range(size-1):
        min_index =i
        for j in range(i+1, size):
            if arr[j] < arr[min_index]:
                min_index =j
        if min_index != i:
            arr[i], arr[min_index] = arr[min_index], arr[i]

# def insertion_sort(arr):
#     size = len(arr)
#     for i in range(1,size):
#         anchor =arr[i]
#         j = i-1
#         while j >= 0 and arr[j] > anchor:
#             arr[j+1] = arr[j]
#             j = j-1
#         arr[j+1] = anchor

# def shell_sort(arr):
#     size = len(arr)
#     gap = size // 2  # Initialize the gap size.
#
#     # Start with a big gap, then reduce the gap.
#     while gap > 0:
#         # Do a gapped insertion sort for this gap size.
#         for i in range(gap, size):
#             anchor = arr[i]
#             j = i
#             # Shift earlier gap-sorted elements up until the correct location for arr[i] is found.
#             while j >= gap and arr[j - gap] > anchor:
#                 arr[j] = arr[j - gap]
#                 j -= gap
#             arr[j] = anchor
#         gap //= 2  # Reduce the gap for the next element.

test_cases = [
        [10, 3, 15, 7, 8, 23, 98, 29],
        [],
        [3],
        [9,8,7,2],
        [1,2,3,4,5]
    ]

for arr in test_cases:
    # bubbleSort(arr)
    # insertion_sort(arr)
    selection_sort(arr)
    # shell_sort(arr)
    print(arr)
