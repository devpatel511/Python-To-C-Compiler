#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int* data;
    int length;
} IntList;

IntList* list_new(int len) {
    IntList* list = (IntList*)malloc(sizeof(IntList));
    list->length = len;
    if (len > 0) {
        list->data = (int*)malloc((size_t)len * sizeof(int));
    } else {
        list->data = NULL;
    }
    return list;
}

void int_list_free(IntList* list) {
    if (list != NULL) {
        free(list->data);
        free(list);
    }
}

// Comprehensive function with while loop and list operations
int sum_list(IntList* nums) {
    int _t1;
    bool _t2;
    int _t3;
    int _t4;
    int _t5;
    int total = 0;
    int i = 0;
    while (1) {
        _t1 = nums->length;
        _t2 = i < _t1;
        if (!(_t2)) {
            break;
        }
        _t3 = nums->data[i];
        _t4 = total + _t3;
        total = _t4;
        _t5 = i + 1;
        i = _t5;
    }
    return total;
}

// TESTING COMMENT #2
int max_val(int a, int b) {
    int result = a;
    bool _t6 = b > a;
    if (_t6) {
        result = b;
    }
    return result;
}

int main(void) {
    IntList* _t7 = list_new(3);
    _t7->data[0] = 10;
    _t7->data[1] = 20;
    _t7->data[2] = 30;
    IntList* data = _t7;
    // TESTING COMMENT #3
    int _t8 = sum_list(data);
    int s = _t8;
    int _t9 = max_val(s, 100);
    int m = _t9;
    int_list_free(_t7);
    return 0;
}
