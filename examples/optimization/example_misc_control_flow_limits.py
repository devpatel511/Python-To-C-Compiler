# should not perform any major optimizations on control flow as per design decision
x = 1
if x < 2:
    y = x + 3
else:
    y = x + 4
z = y + 1

# break point 1
def inc(v: int) -> int:
    w = v + 1
    return w

# break point 2
nums = [1, 2, 3]
first = nums[0]
a = inc(first)
b = a
c = b * 2
