#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MB (1024 * 1024)

long parse_page_size(const char *page_size_str) {
    /* Convert page size string (e.g., "4KiB") to bytes */
    char *endptr;
    long value = strtol(page_size_str, &endptr, 10);
    if (strcmp(endptr, "KiB") == 0) {
        return value * 1024;
    } else if (strcmp(endptr, "MiB") == 0) {
        return value * 1024 * 1024;
    } else if (strcmp(endptr, "GiB") == 0) {
        return value * 1024 * 1024 * 1024;
    } else {
        fprintf(stderr, "Invalid page size format: %s. Use '4KiB', '2MiB', etc.\n", page_size_str);
        exit(1);
    }
}

int main(int argc, char *argv[]) {
    long PAGE_SIZE = 4096;  // Default to 4 KiB
    if (argc > 1 && strncmp(argv[1], "--page-size=", 12) == 0) {
        PAGE_SIZE = parse_page_size(argv[1] + 12);  // Skip "--page-size="
    }

    printf("Page Size: %ld bytes\n\n", PAGE_SIZE);

    // Allocate 8MB of memory (2048 pages)
    int memory_size = 8 * MB;
    char *memory = malloc(memory_size);
    
    if (!memory) {
        printf("Failed to allocate memory\n");
        return 1;
    }
    
    printf("Allocated %d MB of memory\n", memory_size / MB);
    
    // Test 
    printf("\nTest 1\n");

    int pages_to_access = memory_size / PAGE_SIZE;
    
    for (int round = 0; round < 5; round++) {        
        for (int i = 0; i < pages_to_access; i++) {
            // Access a different page each time
            int page_num = (i * 300) % pages_to_access;  
            int offset = page_num * PAGE_SIZE;
            memory[offset] = round;
        }        
    }
    
    // Test 2
    printf("\nTest 2\n");
    int stride = PAGE_SIZE * 4;  
    int accesses = 0;
    for (int i = 0; i < memory_size; i += stride) {
        memory[i] = 2;
        accesses++;
    }
    
    // Test 3
    printf("\nTest 3\n");
    int num_pages = 1000; 
    for (int repeat = 0; repeat < 3; repeat++) {
        for (int page = 0; page < num_pages; page++) {
            if (page * PAGE_SIZE >= memory_size) break;
            int offset = page * PAGE_SIZE;
            memory[offset] = page % 256;
        }
    }

    // Test 4
    printf("\nTest 4\n");
    int total_val = 0;
    int second_total_val = 0;
    for (int i = 0; i < memory_size; i += PAGE_SIZE) {
        total_val += memory[i];
        second_total_val -= memory[i];
    }
    
    printf("\nAll tests completed!\n");
    free(memory);
    return 0;
}