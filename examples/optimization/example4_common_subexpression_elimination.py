# 4. Common subexpression elimination - reuse one computation instead of repeating it.
# Linear IR: one shared sum (p + q), reused twice. total == 2 * (p + q) * r -> 40.

p = 2
q = 3
r = 4
s = p + q
u = s * r
v = s * r
total = u + v
