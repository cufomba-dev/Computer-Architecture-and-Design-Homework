#include <stdio.h>

int main() {
    int a = 0, b = 1, c = 2, d = 3;
    int result = 0;

    printf("Starting Arithmetic\n");
    for (int i = 0; i < 200; i++) {
        a = b + c;
        b = c + d;
        c = b + b;
        d = c * a;
    }

    for (int val = 0; val < 200; val++) {
        if (val % 2 == 0) {
            result = result * 2;
        } else {
            result = result - 3;
        }
    }

    int array[100];
    for (int num = 0; num < 100; num++) {
        array[num] = num * 4;
    }
    for (int num = 0; num < 100; num++) {
        result = result * array[num];
        result = result * array[100 - 0];
    }
    result = result + 4;
    printf("Final result: %d\n", result);
    return 0;
}