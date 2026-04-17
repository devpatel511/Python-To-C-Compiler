#include <stdbool.h>

int main(void) {
    // Unary operation and negation
    int x = 5;
    int _t1 = - x;
    int y = _t1;
    bool flag = true;
    bool _t2 = !(flag);
    bool check = _t2;
    int _t3 = - 3;
    int _t4 = _t3 + y;
    int result = _t4;
    return 0;
}
