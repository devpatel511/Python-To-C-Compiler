int main(void) {
    // 4. Common subexpression elimination - reuse one computation instead of repeating it.
    // Linear IR: one shared sum (p + q), reused twice. total == 2 * (p + q) * r -> 40.
    int p = 2;
    int q = 3;
    int r = 4;
    int _t1 = p + q;
    int s = _t1;
    int _t2 = s * r;
    int u = _t2;
    int _t3 = s * r;
    int v = _t3;
    int _t4 = u + v;
    int total = _t4;
    return 0;
}
