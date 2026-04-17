#include <stdbool.h>

int main(void) {
    int number = 7;
    bool is_even = false;
    bool is_odd = false;
    int _t1 = number % 2;
    bool _t2 = _t1 == 0;
    if (_t2) {
        is_even = true;
    } else {
        is_odd = true;
    }
    return 0;
}
