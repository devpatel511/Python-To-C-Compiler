#include <stdbool.h>

// better example to see strength reduction
int compute(int n) {
    int _t14 = n << 1;
    int a = _t14;
    int _t15 = n << 2;
    int b = _t15;
    int _t16 = n << 3;
    int c = _t16;
    int d = n;
    int _t18 = _t14 + _t15;
    int _t19 = _t18 + _t16;
    int _t20 = _t19 + n;
    return _t20;
}

int main(void) {
    // better example to see constant folding
    int a = 5;
    int b = 40;
    int c = 20;
    int d = 5;
    // True
    bool _t9 = true;
    bool e = _t9;
    // 3
    int _t13 = 15;
    int f = _t13;
    int _t21 = compute(3);
    int out = _t21;
    return 0;
}
