int main(void) {
    // 2. Constant propagation — replace uses of variables with known constant values.
    int x = 5;
    int y = x;
    int _t1 = y + 3;
    int z = _t1;
    int result = z;
    return 0;
}
