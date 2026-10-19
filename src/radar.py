"""
importe la funcion perf_counter del modulo time para poder sacar las metricas de la funcion(el tiempo)
Busqueda optimizada solo revisa posiciones pares reduciendo el tiempo, pero no muestra todo el barco, solo algunos ?
Uso round para acortar el numero que me tira perf_counter

Cosas que supuse:
En el TPO  
Sonar por planos -> usa a tablero.py.
Mientras que las busquedas recorren todo el cubo. Devolviendo metricas y resultados.
Por lo que entendi sonar por planos es una funcion diferente a las 3 busquedas. 
La busqueda optimizada no devuelve todas las posiciones del barco que encontro, detecta partes de los barcos si, en las posiciones pares. Osea no todo el barco

"""


from time import perf_counter
from tablero import obtener_rebanada, aplicar_rebanada

def buscar_nave_lineal(tablero_atacado, matriz_rival, nave):
    """
    Búsqueda lineal completa en todo el cubo (z, x, y) celda por celda.
    Busca la nave específica indicada en el parámetro 'nave'.
    """
    comparaciones = 0
    inicio_tiempo = perf_counter()
    n = len(matriz_rival)
    nave_buscada = nave.upper()
    
    for z in range(n):
        for x in range(n):
            for y in range(n):
                comparaciones += 1
                celda = matriz_rival[z][x][y]
                
                # Comparación directa con la nave recibida
                if celda.upper() == nave_buscada:
                    if tablero_atacado[z][x][y] == "~":
                        tablero_atacado[z][x][y] = "?"

    fin_tiempo = perf_counter()
    tiempo_ms = (fin_tiempo - inicio_tiempo) * 1000

    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": round(tiempo_ms, 2),
        "profundidad_max": 3
    }
    
    return metricas, tablero_atacado


def buscar_nave_optimizada(tablero_atacado, matriz_rival, nave):
    comparaciones = 0
    inicio_tiempo = perf_counter()
    n = len(matriz_rival)
    nave_buscada = nave.upper()
    
    # Recorremos el cubo aplicando el filtro de ajedrez 3D (paridad)
    for z in range(n):
        for x in range(n):
            for y in range(n):
                if (z + x + y) % 2 == 0:
                    comparaciones += 1
                    celda = matriz_rival[z][x][y]
                    
                    if celda.upper() == nave_buscada:
                        if tablero_atacado[z][x][y] == "~":
                            tablero_atacado[z][x][y] = "?"

    fin_tiempo = perf_counter()
    tiempo_ms = (fin_tiempo - inicio_tiempo) * 1000

    metricas = {
        "comparaciones": comparaciones,
        "tiempo_ms": round(tiempo_ms, 2),
        "profundidad_max": 3
    }
    
    return metricas, tablero_atacado
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
