

from time import perf_counter
from tablero import obtener_rebanada, aplicar_rebanada

def busqueda_nave_lineal(tablero_propio1, tablero_atacado1, tablero_propio2, tablero_atacado2):
    """ Si hay ganador devuelve ganador sino None + metricas
    compara cada conjunto de tableros... tablero propio + tablero atacado (del oponente)
    """
    inicio = perf_counter()
    comparaciones = 0
    ganador = None

    tableros = (
        ("jugador2", tablero_propio1, tablero_atacado2),
        ("jugador1", tablero_propio2, tablero_atacado1),
    )

    for posible_ganador, tablero_propio, tablero_atacado in tableros:
        hay_naves = False
        todas_impactadas = True

        for z in range(len(tablero_propio)):
            for x in range(len(tablero_propio[z])):
                for y in range(len(tablero_propio[z][x])):
                    comparaciones += 1
                    celda = tablero_propio[z][x][y]

                    if celda not in ("~", "o", " ", 0):
                        hay_naves = True
                        if tablero_atacado[z][x][y] != "X":
                            todas_impactadas = False

        if hay_naves and todas_impactadas and ganador is None:
            ganador = posible_ganador

    tiempo_ms = (perf_counter() - inicio) * 1000
    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": round(tiempo_ms, 2),
        "profundidad_max": 3,
    }

    return ganador, metricas



def sonar_por_planos(tablero_atacado, matriz_rival, eje_fijo, indice):
    """
    Sonar: Extrae rebanada, cuenta contactos 
    y actualiza el tablero atacado usando aplicar_rebanada.
    
    """
    contactos = 0
    
    # Extraemos las rebanadas del cubo usando el módulo tablero
    plano_rival = obtener_rebanada(matriz_rival, eje_fijo, indice)
    plano_atacado = obtener_rebanada(tablero_atacado, eje_fijo, indice)
    
    n = len(plano_rival)
    
    for i in range(n):
        for j in range(n):
            celda = plano_rival[i][j]
            
            # Si hay una nave presente en el plano
            if celda != "~" and celda != "o" and celda != " ":
                contactos += 1
                if plano_atacado[i][j] == "~":
                    plano_atacado[i][j] = "?"
                    
    # Se aplica cambios que hice en el rebanado 
    aplicar_rebanada(tablero_atacado, plano_atacado, eje_fijo, indice)

    return contactos, tablero_atacado
