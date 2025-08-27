/**
 * iortest1.c
 *
 * Replays an I/O trace, timing the raw read/write operation.
 * The lseek time is not included in the final measurement.
 *
 */

// Include necessary headers
#include "tools.h"      // Contains utility structures and functions like AppConfig, ReplayStats, parse_args, calculate_stats.
#include <time.h>       // For clock_gettime, used for precise time measurements (although gettimeofday is used here).
#include <errno.h>      // For system error handling (perror).
#include <string.h>     // For string and memory manipulation functions (memset, memcpy).
#include <sys/mman.h>   // For the mmap function, used to map the trace file into memory.
#include <sys/stat.h>   // For fstat, which gets file information.
#include <fcntl.h>      // For open and file flags (O_RDONLY, O_WRONLY, O_DIRECT, etc.).
#include <unistd.h>     // For close, lseek64, read, write, sync.
#include <stdio.h>      // For standard input/output functions (fprintf, printf, perror).
#include <stdlib.h>     // For memory allocation functions (malloc, free, realloc) and exit codes.
#include <stdint.h>     // For fixed-size integer types (uint64_t).
#include <math.h>       // For mathematical functions (llabs for absolute value, sqrt for square root, pow for powers).
#include <inttypes.h>   // For printf formatting macros (PRIu64).
#include <sys/time.h>   // For gettimeofday, a high-resolution timing method.

#define SECTOR_SIZE 512
#define TARGET_MEM_BYTES (1024 * 1024) /* 1 MiB target per memory measurement */

// Structure representing a single I/O request
typedef struct {
    short op_type;       /* 0 for a read, 1 for a write */
    long  offset;        /* The offset in bytes from the start of the file */
    short length;        /* The length of the operation in bytes */
} IOReq;

static AppConfig config;


/**
 * @brief Loads an I/O trace from a file and stores it in an array.
 * @param path The path to the trace file.
 * @param reqs A pointer to a pointer of IOReq to store the array of requests.
 * @return The number of requests loaded, or 0 on error.
 */
static size_t load_trace(const char *path, IOReq **reqs) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        perror("open trace");
        return 0;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("fstat");
        close(fd);
        return 0;
    }
    size_t filesize = (size_t)st.st_size;
    if (filesize == 0) {
        close(fd);
        return 0;
    }

    // Map the file into memory for fast reading
    char *data = mmap(NULL, filesize, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    if (data == MAP_FAILED) {
        perror("mmap");
        return 0;
    }

    // Skip the first two header lines of the trace file
    char *ptr = data;
    char *end = data + filesize;
    char *nl = memchr(ptr, '\n', end - ptr);
    if (nl) ptr = nl + 1;
    nl = memchr(ptr, '\n', end - ptr);
    if (nl) ptr = nl + 1;

    // Allocate memory for the requests with an initial capacity
    size_t capacity = ((end - ptr) / 8) + 8;
    IOReq *array = malloc(capacity * sizeof(IOReq));
    if (!array) {
        perror("malloc reqs");
        munmap(data, filesize);
        return 0;
    }

    // Read each line of the trace and parse it into an IOReq structure
    size_t count = 0;
    while (ptr < end) {
        if (count >= capacity) {
            capacity *= 2;
            IOReq *tmp = realloc(array, capacity * sizeof(IOReq));
            if (!tmp) {
                perror("realloc");
                free(array);
                munmap(data, filesize);
                return 0;
            }
            array = tmp;
        }

        short t; long off; short len;
        if (sscanf(ptr, "%hd %ld %hd", &t, &off, &len) == 3) {
            array[count].op_type = t;
            array[count].offset  = off;
            array[count].length  = len;
            count++;
        }
        char *next = memchr(ptr, '\n', end - ptr);
        if (!next) break;
        ptr = next + 1;
    }

    // Unmap the memory
    munmap(data, filesize);

    if (count == 0) {
        free(array);
        *reqs = NULL;
        return 0;
    }
    // Resize the array to the final size
    IOReq *final = realloc(array, count * sizeof(IOReq));
    *reqs = final ? final : array;
    return count;
}


