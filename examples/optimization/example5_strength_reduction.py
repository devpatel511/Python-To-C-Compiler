# 5. Strength reduction - replace expensive ops with cheaper ones (e.g. mul by power of two, x + 0, x * 1).

def compute(n: int) -> int:
    a = n * 2
    b = n * 4
    c = n * 8
    d = n - 0
    return a + b + c + d

out = compute(3)
