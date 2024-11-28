
def inLinux():
   return True

if(not inLinux):
    paths = {
        "pdf_path": r'C:\Users\Junji\Downloads\Junji_inventario-main1\Junji_inventario-main\Junji_inventario-main\app\pdf'
        ,
    }
else:
    paths = {
        "pdf_path": r"~/Junji_inventario-main/app/pdf"

    }

cuentas = {
    #db
    "nombre_usuario": "junji",
    "contrasenna": "Tijunji2017",
    #correo para enviar a funcionarios
    "nombre_correo": "martin.castro@junji.cl",
    "correo_contrasenna": "junji.2024"
}



#cuenta servidor
#nombre_usuario : "junji"
#contraseña : "Tijunji2017"
#cuenta local
#nombre_usuario: "root"
#contraseña: ""
