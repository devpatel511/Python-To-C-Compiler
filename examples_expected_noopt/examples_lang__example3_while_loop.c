#include <stdbool.h>

int main(void) {
    bool _t1;
    int _t2;
    int _t3;
    int counter = 0;
    int total = 0;
    while (1) {
        _t1 = counter < 5;
        if (!(_t1)) {
            break;
        }
        _t2 = total + counter;
        total = _t2;
        _t3 = counter + 1;
        counter = _t3;
    }
    return 0;
}
