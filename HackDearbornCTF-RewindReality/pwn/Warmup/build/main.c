#include <stdio.h>
#include <stdlib.h>

void get_flag() {
    FILE *file = fopen("flag.txt", "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }
    char flag[256];
    if (fgets(flag, sizeof(flag), file) != NULL) {
        printf("%s\n", flag);
    } else {
        printf("Error reading flag\n");
    }
    fclose(file);
}

void vuln() {
    int magic = 0;
    char buffer[1024];
    printf("Enter data: ");
    gets(buffer);
    if (magic == 0x41414141) {
        get_flag();
    } else {
        printf("No flag for you!\n");
    }
}

int main() {
    setvbuf(stdout, NULL, _IONBF, 0); // Disable output buffering
    vuln();
    return 0;
}
