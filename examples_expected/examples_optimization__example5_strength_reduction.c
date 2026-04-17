// 5. Strength reduction - replace expensive ops with cheaper ones (e.g. mul by power of two, x + 0, x * 1).
int compute(int n) {
    int _t1 = n << 1;
    int a = _t1;
    int _t2 = n << 2;
    int b = _t2;
    int _t3 = n << 3;
    int c = _t3;
    int d = n;
    int _t5 = _t1 + _t2;
    int _t6 = _t5 + _t3;
    int _t7 = _t6 + n;
    return _t7;
}

int main(void) {
    int _t8 = compute(3);
    int out = _t8;
    return 0;
}
