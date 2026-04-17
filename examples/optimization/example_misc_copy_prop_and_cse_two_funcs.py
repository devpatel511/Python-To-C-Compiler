# better example to see copy propagation
def process(b: int, c: int) -> int:
    a = b
    t1 = a + c
    x = a * 2
    return t1 + x

# better example to see common subexpression elimination
def compute(a: int, b: int, c: int, d: int) -> int:
    t1 = a + b
    x = t1 * c
    t2 = a + b
    y = t2 * d
    return x + y

p = process(3, 4)
q = compute(1, 2, 3, 4)
