#include <stdio.h>  // For fopen, getline, printf, fclose
#include <stdlib.h> // For malloc, free, atoi, atol
#include <string.h> // For strstr, sscanf, strcmp

// Structure to store information about an I/O operation (not directly used but good practice)
typedef struct {
    char type[10];          // "read" or "write"
    long fd;                // File descriptor
    char path[256];         // File path
    long offset;            // Operation offset
    long size_requested;    // Requested size
    long bytes_transferred; // Actual bytes transferred
} IoOperation;

int main(int argc, char *argv[]) {
    // Expect exactly one argument: the trace file name
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <trace_file.log>\n", argv[0]);
        return EXIT_FAILURE;
    }

    // Open the trace file in read mode
    FILE *file = fopen(argv[1], "r");
    if (file == NULL) {
        perror("Cannot open the trace file");
        return EXIT_FAILURE;
    }

    char *line = NULL;   // Buffer for getline
    size_t len = 0;      // Size of the buffer
    ssize_t read_len;    // Length of the line read

    // Array to store the current offset per file descriptor (FD).
    // Index = FD number, Value = current offset.
    // Size is 4096 by default (sufficient for most workloads).
    long current_offsets[4096] = {0};

    // Boolean array (0/1) to check if a FD offset has been initialized (via open/lseek).
    int fd_initialized[4096] = {0};

    // Print the header (output format explanation)
    printf("Nature_operation Offset Taille_requete\n");
    printf("--------------------------------------\n");

    // Read the trace file line by line
    while ((read_len = getline(&line, &len, file)) != -1) {
        char op_type[10];             // Stores "read" or "write"
        long fd_num;                  // File descriptor number
        char path_buffer[256] = "";   // File path extracted from trace

        // Variables for lseek parsing
        long lseek_offset_arg, lseek_result;
        char whence_str[10];

        // Try to parse an lseek operation.
        // Example trace line: lseek(16<...>, 101429760, SEEK_SET) = 101429760
        if (sscanf(line, "[pid %*d] lseek(%ld<%255[^>]>, %ld, %9[^)]) = %ld", 
                   &fd_num, path_buffer, &lseek_offset_arg, whence_str, &lseek_result) == 5) {
            
            // Update the offset if FD is valid
            if (fd_num >= 0 && fd_num < 4096) {
                current_offsets[fd_num] = lseek_result; // Set the new offset
                fd_initialized[fd_num] = 1;             // Mark FD as initialized
            }
            continue; // Skip to next line
        }
        
        // Variables for read/write parsing
        long size_req, bytes_trans;
        
        // Try to parse a read/write operation.
        // Example trace line: read(16<...>, "...", 512) = 512
        if (sscanf(line, "[pid %*d] %9[a-z](%ld<%255[^>]>, %*[^,], %ld) = %ld", 
                   op_type, &fd_num, path_buffer, &size_req, &bytes_trans) == 5) {

            // Only process valid file descriptors and valid operations (read/write)
            if (fd_num >= 0 && fd_num < 4096 && 
                (strcmp(op_type, "read") == 0 || strcmp(op_type, "write") == 0)) {
                
                // If this FD is used for the first time and no lseek was seen,
                // initialize offset to 0.
                if (!fd_initialized[fd_num]) {
                    current_offsets[fd_num] = 0; 
                    fd_initialized[fd_num] = 1;
                }

                // Filter: we only output operations where
                // 1. The requested size == 512
                // 2. The current offset is aligned to 512
                if (size_req == 512 && (current_offsets[fd_num] % 512 == 0)) {
                    // Binary type for operation: 0 = read, 1 = write
                    int binary_op_type = (strcmp(op_type, "write") == 0) ? 1 : 0;
                    
                    // Print operation: type offset size
                    // We cast size_req to int because the replay program expects int
                    printf("%d %ld %d\n", 
                           binary_op_type, 
                           current_offsets[fd_num], 
                           (int)size_req);
                }

                // Always update the current offset:
                // It increases by the number of bytes actually transferred.
                if (bytes_trans > 0) {
                    current_offsets[fd_num] += bytes_trans;
                }
            }
        }
    }

    // Cleanup: free memory allocated by getline
    free(line);

    // Close the trace file
    fclose(file);

    return EXIT_SUCCESS;
}

