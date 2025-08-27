# Makefile pour compiler le benchmark de rejeu d'E/S

# Compilateur C
CC = gcc

# Flags de compilation :
# -O2    : Optimisation de niveau 2
# -Wall  : Activer tous les avertissements
# -g     : Inclure les symboles de débogage
# -D_GNU_SOURCE : Nécessaire pour O_DIRECT et d'autres extensions GNU
CFLAGS = -O2 -Wall -g -D_GNU_SOURCE

# Bibliothèques à lier (linker)
# -lm : Bibliothèque mathématique (pour sqrt)
LDFLAGS = -lm

# Nom de l'exécutable final
TARGET = iortest1

# Fichiers sources (.c)
SOURCES = iortest1.c tools.c

# Fichiers objets (.o) générés à partir des sources
OBJECTS = $(SOURCES:.c=.o)

# Règle par défaut : ce qui est exécuté quand on tape "make"
all: $(TARGET)

# Règle pour lier les fichiers objets et créer l'exécutable
$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJECTS) $(LDFLAGS)

# Règle pour compiler les fichiers sources en fichiers objets
%.o: %.c tools.h
	$(CC) $(CFLAGS) -c $< -o $@

# Règle pour nettoyer les fichiers générés
clean:
	rm -f $(OBJECTS) $(TARGET) log_*.txt

# Déclare que 'all' et 'clean' ne sont pas des noms de fichiers
.PHONY: all clean

