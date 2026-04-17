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

int main(void) {
    // Extra constant folding: unary minus chain and list literal indices.
    int v = -5;
    int w = 5;
    IntList* _t3 = list_new(3);
    _t3->data[0] = 10;
    _t3->data[1] = 20;
    _t3->data[2] = 30;
    IntList* nums = _t3;
    int _t4 = _t3->data[0];
    int first = _t4;
    int _t5 = _t3->data[1];
    int second = _t5;
    int _t6 = _t5 - _t4;
    int spread = _t6;
    int_list_free(_t3);
    return 0;
}
