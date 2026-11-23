from time import perf_counter
import tablero


NAVE_OCULTA = 'N'
HUNDIDO = '#'
TIPOS_NAVE = ('F', 'D', 'S', 'C', 'P', 'E', NAVE_OCULTA)


def revisar_planos(propio, atacado, z=0, profundidad=1):
    """Revisa recursivamente un plano por llamada y combina sus resultados."""
    if z == len(propio):
        return False, True, 0, profundidad

    hay_naves = False
    todas_hundidas = True
    comparaciones = 0

    for x in range(len(propio[z])):
        for y in range(len(propio[z][x])):
            comparaciones += 1
            if propio[z][x][y] in TIPOS_NAVE:
                hay_naves = True
                if atacado[z][x][y] != HUNDIDO:
                    todas_hundidas = False

    hay_siguientes, siguientes_hundidas, comparaciones_siguientes, profundidad_max = (
        revisar_planos(propio, atacado, z + 1, profundidad + 1)
    )

    return (
        hay_naves or hay_siguientes,
        todas_hundidas and siguientes_hundidas,
        comparaciones + comparaciones_siguientes,
        profundidad_max,
    )


def busqueda_nave_lineal(tablero_propio1, tablero_atacado1,
                         tablero_propio2, tablero_atacado2):
    """Recorre linealmente los tableros para buscar si hay un ganador."""
    inicio = perf_counter()
    comparaciones = 0
    ganador = None

    candidatos = (
        ('jugador2', tablero_propio1, tablero_atacado2),
        ('jugador1', tablero_propio2, tablero_atacado1),
    )

    for posible_ganador, propio, atacado in candidatos:
        hay_naves = False
        todas_hundidas = True

        for z in range(len(propio)):
            for x in range(len(propio[z])):
                for y in range(len(propio[z][x])):
                    comparaciones += 1
                    if propio[z][x][y] in TIPOS_NAVE:
                        hay_naves = True
                        if atacado[z][x][y] != HUNDIDO:
                            todas_hundidas = False

        if hay_naves and todas_hundidas and ganador is None:
            ganador = posible_ganador

    metricas = {
        'comparaciones': comparaciones,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': 0
    }
    return ganador, metricas


def busqueda_nave_recursiva(tablero_propio1, tablero_atacado1,
                            tablero_propio2, tablero_atacado2):
    """Busca recursivamente si alguno de los jugadores hundio toda la flota rival."""
    inicio = perf_counter()
    comparaciones = 0
    profundidad_max = 0
    ganador = None

    candidatos = (
        ('jugador2', tablero_propio1, tablero_atacado2),
        ('jugador1', tablero_propio2, tablero_atacado1),
    )

    for posible_ganador, propio, atacado in candidatos:
        hay_naves, todas_hundidas, cantidad, profundidad = revisar_planos(
            propio, atacado
        )
        comparaciones += cantidad
        profundidad_max = max(profundidad_max, profundidad)

        if hay_naves and todas_hundidas and ganador is None:
            ganador = posible_ganador

    metricas = {
        'comparaciones': comparaciones,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': profundidad_max
    }
    return ganador, metricas


def crear_indice_naves(cubo):
    """Devuelve letra -> puntos para consultar las naves sin recorrer el cubo."""
    indice = {}
    for z in range(len(cubo)):
        for x in range(len(cubo[z])):
            for y in range(len(cubo[z][x])):
                letra = cubo[z][x][y]
                if letra in TIPOS_NAVE:
                    if letra not in indice:
                        indice[letra] = []
                    indice[letra].append([z + 1, x + 1, y + 1])
    return indice


def busqueda_nave_optimizada(indice1, tablero_atacado1,
                             indice2, tablero_atacado2):
    """Busca un ganador usando los indices de coordenadas de las naves."""
    inicio = perf_counter()
    comparaciones = 0
    ganador = None

    candidatos = (
        ('jugador2', indice1, tablero_atacado2),
        ('jugador1', indice2, tablero_atacado1),
    )

    for posible_ganador, indice, atacado in candidatos:
        hay_naves = False
        todas_hundidas = True

        for puntos in indice.values():
            for z, x, y in puntos:
                comparaciones += 1
                hay_naves = True
                if atacado[z - 1][x - 1][y - 1] != HUNDIDO:
                    todas_hundidas = False

        if hay_naves and todas_hundidas and ganador is None:
            ganador = posible_ganador

    metricas = {
        'comparaciones': comparaciones,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': 0
    }
    return ganador, metricas


def sonar_por_planos(tablero_atacado, matriz_rival, eje_fijo, indice):
    """Recibe cubos, eje e indice desde 0. Devuelve contactos y cubo; lanza ErrorTablero"""
    contactos = 0
    plano_rival = tablero.obtener_rebanada(matriz_rival, eje_fijo, indice)
    plano_atacado = tablero.obtener_rebanada(tablero_atacado, eje_fijo, indice)
    for i in range(len(plano_rival)):
        for j in range(len(plano_rival[i])):
            if plano_rival[i][j] in TIPOS_NAVE:
                contactos += 1
                if plano_atacado[i][j] == tablero.AGUA_SIN_EXPLORAR:
                    plano_atacado[i][j] = tablero.DETECTADO
    tablero.aplicar_rebanada(tablero_atacado, plano_atacado, eje_fijo, indice)
    return contactos, tablero_atacado
