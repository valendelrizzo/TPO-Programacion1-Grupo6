from radar import sonar_por_planos
import tablero as cubo
import flota

CATALOGO_ARMAS={
    'T': {
        'nombre': 'Torpedo',
        'municion_inicial': None
    },
    'R': {
        'nombre': 'Misil de Racimo',
        'municion_inicial': 3
    },
    'C': {
        'nombre': 'Carga de Profundidad',
        'municion_inicial': 2
    },
    'S': {
        'nombre': 'Sonar',
        'municion_inicial': 4
    },
    'L': {
        'nombre': 'Barrido Laser',
        'municion_inicial': 2
    },
    'O': {
        'nombre': 'Onda Expansiva',
        'municion_inicial': 1
    },
    'G': {
        'nombre': 'Torpedo Guiado',
        'municion_inicial': 1
    }
}


class ErrorArmamento(cubo.ErrorJuego):
    """Arma, objetivo o municion no validos."""
    pass


def crear_municion_jugador():
    """Devuelve municion nueva desde el catalogo; None significa ilimitada."""
    municion = {}
    for codigo in CATALOGO_ARMAS:
        municion[codigo] = CATALOGO_ARMAS[codigo]['municion_inicial']
    return municion


def tiene_municion(codigo_arma, municion_jugador):
    """Devuelve si el arma tiene municion; no modifica datos ni lanza excepciones."""
    if codigo_arma not in municion_jugador:
        return False
    cantidad = municion_jugador[codigo_arma]
    return cantidad is None or cantidad > 0


def descontar_municion(codigo_arma, municion_jugador, consumo):
    """Descuenta consumo y devuelve el saldo. Lanza ErrorArmamento si no alcanza."""
    if codigo_arma not in municion_jugador or consumo < 0:
        raise ErrorArmamento('Arma o consumo invalido.')
    cantidad = municion_jugador[codigo_arma]
    if cantidad is not None:
        if cantidad < consumo:
            raise ErrorArmamento('No queda municion.')
        municion_jugador[codigo_arma] -= consumo
    return municion_jugador[codigo_arma]


def en_rango(tablero, punto):
    """Devuelve si el punto contiene enteros desde 1 hasta N, sin lanzar excepciones."""
    return cubo.validar_punto(tablero, punto)


def validacion_cordenadas(tablero, punto):
    """Devuelve ejecutado o no ejecutado segun el rango del punto, sin modificar datos."""
    if not en_rango(tablero, punto):
        return 'no ejecutado'
    return 'ejecutado'


def ataque_cordenadas(tablero, punto, informacion, flota_rival, ignorar_submarino=False):
    """Aplica un impacto y devuelve su detalle. Recibe punto desde 1; lanza ErrorTablero."""
    if not en_rango(tablero, punto):
        return {'punto': punto, 'resultado': 'invalida'}
    nave = flota.obtener_nave_en_punto(flota_rival, punto)
    if ignorar_submarino and nave is not None and nave['tipo'] == 'S':
        return {'punto': punto, 'resultado': 'inmune'}
    if cubo.leer_celda(tablero, punto) in (cubo.AGUA_MARCADA, cubo.HUNDIDO):
        return {'punto': punto, 'resultado': 'repetido'}
    detalle = flota.registrar_impacto(flota_rival, punto)
    resultado = detalle['resultado']
    simbolo = cubo.IMPACTO
    if resultado == 'repetido':
        simbolo = 'repetido'
    elif resultado == 'agua':
        simbolo = cubo.AGUA_MARCADA
        cubo.escribir_celda(tablero, punto, simbolo)
    else:
        cubo.escribir_celda(tablero, punto, simbolo)
        if resultado == 'hundido':
            for celda in nave['celdas']:
                cubo.escribir_celda(tablero, celda, cubo.HUNDIDO)
    return {'punto': punto, 'resultado': simbolo, 'detalle': detalle}


def crear_resultado_arma(codigo_arma, punto, estado, celdas, municion_restante=None, motivo='ok'):
    """Agrupa los resultados por celda y devuelve el resumen de un ataque, sin excepciones."""
    impactos = []
    agua = []
    invalidas = []
    for item in celdas:
        if item['resultado'] == cubo.IMPACTO:
            impactos.append(item['punto'])
        elif item['resultado'] == cubo.AGUA_MARCADA:
            agua.append(item['punto'])
        else:
            invalidas.append(item['punto'])
    exito = estado == 'ejecutado'
    return {
        'codigo_arma': codigo_arma, 'punto_origen': punto, 'estado': estado,
        'exito': exito, 'motivo': motivo, 'consumo_municion': int(exito),
        'municion_restante': municion_restante, 'celdas': celdas,
        'impactos': impactos, 'agua': agua, 'invalidas': invalidas,
        'cantidad_impactos': len(impactos)
    }


