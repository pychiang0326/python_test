# bubble sort
# for i in range(7,-1,-1):
#     print(i)
#     for j in range(i):
#         print(" "*j+str(j)+str(j+1))
#     print("\n")

# selection sort
# data = [4,2,3,32,16,65]
# size = len(data)
# #print(size)
# for i in range(size-1):
#     for j in range (i+1,size):
#         if data[i]>data[j]:
#             data[i],data[j]=data[j],data[i]
#
# for i in range(size):
#     print("%2d" %data[i],end = " ")

#insertion sort

# data = [3,2,1]
# size = len(data)
# for i in range(1,size):
#     temp = data[i]
#     no = i-1
#     while(no >=0 and temp<data[no]):
#         data[no+1]=data[no]
#         no-=1
#     data[no+1]=temp
#     print("i = "+str(i),end=" ")
#     print(data)
#
# print(data)

# jmp =1//2
# print(jmp)
# data = [3,2,1]
# print(len(data))
# for i in range(1,3):
#     print(i, end =" ")

arr=[[0]*6 for row in range(6)]
print(arr)

for i in range(10):
    print(i)
    for j in range(2):
        print(j)
        for k in range(6):
            print(k, end=" ")
        print("\n")
