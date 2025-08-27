#include "tools.h"
#include <stdio.h>    // Pour fprintf, perror
#include <stdlib.h>   // Pour atoll, malloc, free, qsort, exit
#include <string.h>   // Pour strlen, strcmp, memcpy, memset
#include <math.h>     // Pour sqrt
#include <sys/stat.h> // Pour stat64
#include <fcntl.h>    // Pour open64
#include <unistd.h>   // Pour close, write, read, sync
#include <errno.h>    // Pour errno
#include <time.h>     // Pour struct tm, localtime, strftime, time_t (ajouté pour format_timestamp)

// Votre fonction pour parser les valeurs avec suffixes (k, M, G)
size_t get_val_arg(const char *arg) {
    size_t value;
    char last_character;

    value = atoll(arg);
    last_character = arg[strlen(arg) - 1];
    switch (last_character) {
        case 's': case 'S': value *= 512; break;
        case 'k': case 'K': value *= 1 << 10; break;
        case 'm': case 'M': value *= 1 << 20; break;
        case 'g': case 'G': value *= 1 << 30; break;
        default: break;
    }
    return value;
}

// Nouvelle fonction parse_args qui gère tous les modes
void parse_args(int argc, char **argv, AppConfig *config) {
    // Valeurs par défaut
    config->mode = MODE_READ; // Mode par défaut
    config->nb_run = 100;
    config->nb_bloc = 1;
    config->sz_bloc = 1 * 1024 * 1024; // 1M
    config->trace_path = "filtered_trace.log";
    config->data_file_path = "/tmp/iortest.file";
    config->log_prefix = "log_iortest";
    config->data_file_size = 256 * 1024 * 1024; // 256M

    // On utilise un parsing manuel simple, plus proche de votre original
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--mode")) {
            i++;
            if (i >= argc) continue;
            if (!strcmp(argv[i], "read")) config->mode = MODE_READ;
            else if (!strcmp(argv[i], "write")) config->mode = MODE_WRITE;
            else if (!strcmp(argv[i], "replay")) config->mode = MODE_REPLAY;
        } else if (!strcmp(argv[i], "--nb_run")) {
            i++; if (i < argc) config->nb_run = get_val_arg(argv[i]);
        } else if (!strcmp(argv[i], "--nb_bloc")) {
            i++; if (i < argc) config->nb_bloc = get_val_arg(argv[i]);
        } else if (!strcmp(argv[i], "--sz_bloc")) {
            i++; if (i < argc) config->sz_bloc = get_val_arg(argv[i]);
        } else if (!strcmp(argv[i], "--filesize")) {
            i++; if (i < argc) config->data_file_size = get_val_arg(argv[i]);
        } else if (!strcmp(argv[i], "--trace-file")) {
            i++; if (i < argc) config->trace_path = argv[i];
        } else if (!strcmp(argv[i], "--data-file")) { // Ajout de l'option --data-file
            i++; if (i < argc) config->data_file_path = argv[i];
        } else if (!strcmp(argv[i], "--help")) {
            fprintf(stderr, "Usage: %s --mode <read|write|replay> [options]\n", argv[0]);
            fprintf(stderr, "\n--- Options de Génération ---\n");
            fprintf(stderr, "  --nb_run <N>           Nombre d'opérations à effectuer (défaut: 100)\n");
            fprintf(stderr, "  --nb_bloc <N>          Nombre de blocs par opération (défaut: 1)\n");
            fprintf(stderr, "  --sz_bloc <N>          Taille d'un bloc (ex: 512, 4k, 1M) (défaut: 1M)\n");
            fprintf(stderr, "\n--- Options de Rejeu ---\n");
            fprintf(stderr, "  --trace-file <path>    Chemin du fichier de trace (défaut: filtered_trace.log)\n");
            fprintf(stderr, "  --data-file <path>     Chemin du fichier de données pour le rejeu (défaut: /tmp/iortest.file)\n"); // Ajout de l'aide
            fprintf(stderr, "\n--- Options Communes ---\n");
            fprintf(stderr, "  --filesize <N>         Taille du fichier de données (ex: 256M, 4G) (défaut: 256M)\n");
            exit(0);
        }
    }
}

// Fonction pour comparer, nécessaire pour qsort
int compare_size_t(const void *a, const void *b) {
    size_t val1 = *(const size_t*)a;
    size_t val2 = *(const size_t*)b;
    return (val1 > val2) - (val1 < val2);
}

