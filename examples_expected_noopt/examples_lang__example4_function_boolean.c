#include <stdbool.h>

bool is_positive(int n) {
    bool result = false;
    bool _t1 = n > 0;
    if (_t1) {
        result = true;
    }
    return result;
}

int main(void) {
    int value = 42;
    int _t2 = is_positive(value);
    int check = _t2;
    return 0;
}
