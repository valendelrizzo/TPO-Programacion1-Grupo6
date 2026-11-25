from time import perf_counter
import tablero


NAVE_OCULTA = 'N'
HUNDIDO = '#'
TIPOS_NAVE = ('F', 'D', 'S', 'C', 'P', 'E', NAVE_OCULTA)


class ErrorRadar(tablero.ErrorJuego):
    """Metodo de busqueda, recorrido o parametro de radar invalido."""
    pass


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


def busqueda_nave_lineal(estado):
    """Recorre linealmente los tableros del estado recibido para buscar si hay un ganador."""
    tablero_propio1  = estado["jugador1"]["tablero_propio"]
    tablero_atacado1 = estado["jugador1"]["tablero_atacado"]
    tablero_propio2  = estado["jugador2"]["tablero_propio"]
    tablero_atacado2 = estado["jugador2"]["tablero_atacado"]

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

        if hay_naves and todas_hundidas:
            ganador = posible_ganador
            metricas = {
                    'comparaciones': comparaciones,
                    'tiempo_ms': (perf_counter() - inicio) * 1000,
                    'profundidad_max': 0
                }
            
            return ganador, metricas

    metricas = {
        'comparaciones': comparaciones,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': 0
    }
    return ganador, metricas


def busqueda_nave_recursiva(estado):
    """Busca recursivamente en el estado recibido si alguno de los jugadores hundio toda la flota rival."""
    tablero_propio1 = estado["jugador1"]["tablero_propio"]
    tablero_atacado1 = estado["jugador1"]["tablero_atacado"]
    tablero_propio2 = estado["jugador2"]["tablero_propio"]
    tablero_atacado2 = estado["jugador2"]["tablero_atacado"]

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

        if hay_naves and todas_hundidas:
            ganador = posible_ganador
            metricas = {
                    'comparaciones': comparaciones,
                    'tiempo_ms': (perf_counter() - inicio) * 1000,
                    'profundidad_max': profundidad_max
                }
            
            return ganador , metricas

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


def busqueda_nave_optimizada(estado):
    """Busca un ganador en el estado recibido usando los indices de coordenadas de las naves."""
    indice1 = estado["jugador1"].get("indice_naves") or crear_indice_naves(estado["jugador1"]["tablero_propio"])
    indice2 = estado["jugador2"].get("indice_naves") or crear_indice_naves(estado["jugador2"]["tablero_propio"])
    tablero_atacado1 = estado["jugador1"]["tablero_atacado"]
    tablero_atacado2 = estado["jugador2"]["tablero_atacado"]

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

        if hay_naves and todas_hundidas:
            ganador = posible_ganador

    metricas = {
        'comparaciones': comparaciones,
        'tiempo_ms': (perf_counter() - inicio) * 1000,
        'profundidad_max': 0
    }
    return ganador, metricas


METODOS_BUSQUEDA = {
    '1': busqueda_nave_lineal,
    '2': busqueda_nave_optimizada,
    '3': busqueda_nave_recursiva
}


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

#Mapa probabilidad

