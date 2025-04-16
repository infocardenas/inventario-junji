#!/bin/bash

# Configuración
FECHA=$(date +%F_%H-%M)
RAMA="copia_seguridad"
REPO_DIR="/home/junji/inventario-junji"
BACKUP_DIR="$REPO_DIR/backup_$FECHA"
LOG_FILE="$REPO_DIR/backup_log.txt"

# Crear carpeta para el backup
mkdir -p "$BACKUP_DIR"

# 1. Respaldo de archivos del sistema
echo "[$FECHA] Iniciando respaldo de archivos..." >> $LOG_FILE
rsync -av --exclude='.git' /etc /home "$BACKUP_DIR/" >> $LOG_FILE 2>&1

# 2. Respaldo de base de datos MySQL usando ~/.my.cnf
echo "[$FECHA] Iniciando respaldo de base de datos MySQL..." >> $LOG_FILE
mysqldump --defaults-file=~/.my.cnf --all-databases > "$BACKUP_DIR/bd_$FECHA.sql" 2>> $LOG_FILE

# 3. Ir al repositorio local
cd "$REPO_DIR" || { echo "[$FECHA] ERROR: No se pudo acceder al repositorio" >> $LOG_FILE; exit 1; }

# 4. Cambiar a la rama de respaldo o crearla si no existe
if git rev-parse --verify $RAMA >/dev/null 2>&1; then
    git checkout $RAMA >> $LOG_FILE 2>&1
else
    git checkout -b $RAMA >> $LOG_FILE 2>&1
fi

# 5. Agregar y commitear los cambios
git add . >> $LOG_FILE 2>&1
git commit -m "Backup del $FECHA" >> $LOG_FILE 2>&1

# 6. Subir al repositorio remoto
git push origin $RAMA >> $LOG_FILE 2>&1

echo "[$FECHA] Backup completo y subido correctamente a la rama '$RAMA'" >> $LOG_FILE