// Calcule les statistiques
void calculate_stats(const size_t *times, size_t op_count, size_t total_bytes, const struct timeval *start, const struct timeval *end, ReplayStats *stats) {
    if (op_count == 0) {
        // Initialiser toutes les stats à zéro si aucune opération
        memset(stats, 0, sizeof(ReplayStats));
        return;
    }

    size_t sum = 0;
    double sum_sq = 0;
    
    // Initialiser min_latency_us avec la première valeur (si op_count > 0)
    stats->min_latency_us = times[0]; 
    stats->max_latency_us = 0;

    for (size_t i = 0; i < op_count; ++i) {
        sum += times[i];
        sum_sq += (double)times[i] * times[i];
        if (times[i] < stats->min_latency_us) stats->min_latency_us = times[i];
        if (times[i] > stats->max_latency_us) stats->max_latency_us = times[i];
    }

    stats->total_ops = op_count;
    stats->total_bytes = total_bytes;
    stats->mean_us = (double)sum / op_count;
    double variance = (sum_sq / op_count) - (stats->mean_us * stats->mean_us);
    stats->stdev_us = sqrt(variance > 0 ? variance : 0);
    
    // CORRECTION ICI : Vérifier si start et end sont non NULL avant de les utiliser
    if (start && end) {
        stats->total_duration_s = (end->tv_sec - start->tv_sec) + (double)(end->tv_usec - start->tv_usec) / 1e6;
        stats->iops = stats->total_duration_s > 0 ? (double)op_count / stats->total_duration_s : 0;
        stats->throughput_mbs = stats->total_duration_s > 0 ? (double)total_bytes / stats->total_duration_s / (1024 * 1024) : 0;
    } else {
        // Si start ou end sont NULL, ces statistiques ne peuvent pas être calculées
        stats->total_duration_s = 0;
        stats->iops = 0;
        stats->throughput_mbs = 0;
    }
    
    // Calcul des quartiles (nécessite au moins 4 points pour Q1 et Q3, 2 pour médiane)
    // Pour 8 points, c'est bon. Pour moins, les indices peuvent être problématiques.
    // Une implémentation plus robuste gérerait les cas où op_count est très petit.
    // Pour l'instant, nous nous basons sur l'hypothèse que op_count est suffisant.
    size_t *sorted_times = malloc(op_count * sizeof(size_t));
    if (!sorted_times) {
        perror("malloc sorted_times");
        // Ne pas sortir, mais ne pas calculer les quartiles
        stats->q1_us = 0;
        stats->median_us = 0;
        stats->q3_us = 0;
        stats->ci95_us = 0; // Pas de CI sans calcul
        return;
    }
    memcpy(sorted_times, times, op_count * sizeof(size_t));
    qsort(sorted_times, op_count, sizeof(size_t), compare_size_t);
    
    // Calcul des quartiles :
    // Pour un petit nombre de points, les indices peuvent être 0.
    // Par exemple, pour 8 points:
    // Q1: sorted_times[8/4 - 1] = sorted_times[1] (si 1-indexed) ou sorted_times[op_count / 4] = sorted_times[2] (si 0-indexed)
    // La formule standard pour les quartiles peut varier légèrement.
    // Ici, nous utilisons une version simple basée sur l'index.
    // Pour 8 éléments (0 à 7):
    // Q1 (25%): index 2 (valeur à la 3ème position)
    // Median (50%): index 4 (valeur à la 5ème position)
    // Q3 (75%): index 6 (valeur à la 7ème position)
    // C'est pourquoi op_count / 4, op_count / 2, 3 * op_count / 4 sont utilisés comme indices 0-based.
    // Si op_count est 8:
    // q1_us = sorted_times[2]
    // median_us = sorted_times[4]
    // q3_us = sorted_times[6]
    // Cela semble correct pour 8 éléments.
    
    stats->q1_us = sorted_times[op_count / 4];
    stats->median_us = sorted_times[op_count / 2];
    stats->q3_us = sorted_times[3 * op_count / 4];

    // Calcul de l'intervalle de confiance (très simplifié ici, nécessite plus de points pour être précis)
    // Pour un petit échantillon (n < 30), il faudrait utiliser une distribution de Student.
    // Ici, on utilise une approximation basée sur la distribution normale (Z=1.96 pour 95% CI)
    // Ce calcul peut être imprécis pour n=8, mais n'est pas la cause du segfault.
    stats->ci95_us = 1.96 * stats->stdev_us / sqrt((double)op_count);

    free(sorted_times);
}

