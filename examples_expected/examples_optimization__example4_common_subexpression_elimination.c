int main(void) {
    // 4. Common subexpression elimination - reuse one computation instead of repeating it.
    // Linear IR: one shared sum (p + q), reused twice. total == 2 * (p + q) * r -> 40.
    int p = 2;
    int q = 3;
    int r = 4;
    int s = 5;
    int u = 20;
    int v = 20;
    int _t4 = 40;
    int total = _t4;
    return 0;
}