def aplicar_celdas(codigo, tablero, punto, informacion, flota_rival, puntos):
    """Aplica puntos validos y devuelve un resultado. Lanza ErrorTablero ante cubos invalidos."""
    resultados = []
    for celda in puntos:
        resultados.append(ataque_cordenadas(tablero, celda, informacion, flota_rival, codigo == 'L'))
    estado = 'no ejecutado'
    for resultado in resultados:
        if resultado['resultado'] in (cubo.IMPACTO, cubo.AGUA_MARCADA, 'inmune'):
            estado = 'ejecutado'
    motivo = 'ok'
    if estado == 'no ejecutado':
        motivo = 'No hay celdas nuevas para atacar.'
    return crear_resultado_arma(codigo, punto, estado, resultados, motivo=motivo)


def celdas_torpedo(tablero, punto, informacion, flota_rival, eje=None):
    """Devuelve el ataque a una celda desde 1. Usa la flota rival para registrar el impacto."""
    return aplicar_celdas('T', tablero, punto, informacion, flota_rival, [punto])


def celdas_misilracimo(tablero, punto, informacion, flota_rival, eje=None):
    """Devuelve el ataque al centro y sus vecinos ortogonales. Lanza ErrorTablero fuera de rango."""
    puntos = [punto] + cubo.vecinos(tablero, punto)
    return aplicar_celdas('R', tablero, punto, informacion, flota_rival, puntos)


def celdas_cargaprofundidad(tablero, punto, informacion, flota_rival, eje=None):
    """Devuelve el ataque a toda la recta z que pasa por el punto desde 1."""
    z, x, y = punto
    puntos = []
    for valor in range(1, len(tablero) + 1):
        puntos.append((valor, x, y))
    return aplicar_celdas('C', tablero, punto, informacion, flota_rival, puntos)


def celdas_barridolaser(tablero, punto, informacion, flota_rival, eje):
    """Devuelve un ataque sobre x o y, sin afectar submarinos. Lanza ErrorArmamento por eje."""
    if eje not in ('x', 'y'):
        raise ErrorArmamento('El laser requiere el eje x o y.')
    z, x, y = punto
    puntos = []
    for valor in range(1, len(tablero) + 1):
        if eje == 'x':
            puntos.append((z, valor, y))
        else:
            puntos.append((z, x, valor))
    return aplicar_celdas('L', tablero, punto, informacion, flota_rival, puntos)


def celdas_sonar(tablero, punto, informacion, flota_rival, eje=None):
    """Recibe el valor del plano en punto y devuelve contactos, sin dano. Lanza ErrorJuego."""
    if type(punto) != int:
        raise ErrorArmamento('El valor del plano debe ser entero.')
    contactos, tablero = sonar_por_planos(tablero, informacion, eje, punto - 1)
    resultado = crear_resultado_arma('S', None, 'ejecutado', [])
    resultado['contactos'] = contactos
    resultado['eje'] = eje
    resultado['valor'] = punto
    return resultado


def ejecutar_sonar(tablero, informacion, eje, indice, municion_jugador):
    """Recibe un valor desde 1, descuenta municion y devuelve contactos. Lanza ErrorJuego."""
    return selec_catalogo('S', None, tablero, informacion, municion_jugador, [], eje, indice)


def catalogo(municion_jugador=None):
    """Devuelve el catalogo como texto para que el integrador lo muestre, sin excepciones."""
    lineas = []
    for codigo in ('T', 'R', 'C', 'S', 'L'):
        texto = f"{codigo} - {CATALOGO_ARMAS[codigo]['nombre']}"
        if municion_jugador is not None:
            balas = municion_jugador[codigo]
            texto += ' (ilimitada)' if balas is None else f' ({balas} disponibles)'
        lineas.append(texto)
    return '\n'.join(lineas)


ARMAS = {
    'T': celdas_torpedo,
    'R': celdas_misilracimo,
    'C': celdas_cargaprofundidad,
    'S': celdas_sonar,
    'L': celdas_barridolaser
}


def selec_catalogo(opcion, punto, tablero, informacion, municion_jugador, flota_rival,
                  eje=None, indice=None):
    """Despacha el arma y devuelve el resultado. Lanza ErrorArmamento por jugada invalida."""
    if not isinstance(opcion, str):
        raise ErrorArmamento('El arma debe ser una letra.')
    opcion = opcion.strip().upper()
    if opcion not in ARMAS:
        raise ErrorArmamento('Arma no disponible en esta entrega.')
    if not tiene_municion(opcion, municion_jugador):
        raise ErrorArmamento('No queda municion para esa arma.')
    if opcion == 'S':
        punto = indice
    elif not en_rango(tablero, punto):
        raise ErrorArmamento('El objetivo debe estar entre 1 y el tamano del cubo.')
    else:
        punto = tuple(punto)
    resultado = ARMAS[opcion](tablero, punto, informacion, flota_rival, eje)
    if not resultado['exito']:
        raise ErrorArmamento(resultado['motivo'])
    resultado['municion_restante'] = descontar_municion(opcion, municion_jugador, 1)
    return resultado
