# Extra constant folding: unary minus chain and list literal indices.

v = 0 - 5
w = v + 10

nums = [10, 20, 30]
first = nums[0]
second = nums[1]
spread = second - first