/**
 * @brief Prepares a memory-aligned I/O buffer for O_DIRECT operations.
 * @param reqs The array of I/O requests to determine the maximum length.
 * @param nreq The number of requests.
 * @param out_max_len A pointer to store the maximum buffer size.
 * @return A pointer to the allocated I/O buffer, or NULL on failure.
 */
static char *prepare_io_buffer(IOReq *reqs, size_t nreq, size_t *out_max_len) {
    *out_max_len = 0;
    for (size_t i = 0; i < nreq; ++i)
        if ((size_t)reqs[i].length > *out_max_len)
            *out_max_len = reqs[i].length;
    if (*out_max_len == 0) *out_max_len = SECTOR_SIZE;

    char *buf = NULL;
    // Allocate memory aligned to the sector size
    if (posix_memalign((void**)&buf, SECTOR_SIZE, *out_max_len) != 0) {
        perror("posix_memalign");
        return NULL;
    }
    // Fill the buffer with some data
    memset(buf, 'B', *out_max_len);
    return buf;
}


/**
 * @brief Forces the purging of kernel page caches.
 * Requires root privileges to work correctly.
 */
static void drop_cache(void) {
    sync(); // Ensures all pending data is written to disk
    int fd = open("/proc/sys/vm/drop_caches", O_WRONLY);
    if (fd >= 0) {
        if (write(fd, "3", 1) < 0) perror("write drop_caches");
        close(fd);
    }
}


/**
 * @brief Replays the I/O requests and times each raw operation.
 * @param reqs The array of requests to replay.
 * @param nreq The number of requests.
 * @param buffer The I/O buffer.
 * @param io_wait_times_us An array to store the latency times in microseconds.
 * @param seek_distances An array to store the seek distances in bytes.
 * @return The number of successfully executed requests.
 */
static size_t replay_requests_detailed(IOReq *reqs, size_t nreq, char *buffer,
                                       size_t *io_wait_times_us,
                                       long *seek_distances) {
    // Use O_RDWR, O_SYNC, and O_DIRECT flags for non-cached I/O
    int flags = O_RDWR | O_SYNC | O_DIRECT;
    int fd = open64(config.data_file_path, flags);
    if (fd < 0) {
        perror("open64 data file");
        return 0;
    }

    // Initial drop_cache to clear the cache before starting the replay
    drop_cache();

    struct timeval t_start_op, t_end_op;
    long last_offset = -1;
    size_t executed = 0;

    int fdcleancache = open("/proc/sys/vm/drop_caches", O_WRONLY);
    if (fdcleancache < 0) {
        perror("open drop_caches");
    }

    for (size_t i = 0; i < nreq; ++i) {
        IOReq *r = &reqs[i];

        // Calculate the seek distance between requests
        if (last_offset != -1) {
            seek_distances[i] = llabs(r->offset - last_offset);
        } else {
            seek_distances[i] = 0;
        }

        // Position the read/write head (seek)
        if (lseek64(fd, r->offset, SEEK_SET) < 0) {
            perror("lseek64");
            break;
        }
        
        // Start timing
        gettimeofday(&t_start_op, NULL);
        
        // Execute the I/O operation (read or write)
        ssize_t ret = (r->op_type == 0) ? read(fd, buffer, r->length) : write(fd, buffer, r->length);
        
        // Stop timing
        gettimeofday(&t_end_op, NULL);
        
        // Calculate the total duration of the operation in microseconds
        size_t total_op_us = (size_t)((t_end_op.tv_sec - t_start_op.tv_sec) * 1000000L + (t_end_op.tv_usec - t_start_op.tv_usec));
        
        // Store the measured time
        io_wait_times_us[i] = total_op_us;

        last_offset = r->offset;
        executed++;

        // Perform sync and cache flush operations after the measurement
        // and outside the timed loop
        sync();
        if (fdcleancache >= 0) {
            if (write(fdcleancache, "3", 1) < 0) {
                fprintf(stderr, "cache flush failed, need root\n");
            }
        }
    }

    if (fdcleancache >= 0) {
        close(fdcleancache);
    }
    close(fd);
    return executed;
}