// Affiche les statistiques
void print_stats(const ReplayStats *stats) {
    printf("\n--- Statistiques du Benchmark ---\n");
    printf("Opérations Exécutées : %zu\n", stats->total_ops);
    printf("Données Transférées  : %.2f MB\n", (double)stats->total_bytes / (1024 * 1024));
    printf("Durée Totale         : %.3f secondes\n", stats->total_duration_s);
    printf("-----------------------------\n");
    printf("Débit Moyen          : %.2f IOPS\n", stats->iops);
    printf("Débit Moyen          : %.2f MB/s\n", stats->throughput_mbs);
    printf("-----------------------------\n");
    printf("Latence (µs)         :\n");
    printf("  Moyenne            : %.2f µs\n", stats->mean_us);
    printf("  Écart-type         : %.2f µs\n", stats->stdev_us);
    printf("  Min / Max          : %zu µs / %zu µs\n", stats->min_latency_us, stats->max_latency_us);
    printf("  Quartiles (Q1/Med/Q3): %zu µs / %zu µs / %zu µs\n", stats->q1_us, stats->median_us, stats->q3_us);
    printf("  95%% CI             : ±%.2f µs\n", stats->ci95_us); // Ajout de l'affichage du CI
    printf("-----------------------------\n");
}

// Crée le fichier de données
void make_file_if_necessary(const char *path, size_t filesize) {
    const size_t _BUF_SIZE = 1<<22;
    char buffer[_BUF_SIZE];
    size_t total_written = 0;
    int fd, fdrand, fdcleancache;
    
    struct stat64 file_stat;
    if(stat64(path, &file_stat) < 0){
        if(errno != ENOENT) { perror("stat64"); exit(1); }
    } else {
        if(file_stat.st_size >= (off64_t)filesize) return;
    }

    printf("Création du fichier de données '%s' de taille %zu octets...\n", path, filesize);
    fd = open64(path, O_WRONLY | O_CREAT | O_TRUNC, 0666);
    if(fd < 0) { perror("open64 create"); exit(1); }
    fdrand = open("/dev/urandom", O_RDONLY);
    if(fdrand < 0) { perror("open /dev/urandom"); exit(1); }

    while(total_written < filesize){
        size_t buf_size = (filesize - total_written > _BUF_SIZE) ? _BUF_SIZE : (filesize - total_written);
        if(read(fdrand, buffer, buf_size) <= 0) { perror("read from urandom"); exit(1); }
        ssize_t written = write(fd, buffer, buf_size);
        if(written < 0) { perror("write to data file"); exit(1); }
        total_written += written;
    }
    
    close(fd);
    close(fdrand);

    sync();
    fdcleancache = open("/proc/sys/vm/drop_caches", O_WRONLY);
    if (fdcleancache >= 0) {
        if(write(fdcleancache, "3", 1) < 0) {
            fprintf(stderr, "Avertissement: Échec du vidage du cache (besoin de droits root).\n");
        }
        close(fdcleancache);
    }
}

// Fonctions de logging
void log_times(const char *path, const size_t *times, size_t n) {
    FILE *file = fopen(path, "w");
    if (!file) { perror("fopen log_times"); return; }
    for(size_t i = 0; i < n; i++) fprintf(file, "%zu\n", times[i]);
    fclose(file);
}

void format_timestamp(struct timeval *tv, char *buffer, size_t buffer_size) {
    // CORRECTION ICI : Déclaration de time_string
    char time_string[64]; 
    struct tm *tm_info;
    time_t now = tv->tv_sec;
    tm_info = localtime(&now);
    strftime(time_string, sizeof(time_string), "%Y-%m-%dT%H:%M:%S", tm_info);
    snprintf(buffer, buffer_size, "%s.%06ld", time_string, tv->tv_usec);
}

void log_timestamps(const char *path, const struct timeval *timestamps, size_t n) {
    FILE *file = fopen(path, "w");
    if (!file) { perror("fopen log_timestamps"); return; }
    char buffer[128];
    for (size_t i = 0; i < n; i++) {
        format_timestamp((struct timeval*)&timestamps[i], buffer, sizeof(buffer));
        fprintf(file, "%s\n", buffer);
    }
    fclose(file);
}
