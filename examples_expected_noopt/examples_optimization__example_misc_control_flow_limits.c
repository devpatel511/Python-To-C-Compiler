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

// break point 1
int inc(int v) {
    int _t5 = v + 1;
    int w = _t5;
    return w;
}

int main(void) {
    int _t2;
    int y;
    int _t3;
    // should not perform any major optimizations on control flow as per design decision
    int x = 1;
    bool _t1 = x < 2;
    if (_t1) {
        _t2 = x + 3;
        y = _t2;
    } else {
        _t3 = x + 4;
        y = _t3;
    }
    int _t4 = y + 1;
    int z = _t4;
    // break point 2
    IntList* _t6 = list_new(3);
    _t6->data[0] = 1;
    _t6->data[1] = 2;
    _t6->data[2] = 3;
    IntList* nums = _t6;
    int _t7 = nums->data[0];
    int first = _t7;
    int _t8 = inc(first);
    int a = _t8;
    int b = a;
    int _t9 = b * 2;
    int c = _t9;
    int_list_free(_t6);
    return 0;
}
