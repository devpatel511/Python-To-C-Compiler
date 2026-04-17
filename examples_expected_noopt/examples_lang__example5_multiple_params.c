#include <stdbool.h>

int max(int a, int b) {
    int result = a;
    bool _t1 = b > a;
    if (_t1) {
        result = b;
    }
    return result;
}

int main(void) {
    int x = 15;
    int y = 23;
    int _t2 = max(x, y);
    int larger = _t2;
    return 0;
}
