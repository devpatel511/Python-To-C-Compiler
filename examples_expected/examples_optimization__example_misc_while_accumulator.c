#include <stdbool.h>

int main(void) {
    bool _t1;
    int _t2;
    int _t3;
    // Misc: while loop — optimizers reset facts at labels; fewer cross-iteration constant folds.
    // Sum of 0..4.
    int i = 0;
    int s = 0;
    while (1) {
        _t1 = i < 5;
        if (!(_t1)) {
            break;
        }
        _t2 = s + i;
        s = _t2;
        _t3 = i + 1;
        i = _t3;
    }
    return 0;
}
