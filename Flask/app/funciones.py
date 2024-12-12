# valida que 'name' (el parametro que vendra desde la validacion en proveedor.py) sea igual a uno de los caracteres en char= de ser asi lo retorna
char = '<>"' "!#$%&/()=-.,"


def validarChar(name):
    # se recorre char y se almacena en i
    for i in char:
        if i == name:
            return i

#deberia ser un rut sin puntos y con guion
def validarRut(rut):
    print("validar rut")
    rutGrupo = rut.split("-")
    print(rutGrupo)
    if len(rutGrupo) != 2:
        return False
    num = rutGrupo[0]
    digVerificador = rutGrupo[1]
    #try:
    suma = 0
    multiplicador = 2
    print("antes for")
    print(len(num))
    for i in range(0, len(num)):
        print("i: " + str(i))
        j = len(num) -1 - i
        print("j: " + str(j))
        n = num[j]
        print("n: " + str(n))
        n = int(n)
        suma += n * multiplicador
        print("suma: " + str(suma))
        multiplicador += 1
        if(multiplicador > 7):
            multiplicador = 2
    num = suma
    #except:
        #Si no es posible convertir el num a int tiene un formato incorrecto
        #return False
    mod = (num % 11)
    print("mod1")
    print(mod)
    mod = 11 - mod
    print("mod2")
    print(mod)
    if digVerificador == "k" or digVerificador == "K":
        digVerificador = 10
    else:
        try:
            digVerificador = int(digVerificador)
        except:
            return False
    if mod == digVerificador:
        return True
    else:
        return False

def validarCorreo(correo_funcionario):
    #abandonado
    pass

#define el numero de filas en las tablas para la paginacion
def getPerPage():
    return 15

#categorias
categorias = {
    "Mouse": "accesorio",
    "Teclado": "accesorio",

    "Telefono": "telefono_fijo"


}
