# inventario-junji

Este proyecto es una aplicación web construida con **Flask** (Python) y una base de datos **MySQL**, administrada desde **MySQL Workbench**.

---

## 🛠️ Requisitos

Antes de comenzar, asegúrate de tener lo siguiente instalado en tu sistema:

- Python <= 3.12.4
- MySQL Server
- MySQL Workbench
- pip (el gestor de paquetes de Python)
- Git (para clonar el repositorio)

---

## 🚀 Instalación

### 1. Clona este repositorio

```bash
git clone https://github.com/tu-usuario/tu-repo.git](https://github.com/infocardenas/inventario-junji.git
cd inventario-junji
```

## 🔁 Cómo importar (restaurar) backup

### Ruta del bachup
```bash
/mnt/backups/backups_inventariofinal
```


### 1. Extraer el archivo .tar.gz
Primero descomprime el archivo de respaldo:
```bash
tar -xzvf backup_total_YYYY-MM-DD.tar.gz -C /ruta/donde/quieras/descomprimir
```
Reemplaza YYYY-MM-DD por la fecha que corresponda y /ruta/... por donde quieras.

### 2. Ubica el archivo .sql
Después de descomprimir, deberías tener un archivo como:
```bash
bd_2025-06-06.sql
```
### 3. Restaurar la base de datos MySQL
Asegúrate de que la base de datos inventariofinal exista. Si no, créala:
```bash
mysql -u tu_usuario -p -e "CREATE DATABASE inventariofinal;"
```
Luego, importa el SQL:
```bash
mysql -u tu_usuario -p inventariofinal < /ruta/a/bd_2025-06-06.sql
```
Si usas un archivo de configuración .my.cnf como en el script, puedes hacer:
