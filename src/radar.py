

def buscar_nave_lineal(tablero_atacado, matriz_rival):
    comparaciones = 0
    for eje1 in range(len(matriz_rival)):
        for eje2 in range(len(matriz_rival[eje1])):
            comparaciones += 1
            if matriz_rival[eje1][eje2].isalpha() and matriz_rival[eje1][eje2] != "o":
                if  tablero_atacado[eje1][eje2] == "~":
                    tablero_atacado[eje1][eje2] = "?"


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

