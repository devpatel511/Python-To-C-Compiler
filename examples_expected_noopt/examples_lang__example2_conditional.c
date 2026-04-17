#include <stdbool.h>

int main(void) {
    int age = 25;
    bool is_adult = false;
    bool _t1 = age >= 18;
    if (_t1) {
        is_adult = true;
    }
    return 0;
}
