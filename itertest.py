import random

from functools import reduce

# word = ["h","e","l","l","o"]
# reduce
#test = lambda x,y: x+y
#print(reduce(test, word))
#rint(reduce(lambda x,y: x+y, word))

# map
# test = lambda x: x.upper()
# print(list(map(test, word))) #map for iterable all list

# filter

# score =[100,90,80,70,60,50,40,30]
#
# print(list(filter(lambda x : x >= 60, score)))

# fruits = {"Apple", "Peach", "Mango"}
# printx = lambda x: x
# print(list(map(printx, fruits)))

# for loop to access each fruits
# for fruit in fruits:
#     print(fruit)

#%%
# nasted dictionaty
# data = {"M":{180:70},"F":{160:50}}
#
# for x, obj in data.items():
#   print(x)
#   for y in obj:
#     print(str(y)+':'+str(obj[y]))
# %%

# val=1
# data=[0]*5
# for i in range(5):
#     data[i]=val
#     val=val+random.randint(1,5)
#     print(f"i :{i}, val: {val}, data:{data[i]}")
# print('資料內容：')
# for i in range(5):
#     for j in range(10):
#         print('%3d-%-3d' %(i*10+j+1,data[i*10+j]), end='')
#     print()

def b_s(arr, data):
    low =0
    hight =arr.__len__()
    while low <= hight and data != -1:
        mid = (low+hight) // 2
        if arr[mid] > data:
            hight = mid - 1
        elif arr[mid] < data:
            low = mid + 1
        else:
            return mid
    return -1

arr=[11,12,13,14,15]
index=b_s(arr,15)
print(f"index :{index}")