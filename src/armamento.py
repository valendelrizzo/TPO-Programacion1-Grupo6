def celdas_misilracimo(tablero, punto, informacion):
    z,x,y = punto
    ataque_cordenadas(tablero, (z,x,y), informacion)
    ataque_cordenadas(tablero, (z+1,x,y), informacion)
    ataque_cordenadas(tablero, (z,x+1,y), informacion)
    ataque_cordenadas(tablero, (z,x,y+1), informacion)
    ataque_cordenadas(tablero, (z-1,x,y), informacion)
    ataque_cordenadas(tablero, (z,x-1,y), informacion)
    ataque_cordenadas(tablero, (z,x,y-1), informacion)

   
def ataque_cordenadas(tablero, punto, informacion):
    if tablero[punto[0]][punto[1]][punto[2]] == "X":
            return None
    
    elif tablero[punto[0]][punto[1]][punto[2]] == "~":
        if informacion[punto[0]][punto[1]][punto[2]] == "#":
            tablero[punto[0]][punto[1]][punto[2]] = "X"
        else:
            tablero[punto[0]][punto[1]][punto[2]] = "0"

def celdas_cargaprofundidad(tablero, punto, informacion):
    _,x,y = punto
    for i in range(len(tablero)):
        ataque_cordenadas(tablero, (x,y,i), informacion)

def celdas_torpedo(tablero, punto, informacion):
    ataque_cordenadas(tablero, punto, informacion)
    return [punto]

CATALOGO_ARMAS = {
        'T': {'nombre': 'Torpedo', 'municion_inicial': None},
        'R': {'nombre': 'Misil de Racimo', 'municion_inicial': 3},
        'C': {'nombre': 'Carga de Profundidad', 'municion_inicial': 2},
        'S': {'nombre': 'Sonar', 'municion_inicial': 4},
        'L': {'nombre': 'Barrido Láser', 'municion_inicial': 2},
        'O': {'nombre': 'Onda Expansiva', 'municion_inicial': 1},
        'G': {'nombre': 'Torpedo Guiado', 'municion_inicial': 1}
        }

def catalogo(tablero, informacion):
   return"""====== CATALOGO ======
T - TORPEDO
R - MISIL DE RACIMO"""

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
    



