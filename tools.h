#ifndef TOOLS_H
#define TOOLS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/time.h>
#include <errno.h>
#include <math.h>
#include <time.h>

#define SECTOR_SIZE 4096

// Énumération pour les différents modes de fonctionnement
typedef enum {
    MODE_READ,
    MODE_WRITE,
    MODE_REPLAY
} BenchMode;

// Structure pour stocker la configuration de l'application
typedef struct {
    BenchMode mode;
    size_t nb_run;
    size_t nb_bloc;
    size_t sz_bloc;
    size_t filesize;  // Doit être présent
    char *trace_path;
    char *data_file_path;
    char *log_prefix;
    size_t data_file_size;
} AppConfig;

// Structure pour stocker les résultats statistiques
typedef struct {
    size_t total_ops;
    size_t total_bytes;
    double total_duration_s;
    double mean_us;
    double stdev_us;
    double ci95_us; // <--- VÉRIFIEZ BIEN QUE CETTE LIGNE EST PRÉSENTE
    double iops;
    double throughput_mbs;
    size_t min_latency_us;
    size_t max_latency_us;
    size_t q1_us;
    size_t median_us;
    size_t q3_us;
} ReplayStats;


// --- Prototypes des Fonctions ---
void parse_args(int argc, char **argv, AppConfig *config);
size_t get_val_arg(const char *arg);
void make_file_if_necessary(const char *path, size_t size);
void calculate_stats(const size_t *times, size_t op_count, size_t total_bytes, const struct timeval *start, const struct timeval *end, ReplayStats *stats);
void log_times(const char *path, const size_t *times, size_t n);
void log_timestamps(const char *path, const struct timeval *timestamps, size_t n);
void format_timestamp(struct timeval *tv, char *buffer, size_t buffer_size);

#endif // TOOLS_H
