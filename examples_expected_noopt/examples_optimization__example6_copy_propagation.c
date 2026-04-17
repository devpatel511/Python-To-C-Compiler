// 6. Copy propagation - use the original value directly instead of routing through a copy temp.
int process(int b, int c) {
    int a = b;
    int _t1 = a + c;
    int t1 = _t1;
    int _t2 = a * 2;
    int x = _t2;
    int _t3 = t1 + x;
    return _t3;
}

int main(void) {
    int _t4 = process(3, 4);
    int p = _t4;
    // Module-level copy chain: tmp holds z, then result reads tmp.
    int z = 42;
    int tmp = z;
    int result = tmp;
    return 0;
}
