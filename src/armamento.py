#aciertosTorpedos = 0

def celdas_torpedo(tablero, punto, informacion):
    if tablero[punto[0]][punto[1]][punto[2]] == "X":
        return None
    
    elif tablero[punto[0]][punto[1]][punto[2]] == "~":
        if informacion[punto[0]][punto[1]][punto[2]] == "#":
           tablero[punto[0]][punto[1]][punto[2]] = "X"
           #aciertosTorpedos = aciertosTorpedos + 1
        else:
           tablero[punto[0]][punto[1]][punto[2]] = "0"
    return [punto]

CATALOGO_ARMAS = {
        'T': {'nombre': 'Torpedo', 'municion_inicial': None}
        }

def catalogo(tablero, informacion):
   return"""====== CATALOGO ======
T - TORPEDO"""

   #opcion = input("INGRESE UNA OPCION:")
   #opcion = opcion.upper()
   #z = int(input("INGRESE LA CORDENADA Z: "))
   #x = int(input("INGRESE LA CORDENADA X: "))
   #y = int(input("INGRESE LA CORDENADA Y: "))
   #selec_catalogo(opcion, (z,x,y), tablero, informacion)
   


def selec_catalogo(opcion, punto, tablero, informacion):
  match opcion:
    case "T":
        celdas_torpedo(tablero, punto, informacion)
        #registro(celdas_torpedo(tablero, punto, informacion))
    case _:
        print("OPCION INVALIDA!")
        catalogo(tablero, informacion)
    



