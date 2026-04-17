# better example to see constant folding
a = 2 + 3
b = 10 * 4
c = 100 / 5
d = 7 - 2
# True
e = not (True and False) or (-5 > 3)
# 3
f = (2 + 3) * (10 - 4) / 2

# better example to see strength reduction
def compute(n: int) -> int:
    a = n * 2
    b = n * 4
    c = n * 8
    d = n - 0
    return a + b + c + d

out = compute(3)
