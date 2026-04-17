// better example to see copy propagation
int process(int b, int c) {
    int a = b;
    int _t1 = a + c;
    int t1 = _t1;
    int _t2 = a * 2;
    int x = _t2;
    int _t3 = t1 + x;
    return _t3;
}

// better example to see common subexpression elimination
int compute(int a, int b, int c, int d) {
    int _t4 = a + b;
    int t1 = _t4;
    int _t5 = t1 * c;
    int x = _t5;
    int _t6 = a + b;
    int t2 = _t6;
    int _t7 = t2 * d;
    int y = _t7;
    int _t8 = x + y;
    return _t8;
}

int main(void) {
    int _t9 = process(3, 4);
    int p = _t9;
    int _t10 = compute(1, 2, 3, 4);
    int q = _t10;
    return 0;
}
