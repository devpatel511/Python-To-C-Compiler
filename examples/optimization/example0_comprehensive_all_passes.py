# 1. Constant propagation: x = 5, y = x -> y = 5
# 2. Constant folding: 5 * 2 = 10, 10 + 0 = 10
# 3. Strength reduction: + 0 -> identity
# 4. Copy propagation: tmp = z, result_1 = tmp -> result_1 = z

x = 5
y = x
z = y * 2 + 0
tmp = z
result_1 = tmp

# 5. Common subexpression elimination: a + b
# 6. Dead code elimination: all temporary variables in IR removed
a = 10
b = 20
c = a + b
d = a + b
e = c + d
result_2 = e

# It is expected that both results are optimized to a constant
