import tablero


gPartidaActual={}


class ErrorRegistro(tablero.ErrorJuego):
    """Operacion de registro no disponible o invalida"""
    pass


def crear_partida(navesJ1, navesJ2, nombre=''):
    """Recibe ambas flotas y un nombre; devuelve un registro nuevo sin excepciones"""
    return {'nombre': nombre, 'naves1': navesJ1, 'naves2': navesJ2, 'movimientos': []}


def crear_movimiento(arma, celdas):
    """Recibe arma y resultados; devuelve un movimiento sin modificar los datos"""
    return {'arma': arma, 'celdasAfectadas': celdas}


def get_estado_actual():
    """Devuelve el registro actual en memoria, sin lanzar excepciones"""
    return gPartidaActual


def registrar_ataque(arma, celdasAfectadas):
    """Agrega un ataque al registro actual. Lanza ErrorRegistro si no fue iniciado"""
    if not gPartidaActual:
        raise ErrorRegistro('Primero debe iniciarse el registro.')
    gPartidaActual['movimientos'].append(crear_movimiento(arma, celdasAfectadas))


def iniciar_partida(navesJ1, navesJ2, nombre=''):
    """Inicia y devuelve el registro global con las flotas recibidas, sin excepciones"""
    global gPartidaActual
    gPartidaActual = crear_partida(navesJ1, navesJ2, nombre)
    return gPartidaActual


def terminar_partida(nombre=None):
    """Devuelve el registro actual y completa su nombre si faltaba, sin excepciones"""
    if not gPartidaActual:
        return crear_partida([], [])
    if not gPartidaActual['nombre'] and nombre:
        gPartidaActual['nombre'] = nombre
    return gPartidaActual


def registrar_jugada(estado, jugada):
    """Agrega una jugada al historial del estado y devuelve el estado actualizado"""
    estado['historial'].append(jugada)
    return estado


def estadisticas(estado):
    """Recibe el estado y devuelve estadisticas de ambos jugadores a partir del historial"""
    resumen = {}
    for clave in ('jugador1', 'jugador2'):
        jugador = estado[clave]
        datos = {'turnos': 0, 'disparos': 0, 'impactos': 0, 'agua': 0,
                 'sonares': 0, 'hundidas': 0, 'precision': 0.0}
        for jugada in estado['historial']:
            if jugada['jugador'] == jugador['nombre']:
                datos['turnos'] += 1
                if jugada['arma'] == 'S':
                    datos['sonares'] += 1
                else:
                    datos['disparos'] += 1
                for celda in jugada['celdas']:
                    if celda['resultado'] == tablero.IMPACTO:
                        datos['impactos'] += 1
                        if celda['detalle']['resultado'] == 'hundido':
                            datos['hundidas'] += 1
                    elif celda['resultado'] == tablero.AGUA_MARCADA:
                        datos['agua'] += 1
        total = datos['impactos'] + datos['agua']
        if total:
            datos['precision'] = round(datos['impactos'] * 100 / total, 2)
        resumen[clave] = datos
    return resumen


def resumen_partida(estado):
    """Devuelve el ganador y las estadisticas finales del estado recibido, sin modificarlo"""
    return {'ganador': estado['ganador'], 'jugadores': estadisticas(estado)}


def guardar_partida(estado, nombre):
    """Recibe estado y nombre. Lanza ErrorRegistro: el guardado corresponde a la entrega 3"""
    raise ErrorRegistro('Guardar partidas corresponde a la entrega 3.')


def cargar_partida(nombre):
    """Recibe un nombre. Lanza ErrorRegistro: la carga corresponde a la entrega 3"""
    raise ErrorRegistro('Cargar partidas corresponde a la entrega 3.')


def listar_partidas():
    """Lanza ErrorRegistro: el listado de partidas corresponde a la entrega 3"""
    raise ErrorRegistro('Listar partidas corresponde a la entrega 3.')
