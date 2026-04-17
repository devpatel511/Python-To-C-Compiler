// 6. Copy propagation - use the original value directly instead of routing through a copy temp.
int process(int b, int c) {
    int a = b;
    int _t1 = b + c;
    int t1 = _t1;
    int _t2 = b << 1;
    int x = _t2;
    int _t3 = _t1 + _t2;
    return _t3;
}

int main(void) {
    int _t4 = process(3, 4);
    int p = _t4;
    // Module-level copy chain: tmp holds z, then result reads tmp.
    int z = 42;
    int tmp = 42;
    int result = 42;
    return 0;
}
