#include <stdbool.h>

int fact(int n) {
    bool _t1 = n == 0;
    if (_t1) {
        return 1;
    }
    int _t2 = n - 1;
    int _t3 = fact(_t2);
    int _t4 = n * _t3;
    return _t4;
}

int main(void) {
    int _t5 = fact(5);
    int x = _t5;
    return 0;
}
