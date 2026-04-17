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

int sum(IntList* x) {
    int _t1;
    bool _t2;
    int _t3;
    int _t4;
    int _t5;
    int idx = 0;
    int res = 0;
    while (1) {
        _t1 = x->length;
        _t2 = idx < _t1;
        if (!(_t2)) {
            break;
        }
        _t3 = x->data[idx];
        _t4 = res + _t3;
        res = _t4;
        _t5 = idx + 1;
        idx = _t5;
    }
    return res;
}

int main(void) {
    IntList* _t6 = list_new(0);
    IntList* l1 = _t6;
    IntList* _t7 = list_new(4);
    _t7->data[0] = 1;
    _t7->data[1] = 2;
    _t7->data[2] = 3;
    _t7->data[3] = 4;
    l1 = _t7;
    IntList* l2 = l1;
    int _t8 = sum(l2);
    int list_sum = _t8;
    bool is_even = false;
    int _t9 = list_sum % 2;
    bool _t10 = _t9 == 0;
    if (_t10) {
        is_even = true;
    }
    int_list_free(_t6);
    int_list_free(_t7);
    return 0;
}
