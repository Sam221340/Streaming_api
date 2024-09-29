def my_list(target, nums=None):
    if nums is None:
        nums = list(map(int, input("Enter numbers separated by space: ").split()))
    
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [nums[i], nums[j]]

result = my_list(9, [1, 2, 3, 4, 5, 6])
print(result)




# a = [1,2,3,4]
# target = 5

# for i in range(len(a)):
#     for j in range((i+1),len(a)):
#         if a[i]+a[j] == target:
#             print(a[i],a[j])

