#include <stdbool.h>

int main(void) {
    // example comment for booleans behavior
    bool flag = true;
    bool result = false;
    bool _t1 = !(flag);
    if (_t1) {
        result = true;
    }
    bool a = true;
    bool b = false;
    bool _t2 = !(a);
    bool _t3 = !(b);
    bool _t4 = b && _t3;
    bool _t5 = _t2 || _t4;
    bool c = _t5;
    return 0;
}
