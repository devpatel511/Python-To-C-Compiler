def sum(x: list[int]) -> int:
    idx = 0
    res = 0
    while idx < len(x):
        res = res + x[idx]
        idx = idx + 1
    return res

l1 = []
l1 = [1, 2, 3, 4]
l2 = l1
list_sum = sum(l2)
is_even = False
if list_sum % 2 == 0:
    is_even = True
