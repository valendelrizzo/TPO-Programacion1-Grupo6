

def buscar_nave_lineal(tablero_atacado, tablero_rival, pos):
    comparaciones = 0
    z = pos
    for y in range(len(tablero_rival[z])):
        for x in range(len(tablero_rival[z][y])):
            comparaciones += 1
            if tablero_rival[z][y][x].isalpha() and tablero_rival[z][y][x] != "o":
                if  tablero_atacado[z][y][x] == "~":
                    tablero_atacado[z][y][x] = "?"


    metricas = {
        "comparaciones": "x",
        "tiempo_ms": "x",
        "profundidad_max": "x"
    }
    
    
    return metricas, tablero_atacado

def menu_radares():
    return """
1- Busqueda lineal
"""
    
   

def main_radares(tablero_atacado, tablero_propio2, pos): 
    print(menu_radares())
    ingreso = int(input("tipo de radar? "))
    match ingreso: 
        case 1: 
            tablero_atacado = buscar_nave_lineal(tablero_atacado, tablero_propio2, pos)

    return tablero_atacado

