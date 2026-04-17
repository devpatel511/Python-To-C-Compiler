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
    int _t1 = 0 - 5;
    int v = _t1;
    int _t2 = v + 10;
    int w = _t2;
    IntList* _t3 = list_new(3);
    _t3->data[0] = 10;
    _t3->data[1] = 20;
    _t3->data[2] = 30;
    IntList* nums = _t3;
    int _t4 = nums->data[0];
    int first = _t4;
    int _t5 = nums->data[1];
    int second = _t5;
    int _t6 = second - first;
    int spread = _t6;
    int_list_free(_t3);
    return 0;
}
