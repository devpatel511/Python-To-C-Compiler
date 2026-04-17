int main(void) {
    // 1. Constant propagation: x = 5, y = x -> y = 5
    // 2. Constant folding: 5 * 2 = 10, 10 + 0 = 10
    // 3. Strength reduction: + 0 -> identity
    // 4. Copy propagation: tmp = z, result_1 = tmp -> result_1 = z
    int x = 5;
    int y = x;
    int _t1 = y * 2;
    int _t2 = _t1 + 0;
    int z = _t2;
    int tmp = z;
    int result_1 = tmp;
    // 5. Common subexpression elimination: a + b
    // 6. Dead code elimination: all temporary variables in IR removed
    int a = 10;
    int b = 20;
    int _t3 = a + b;
    int c = _t3;
    int _t4 = a + b;
    int d = _t4;
    int _t5 = c + d;
    int e = _t5;
    int result_2 = e;
    // It is expected that both results are optimized to a constant
    return 0;
}
