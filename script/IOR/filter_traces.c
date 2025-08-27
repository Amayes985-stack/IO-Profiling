#include <stdio.h>  // Pour fopen, getline, printf, fclose
#include <stdlib.h> // Pour malloc, free, atoi, atol
#include <string.h> // Pour strstr, sscanf, strcmp

// Structure pour stocker les informations d'une opération d'E/S (non utilisée directement mais bonne pratique)
typedef struct {
    char type[10];          // "read" ou "write"
    long fd;                // Descripteur de fichier
    char path[256];         // Chemin du fichier
    long offset;            // Offset de l'opération
    long size_requested;    // Taille demandée
    long bytes_transferred; // Octets réellement transférés
} IoOperation;

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <trace_file.log>\n", argv[0]);
        return EXIT_FAILURE;
    }

    FILE *file = fopen(argv[1], "r");
    if (file == NULL) {
        perror("Impossible d'ouvrir le fichier de trace");
        return EXIT_FAILURE;
    }

    char *line = NULL;
    size_t len = 0;
    ssize_t read_len;

    // Tableau pour stocker l'offset courant par descripteur de fichier.
    // Ajustez la taille si vous vous attendez à des descripteurs de fichiers > 4095.
    long current_offsets[4096] = {0};
    // Flag pour savoir si l'offset d'un FD a été initialisé via lseek ou open.
    int fd_initialized[4096] = {0};

    // En-tête mis à jour pour utiliser des espaces
    printf("Nature_operation Offset Taille_requete\n");
    printf("--------------------------------------\n");

    while ((read_len = getline(&line, &len, file)) != -1) {
        char op_type[10];
        long fd_num;
        char path_buffer[256] = "";

        // Tenter d'analyser les lignes lseek pour mettre à jour les offsets
        long lseek_offset_arg, lseek_result;
        char whence_str[10];
        
        // Regex pour lseek. Exemple: lseek(16<...>, 101429760, SEEK_SET) = 101429760
        if (sscanf(line, "[pid %*d] lseek(%ld<%255[^>]>, %ld, %9[^)]) = %ld", 
                   &fd_num, path_buffer, &lseek_offset_arg, whence_str, &lseek_result) == 5) {
            
            if (fd_num >= 0 && fd_num < 4096) {
                current_offsets[fd_num] = lseek_result;
                fd_initialized[fd_num] = 1;
            }
            continue; // Passer à la ligne suivante
        }
        
        // Tenter d'analyser les lignes read/write
        long size_req, bytes_trans;
        
        // Regex pour read/write. Exemple: read(16<...>, "...", 512) = 512
        if (sscanf(line, "[pid %*d] %9[a-z](%ld<%255[^>]>, %*[^,], %ld) = %ld", 
                   op_type, &fd_num, path_buffer, &size_req, &bytes_trans) == 5) {

            if (fd_num >= 0 && fd_num < 4096 && (strcmp(op_type, "read") == 0 || strcmp(op_type, "write") == 0)) {
                
                // Initialiser l'offset à 0 si c'est la première E/S sur ce FD et qu'aucun lseek n'a été vu
                if (!fd_initialized[fd_num]) {
                    current_offsets[fd_num] = 0; 
                    fd_initialized[fd_num] = 1;
                }

                // On vérifie si la taille de la requête est exactement 512 ET
                // que l'offset courant est un multiple de 512.
                if (size_req == 512 && (current_offsets[fd_num] % 512 == 0)) {
                    // Nature de l'opération (binaire) : 0 pour read (Entrée), 1 pour write (Sortie)
                    int binary_op_type = (strcmp(op_type, "write") == 0) ? 1 : 0;
                    
                    // *** CORRECTION ICI ***
                    // On utilise %d pour la taille, car le programme de rejeu la lit comme un entier.
                    // Les valeurs sont maintenant séparées par un espace.
                    printf("%d %ld %d\n", 
                           binary_op_type, 
                           current_offsets[fd_num], 
                           (int)size_req);
                }

                // Mettre à jour l'offset pour la prochaine opération, que la requête ait été affichée ou non.
                if (bytes_trans > 0) {
                    current_offsets[fd_num] += bytes_trans;
                }
            }
        }
    }

    free(line);
    fclose(file);
    return EXIT_SUCCESS;
}