def calcular_mapa_probabilidad(tablero_atacado, flota_rival=None):
    """
    Calcula y devuelve una matriz 3D (N x N x N) con el peso de probabilidad de cada celda
    segun las naves rivales aun no hundidas, los contactos de sonar ('?') y los impactos ('X').
    """
    n = len(tablero_atacado)
    mapa = tablero.crear_tablero(n, 0)

    tamanos_lineales = []
    incluye_estacion = False
    if flota_rival:
        for nave in flota_rival:
            if not nave.get('hundida', False):
                if nave.get('tipo') == 'E':
                    incluye_estacion = True
                else:
                    tamanos_lineales.append(len(nave.get('celdas', [])) or 2)
    else:
        tamanos_lineales = [2, 2, 2, 3, 3, 3, 3, 4, 5]
        incluye_estacion = True

    bloqueadas = (tablero.AGUA_MARCADA, tablero.HUNDIDO)
    disparables = (tablero.AGUA_SIN_EXPLORAR, tablero.DETECTADO)

    for largo in tamanos_lineales:
        if largo > n:
            continue
        for z in range(n):
            for x in range(n):
                for y in range(n):
                    tramos = []
                    if z + largo <= n:
                        tramos.append([[z + i, x, y] for i in range(largo)])
                    if x + largo <= n:
                        tramos.append([[z, x + i, y] for i in range(largo)])
                    if y + largo <= n:
                        tramos.append([[z, x, y + i] for i in range(largo)])

                    for tramo in tramos:
                        valido = True
                        impactos_en_tramo = 0
                        for cz, cx, cy in tramo:
                            estado_celda = tablero_atacado[cz][cx][cy]
                            if estado_celda in bloqueadas:
                                valido = False
                                break
                            if estado_celda == tablero.IMPACTO:
                                impactos_en_tramo += 1
                        if valido:
                            peso = 1 + (impactos_en_tramo * 15)
                            for cz, cx, cy in tramo:
                                if tablero_atacado[cz][cx][cy] in disparables:
                                    mapa[cz][cx][cy] += peso

    if incluye_estacion and n >= 4:
        for z in range(1, n - 2):
            for x in range(1, n - 2):
                for y in range(1, n - 2):
                    bloque = [
                        [z + dz, x + dx, y + dy]
                        for dz in (0, 1) for dx in (0, 1) for dy in (0, 1)
                    ]
                    valido = True
                    impactos_bloque = 0
                    for cz, cx, cy in bloque:
                        estado_celda = tablero_atacado[cz][cx][cy]
                        if estado_celda in bloqueadas:
                            valido = False
                            break
                        if estado_celda == tablero.IMPACTO:
                            impactos_bloque += 1
                    if valido:
                        peso = 2 + (impactos_bloque * 15)
                        for cz, cx, cy in bloque:
                            if tablero_atacado[cz][cx][cy] in disparables:
                                mapa[cz][cx][cy] += peso

    direcciones = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
    for z in range(n):
        for x in range(n):
            for y in range(n):
                celda = tablero_atacado[z][x][y]
                if celda == tablero.DETECTADO:
                    mapa[z][x][y] += 25
                elif celda == tablero.IMPACTO:
                    for dz, dx, dy in direcciones:
                        vz, vx, vy = z + dz, x + dx, y + dy
                        if 0 <= vz < n and 0 <= vx < n and 0 <= vy < n:
                            if tablero_atacado[vz][vx][vy] in disparables:
                                bono = 35
                                oz, ox, oy = z - dz, x - dx, y - dy
                                if 0 <= oz < n and 0 <= ox < n and 0 <= oy < n:
                                    if tablero_atacado[oz][ox][oy] == tablero.IMPACTO:
                                        bono += 40
                                mapa[vz][vx][vy] += bono
                elif celda in bloqueadas:
                    mapa[z][x][y] = 0

    return mapa


def mejor_objetivo_probabilidad(tablero_atacado, flota_rival=None):
    """Devuelve (mejor_punto, puntaje_maximo, mapa_probabilidad) con coordenadas desde 1."""
    mapa = calcular_mapa_probabilidad(tablero_atacado, flota_rival)
    n = len(mapa)
    mejor_punto = None
    puntaje_max = -1

    for z in range(n):
        for x in range(n):
            for y in range(n):
                if tablero_atacado[z][x][y] in (tablero.AGUA_SIN_EXPLORAR, tablero.DETECTADO):
                    if mapa[z][x][y] > puntaje_max:
                        puntaje_max = mapa[z][x][y]
                        mejor_punto = [z + 1, x + 1, y + 1]

    return mejor_punto, max(0, puntaje_max), mapa


def dibujar_plano_probabilidad(mapa_prob, eje, valor):
    """Devuelve una representacion en texto de un plano del mapa de probabilidad (valor desde 1)."""
    if type(valor) != int:
        raise tablero.ErrorTablero('El valor del plano debe ser entero.')
    plano = tablero.obtener_rebanada(mapa_prob, eje, valor - 1)
    ejes = {'z': ('x', 'y'), 'x': ('y', 'z'), 'y': ('x', 'z')}
    columnas, filas = ejes[eje]
    lineas = [f'========= MAPA DE PROBABILIDAD {eje}={valor} =========']
    encabezado = '    '
    for i in range(len(mapa_prob)):
        encabezado += f'{columnas}{i + 1:<4}'
    lineas.append(encabezado)
    for fila in range(len(mapa_prob)):
        texto = f'{filas}{fila + 1:<3}'
        for columna in range(len(mapa_prob)):
            if eje == 'z':
                celda = plano[columna][fila]
            else:
                celda = plano[fila][columna]
            texto += f'{celda:<5}'
        lineas.append(texto)
    lineas.append('Valores mas altos indican mayor probabilidad de nave oculta.')
    return '\n'.join(lineas)
