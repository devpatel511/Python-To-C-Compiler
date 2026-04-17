#include <stdbool.h>

int main(void) {
    bool _t2;
    int y;
    int _t3;
    int z;
    // example comment for nested blocks behavior
    int x = 10;
    bool _t1 = x > 5;
    if (_t1) {
        _t2 = x > 8;
        if (_t2) {
            y = 1;
        } else {
            y = 2;
        }
        _t3 = y + 1;
        z = _t3;
    }
    return 0;
}
