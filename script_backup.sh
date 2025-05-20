#!/bin/bash

# Configuración
FECHA=$(date +%F)
DESTINO="/mnt/backups/inventario_junji"
ARCHIVOS_BACKUP="$DESTINO/archivos_$FECHA"
SQL_BACKUP="$DESTINO/bd_$FECHA.sql"
BACKUP_TOTAL="$DESTINO/backup_total_$FECHA.tar.gz"

# Crear carpeta destino si no existe
sudo mkdir -p $DESTINO

echo "[$FECHA] Iniciando respaldo..."

# 1. Backup de archivos del sistema
echo "Respaldando /home y /etc en $ARCHIVOS_BACKUP..."
rsync -avz /home /etc "$ARCHIVOS_BACKUP"

# 2. Backup de base de datos (usando ~/.my.cnf para evitar contraseña en el script)
echo "Respaldando base de datos MySQL..."
mysqldump --defaults-file=~/.my.cnf inventariofinal > "$SQL_BACKUP"

# 3. Comprimir todo
echo "Comprimiendo respaldo en $BACKUP_TOTAL..."
tar -czvf "$BACKUP_TOTAL" "$ARCHIVOS_BACKUP" "$SQL_BACKUP"

# 4. Limpiar archivos temporales
echo "Limpiando archivos temporales..."
rm -r "$ARCHIVOS_BACKUP" "$SQL_BACKUP"

echo "[$FECHA] Respaldo completado exitosamente en $BACKUP_TOTAL"
