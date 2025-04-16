#!/bin/bash

# Configuración
FECHA=$(date +%F_%H-%M)
RAMA="copia_seguridad"
REPO_DIR="/home/junji/inventario-junji"
BACKUP_DIR="$REPO_DIR/backup_$FECHA"
LOG_FILE="$REPO_DIR/backup_log.txt"

# Crear carpeta para el backup
mkdir -p "$BACKUP_DIR"

# Archivos a respaldar
echo "[$FECHA] Iniciando respaldo..." >> $LOG_FILE
rsync -av --exclude='.git' /etc /home "$BACKUP_DIR/" >> $LOG_FILE 2>&1

# Ir al repositorio
cd "$REPO_DIR" || { echo "No se pudo acceder al repositorio"; exit 1; }

# Cambiar o crear la rama de respaldo
if git rev-parse --verify $RAMA >/dev/null 2>&1; then
    git checkout $RAMA
else
    git checkout -b $RAMA
fi

# Agregar y commitear los cambios
git add .
git commit -m "Backup del $FECHA" >> $LOG_FILE 2>&1

# Subir al remoto
git push origin $RAMA >> $LOG_FILE 2>&1

echo "[$FECHA] Backup completo y enviado a la rama '$RAMA'" >> $LOG_FILE
