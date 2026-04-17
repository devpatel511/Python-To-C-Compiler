int main(void) {
    // 3. Dead code elimination — remove unused definitions / redundant IR (e.g. unused temps).
    int x = 5;
    int _t1 = x * 2;
    int y = _t1;
    int _t2 = y + 100;
    int scratch = _t2;
    int result = y;
    return 0;
}
