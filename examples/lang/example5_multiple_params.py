def max(a: int, b: int) -> int:
    result = a
    if b > a:
        result = b
    return result

x = 15
y = 23
larger = max(x, y)
