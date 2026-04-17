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
    int x = 5;
    int y = 12;
    int _t4 = 17;
    int z = _t4;
    int a = 3;
    int b = 16;
    IntList* _t7 = list_new(2);
    _t7->data[0] = 11;
    _t7->data[1] = 6;
    IntList* c = _t7;
    int_list_free(_t7);
    return 0;
}
