import os
import json
import re

import tablero

RUTA = os.path.join(os.path.dirname(__file__), "../datos/datosGlobales.json")
fileState = []
fileStateLoaded = False

gPartidaActual = {}


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


def obtener_ultimo_impacto_activo(estado, nombre_jugador, tablero_rival):
    """Recorre el historial de atras hacia adelante y devuelve el ultimo punto impactado cuya nave no este hundida."""
    for jugada in reversed(estado.get('historial', [])):
        if jugada.get('jugador') == nombre_jugador:
            for celda in reversed(jugada.get('celdas', [])):
                punto = celda.get('punto')
                # Verificamos que haya sido impacto y que en el tablero actual siga como IMPACTO (no HUNDIDO)
                if celda.get('resultado') == tablero.IMPACTO and tablero.leer_celda(tablero_rival, punto) == tablero.IMPACTO:
                    return punto
    return None


def resumen_partida(estado):
    """Devuelve el ganador y las estadisticas finales del estado recibido, sin modificarlo"""
    return {'ganador': estado['ganador'], 'jugadores': estadisticas(estado)}


def _escribir_archivo_global():
    """Escribe el estado actual de fileState en el archivo JSON global creando la carpeta si falta."""
    os.makedirs(os.path.dirname(RUTA), exist_ok=True)
    with open(RUTA, "w", encoding="utf-8") as archivo:
        json.dump(fileState, archivo, ensure_ascii=True, separators=(',', ':'))


def cargarEstadoGlobal():
    """Carga la lista de partidas desde el archivo JSON global o lo inicializa vacio si no existe."""
    global fileStateLoaded
    global fileState
    try:
        os.makedirs(os.path.dirname(RUTA), exist_ok=True)
        with open(RUTA, "a+", encoding="utf-8") as archivo:
            archivo.seek(0)
            contenido = archivo.read().strip()
            if not contenido:
                fileState = []
                _escribir_archivo_global()
            else:
                fileState = json.loads(contenido)
    except json.JSONDecodeError:
        print("Error leyendo la informacion global, creando una nueva.")
        guardar_partida(None, None)
    except OSError as error:
        raise ErrorRegistro(f"Error de sistema operativo al leer el archivo: {error}")
    fileStateLoaded = True


def guardar_partida(estado, nombre=None):
    """
    Guarda el estado recibido con su nombre en el archivo JSON global.
    Si recibe None inicializa el archivo con una lista vacia.
    Soporta tanto (estado, nombre) como (nombre, estado).
    """
    global fileState
    global fileStateLoaded
    if estado is None and nombre is None:
        fileState = []
        _escribir_archivo_global()
        fileStateLoaded = True
        return RUTA

    if isinstance(estado, str) and isinstance(nombre, dict):
        estado, nombre = nombre, estado

    if not fileStateLoaded:
        cargarEstadoGlobal()

    if not isinstance(nombre, str) or not nombre.strip():
        raise ErrorRegistro('El nombre de la partida no puede estar vacio.')
    if not isinstance(estado, dict):
        raise ErrorRegistro('El estado de la partida debe ser un diccionario.')

    nombre_limpio = nombre.strip()
    partida_nueva = {"nombre": nombre_limpio, "partida": estado}
    fileState.append(partida_nueva)
    _escribir_archivo_global()
    return RUTA


def listar_partidas():
    """Devuelve la lista numerada de nombres de las partidas guardadas."""
    global fileStateLoaded
    global fileState
    if not fileStateLoaded:
        cargarEstadoGlobal()
    return [f"{i}-{d['nombre']}" for i, d in enumerate(fileState, start=1)]


def cargar_partida(nombre):
    """
    Recibe el nombre o indice (desde 1) de una partida guardada, la extrae del registro
    actualizando el archivo JSON y devuelve su estado. Lanza ErrorRegistro si no existe.
    """
    global fileStateLoaded
    global fileState
    if not fileStateLoaded:
        cargarEstadoGlobal()

    indice_encontrado = None
    if isinstance(nombre, int):
        if 1 <= nombre <= len(fileState):
            indice_encontrado = nombre - 1
    elif isinstance(nombre, str):
        texto = nombre.strip()
        for i, entrada in enumerate(fileState):
            etiqueta = f"{i + 1}-{entrada['nombre']}"
            if entrada['nombre'] == texto or etiqueta == texto:
                indice_encontrado = i
                break
        if indice_encontrado is None and texto.isdigit():
            idx = int(texto)
            if 1 <= idx <= len(fileState):
                indice_encontrado = idx - 1

    if indice_encontrado is None:
        raise ErrorRegistro(f"No se encontro la partida '{nombre}'.")

    registro_cargado = fileState.pop(indice_encontrado)
    _escribir_archivo_global()
    return registro_cargado['partida']


def cargarPartida():
    """Interfaz de consola para listar y elegir una partida guardada a continuar."""
    nombres = listar_partidas()
    cantOpciones = len(nombres)
    texto_nombres = '\n'.join(nombres)
    if cantOpciones < 1:
        print("\nNo hay partidas para cargar.")
        return 1
    print(texto_nombres)
    cargar = 0
    while True:
        try:
            cargar = int(input("\nIngrese la partida que quiere cargar: "))
        except ValueError:
            print("La opcion debe ser un numero.")
            print(texto_nombres)
            continue
        if 1 <= cargar <= cantOpciones:
            break
        print("Opcion invalida.")
        print(texto_nombres)
    nombre_elegido = fileState[cargar - 1]['nombre']
    estado_cargado = cargar_partida(cargar)
    return {"nombre": nombre_elegido, "partida": estado_cargado}


def guardarPartida(estado):
    """Pide un nombre validado por regex y guarda el estado recibido como una partida."""
    while True:
        nombre = input("Ingrese el nombre con el que guardar la partida o CANCELAR:\n").strip()
        if nombre == "CANCELAR":
            return 0
        if not re.fullmatch(r'[A-Za-z0-9 _-]+', nombre):
            print("Nombre invalido. Use solo letras, numeros, espacios, guiones o guion bajo.")
            continue
        guardar_partida(estado, nombre)
        print(f"Partida '{nombre}' guardada correctamente.")
        return 'guardada'
