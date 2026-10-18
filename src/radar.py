import tablero
import time

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