/**
 * @brief Calculates and displays detailed performance statistics.
 * @param n The total number of requests.
 * @param io_wait_raw_us The array of latency times in microseconds.
 * @param seek_bytes The array of seek distances in bytes.
 */
static void print_detailed_stats(size_t n,
                                     size_t *io_wait_raw_us,
                                     long *seek_bytes) {
    ReplayStats stats_io_raw, stats_seek;

    // Calculate the mean and standard deviation for the confidence interval
    double sum = 0.0, mean, std_dev = 0.0;
    for(size_t i = 0; i < n; i++) {
        sum += io_wait_raw_us[i];
    }
    mean = sum / n;
    for(size_t i = 0; i < n; i++) {
        std_dev += pow(io_wait_raw_us[i] - mean, 2);
    }
    std_dev = sqrt(std_dev / n);

    // Calculate the 95% confidence interval (Z-value for 95% is 1.96)
    double ci_95 = 1.96 * (std_dev / sqrt(n));


    size_t *seek_sz = calloc(n, sizeof(size_t));
    if (!seek_sz) { perror("calloc stats temp"); return; }

    for (size_t i = 0; i < n; ++i) {
        seek_sz[i] = (size_t) (seek_bytes[i] >= 0 ? (size_t)seek_bytes[i] : 0);
    }

    // Call the calculate_stats function for the remaining metrics
    calculate_stats(io_wait_raw_us, n, 0, NULL, NULL, &stats_io_raw);
    calculate_stats(seek_sz, n, 0, NULL, NULL, &stats_seek);

    // Display the formatted results
    printf("Mean: %f ms     95%% CI: \xc2\xb1%f ms     Q1: %f ms     Median: %f ms     Q3: %f ms\n",
        mean / 1000.0,
        ci_95 / 1000.0,
        (double)stats_io_raw.q1_us / 1000.0,
        (double)stats_io_raw.median_us / 1000.0,
        (double)stats_io_raw.q3_us / 1000.0);

    free(seek_sz);
}


/* ----------------- main ----------------- */
int main(int argc, char **argv) {
    // Parse command-line arguments
    parse_args(argc, argv, &config);
    if (config.mode != MODE_REPLAY || !config.trace_path || !config.data_file_path) {
        fprintf(stderr, "Usage: %s --mode replay --trace-file <path> --data-file <path>\n", argv[0]);
        return EXIT_FAILURE;
    }

    fprintf(stderr, "INFO: Loading trace from '%s'...\n", config.trace_path);
    IOReq *reqs = NULL;
    size_t nreq = load_trace(config.trace_path, &reqs);
    if (nreq == 0) {
        fprintf(stderr, "Error: No valid requests were loaded.\n");
        return EXIT_FAILURE;
    }
    fprintf(stderr, "INFO: %zu requests loaded.\n", nreq);

    size_t max_len = 0;
    char *buffer = prepare_io_buffer(reqs, nreq, &max_len);
    if (!buffer) {
        free(reqs);
        return EXIT_FAILURE;
    }
    fprintf(stderr, "INFO: I/O buffer of %zu bytes prepared.\n", max_len);

    // Allocate arrays to store the metrics
    size_t *io_wait_raw_us = calloc(nreq, sizeof(size_t));
    long *seek_bytes = calloc(nreq, sizeof(long));
    if (!io_wait_raw_us || !seek_bytes) {
        perror("calloc metrics");
        free(reqs); free(buffer);
        free(io_wait_raw_us); free(seek_bytes);
        return EXIT_FAILURE;
    }

    fprintf(stderr, "INFO: Starting replay...\n");
    // Execute the request replay and collect data
    size_t executed = replay_requests_detailed(reqs, nreq, buffer,
                                               io_wait_raw_us, seek_bytes);
    fprintf(stderr, "INFO: Replay finished. %zu requests executed.\n", executed);

    if (executed > 0) {
        // Display statistics if requests were executed
        print_detailed_stats(executed, io_wait_raw_us, seek_bytes);
    } else {
        fprintf(stderr, "INFO: No requests executed, no statistics.\n");
    }

    // Free all allocated memory
    free(reqs);
    free(buffer);
    free(io_wait_raw_us);
    free(seek_bytes);
    return EXIT_SUCCESS;
}

