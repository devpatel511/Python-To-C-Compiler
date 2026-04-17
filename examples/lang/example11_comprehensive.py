# Comprehensive function with while loop and list operations
def sum_list(nums: list[int]) -> int:
    total = 0
    i = 0
    while i < len(nums):
        total = total + nums[i]
        i = i + 1
    return total

# TESTING COMMENT #2
def max_val(a: int, b: int) -> int:
    result = a
    if b > a:
        result = b
    return result

data = [10, 20, 30]

# TESTING COMMENT #3
s = sum_list(data)
m = max_val(s, 100)
