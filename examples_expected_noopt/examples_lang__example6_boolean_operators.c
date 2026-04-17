#include <stdbool.h>

int main(void) {
    int x = 5;
    int y = 10;
    int z = 15;
    bool result1 = false;
    bool result2 = false;
    bool _t1 = x < y;
    bool _t2 = y < z;
    bool _t3 = _t1 && _t2;
    if (_t3) {
        result1 = true;
    }
    bool _t4 = x > y;
    bool _t5 = x > z;
    bool _t6 = _t4 || _t5;
    if (_t6) {
        result2 = true;
    }
    return 0;
}
