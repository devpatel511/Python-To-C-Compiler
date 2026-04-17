#include <stdbool.h>

// better example to see strength reduction
int compute(int n) {
    int _t14 = n * 2;
    int a = _t14;
    int _t15 = n * 4;
    int b = _t15;
    int _t16 = n * 8;
    int c = _t16;
    int _t17 = n - 0;
    int d = _t17;
    int _t18 = a + b;
    int _t19 = _t18 + c;
    int _t20 = _t19 + d;
    return _t20;
}

int main(void) {
    // better example to see constant folding
    int _t1 = 2 + 3;
    int a = _t1;
    int _t2 = 10 * 4;
    int b = _t2;
    int _t3 = 100 / 5;
    int c = _t3;
    int _t4 = 7 - 2;
    int d = _t4;
    // True
    bool _t5 = true && false;
    bool _t6 = !(_t5);
    int _t7 = - 5;
    bool _t8 = _t7 > 3;
    bool _t9 = _t6 || _t8;
    bool e = _t9;
    // 3
    int _t10 = 2 + 3;
    int _t11 = 10 - 4;
    int _t12 = _t10 * _t11;
    int _t13 = _t12 / 2;
    int f = _t13;
    int _t21 = compute(3);
    int out = _t21;
    return 0;
}
