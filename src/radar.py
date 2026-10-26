from time import perf_counter
import tablero


def busqueda_nave_lineal(cubo, tipo_nave):
    """Recibe cubo y letra. Devuelve puntos y metricas, sin indice auxiliar ni excepciones."""
    inicio = perf_counter()
    comparaciones = 0
    puntos = []
    for z in range(len(cubo)):
        for x in range(len(cubo[z])):
            for y in range(len(cubo[z][x])):
                comparaciones += 1
                if cubo[z][x][y] == tipo_nave:
                    puntos.append((z + 1, x + 1, y + 1))
    metricas = {
        'comparaciones': comparaciones,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': 0
    }
    return puntos, metricas


def crear_indice_naves(cubo):
    """Devuelve letra -> puntos. Se arma una vez para evitar recorrer el cubo en cada consulta."""
    indice = {}
    for z in range(len(cubo)):
        for x in range(len(cubo[z])):
            for y in range(len(cubo[z][x])):
                letra = cubo[z][x][y]
                if letra in ('F', 'D', 'S', 'C', 'P', 'E'):
                    if letra not in indice:
                        indice[letra] = []
                    indice[letra].append((z + 1, x + 1, y + 1))
    return indice


def busqueda_nave_optimizada(indice, tipo_nave):
    """Recibe indice ya construido y letra. Devuelve puntos y metricas de la consulta."""
    inicio = perf_counter()
    puntos = list(indice.get(tipo_nave, []))
    metricas = {
        'comparaciones': 1,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': 0
    }
    return puntos, metricas


def sonar_por_planos(tablero_atacado, matriz_rival, eje_fijo, indice):
    """Recibe cubos, eje e indice desde 0. Devuelve contactos y cubo; lanza ErrorTablero."""
    contactos = 0
    plano_rival = tablero.obtener_rebanada(matriz_rival, eje_fijo, indice)
    plano_atacado = tablero.obtener_rebanada(tablero_atacado, eje_fijo, indice)
    for i in range(len(plano_rival)):
        for j in range(len(plano_rival[i])):
            if plano_rival[i][j] in ('F', 'D', 'S', 'C', 'P', 'E', tablero.NAVE_OCULTA):
                contactos += 1
                if plano_atacado[i][j] == tablero.AGUA_SIN_EXPLORAR:
                    plano_atacado[i][j] = tablero.DETECTADO
    tablero.aplicar_rebanada(tablero_atacado, plano_atacado, eje_fijo, indice)
    return contactos, tablero_atacado
