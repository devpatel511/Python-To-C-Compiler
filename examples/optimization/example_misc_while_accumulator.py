# Misc: while loop — optimizers reset facts at labels; fewer cross-iteration constant folds.
# Sum of 0..4.

i = 0
s = 0
while i < 5:
    s = s + i
    i = i + 1
