# 6. Copy propagation - use the original value directly instead of routing through a copy temp.

def process(b: int, c: int) -> int:
    a = b
    t1 = a + c
    x = a * 2
    return t1 + x

p = process(3, 4)

# Module-level copy chain: tmp holds z, then result reads tmp.
z = 42
tmp = z
result = tmp
