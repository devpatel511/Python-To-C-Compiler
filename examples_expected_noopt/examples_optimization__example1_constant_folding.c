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
    // Constant folding: scalars and list literal element expressions.
    int _t1 = 2 + 3;
    int x = _t1;
    int _t2 = 10 - 4;
    int _t3 = _t2 * 2;
    int y = _t3;
    int _t4 = x + y;
    int z = _t4;
    int _t5 = 6 / 2;
    int a = _t5;
    int _t6 = 4 + 12;
    int b = _t6;
    IntList* _t7 = list_new(2);
    int _t8 = b - 5;
    _t7->data[0] = _t8;
    int _t9 = a + 3;
    _t7->data[1] = _t9;
    IntList* c = _t7;
    int_list_free(_t7);
    return 0;
}
