int main(void) {
    // 1. Constant propagation: x = 5, y = x -> y = 5
    // 2. Constant folding: 5 * 2 = 10, 10 + 0 = 10
    // 3. Strength reduction: + 0 -> identity
    // 4. Copy propagation: tmp = z, result_1 = tmp -> result_1 = z
    int x = 5;
    int y = 5;
    int z = 10;
    int tmp = 10;
    int result_1 = 10;
    // 5. Common subexpression elimination: a + b
    // 6. Dead code elimination: all temporary variables in IR removed
    int a = 10;
    int b = 20;
    int c = 30;
    int d = 30;
    int e = 60;
    int result_2 = 60;
    // It is expected that both results are optimized to a constant
    return 0;
}
