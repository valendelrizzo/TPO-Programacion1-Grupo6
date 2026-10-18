import re
import tablero
import flota
import radar

# ==============================================================================
# 1. EXCEPCIONES PROPIAS DEL DOMINIO DE PARTIDA
# ==============================================================================

class ErrorPartida(Exception):
    """Clase base para errores en el módulo de partida."""
    pass


class OpcionInvalidaError(ErrorPartida):
    """Lanzada cuando se ingresa una opción inexistente en los menús."""
    pass


class TurnoInvalidoError(ErrorPartida):
    """Lanzada cuando una jugada o acción de turno no puede llevarse a cabo."""
    pass


# ==============================================================================
# 2. DEFINICIÓN DE ESTRUCTURA DEL JUGADOR Y LA PARTIDA
# ==============================================================================

def crear_estructura_jugador(nombre, tipo, tamano_cubo):
    """
    Crea y devuelve la estructura de datos correspondiente a un jugador.
    
    Cada jugador tiene:
    - nombre: nombre para mostrar en pantalla ('Jugador 1', 'Jugador 2', 'Máquina').
    - tipo: 'humano' o 'maquina'.
    - tablero_propio: Matriz donde ubica sus naves ('o' para agua, letra para nave).
    - tablero_atacado: Matriz donde ve los disparos realizados al rival ('~' sin explorar).
    - flota: Lista de diccionarios con cada nave ubicada, sus celdas e impactos.

    """
    return {
        "nombre": nombre,
        "tipo": tipo,
        "tablero_propio": tablero.crear_tablero(tamano_cubo, 'o'),
        "tablero_atacado": tablero.crear_tablero(tamano_cubo, '~'),
        "flota": [],
        "municion": {
            "T": 999,   # Torpedo: munición ilimitada
            "R": 3,     # Misil de racimo
            "C": 2,     # Carga de profundidad
            "S": 4,     # Sonar
            "L": 2,     # Barrido láser
            "O": 1,     # Onda expansiva
            "G": 1      # Torpedo guiado
        }
    }


def nueva_partida_1v1(configuracion):
    """
    Crea y devuelve el estado inicial de una partida de dos jugadores humanos.

    """
    tamano = configuracion.get("tamano", configuracion.get("tamaño", 8))

    jugador1 = crear_estructura_jugador("Jugador 1", "humano", tamano)
    jugador2 = crear_estructura_jugador("Jugador 2", "humano", tamano)

    partida = {
        "tipo_partida": "1v1",
        "tamano_cubo": tamano,
        "turno_actual": "jugador1",
        "numero_turno": 1,
        "ganador": None,
        "dificultad": None,
        "jugador1": jugador1,
        "jugador2": jugador2,
        "historial": [],

        # Claves de compatibilidad directa con versiones previas
        "tableroPropio1": jugador1["tablero_propio"],
        "tableroAtacado1": jugador1["tablero_atacado"],
        "tableroPropio2": jugador2["tablero_propio"],
        "tableroAtacado2": jugador2["tablero_atacado"]
    }
    return partida


def nueva_partida_vs_maquina(configuracion, dificultad="facil"):
    """
    Crea y devuelve el estado inicial de una partida contra la máquina.

    """
    tamano = configuracion.get("tamano", configuracion.get("tamaño", 8))

    jugador1 = crear_estructura_jugador("Jugador 1", "humano", tamano)
    jugador2 = crear_estructura_jugador("Máquina", "maquina", tamano)

    partida = {
        "tipo_partida": "vs_maquina",
        "tamano_cubo": tamano,
        "turno_actual": "jugador1",
        "numero_turno": 1,
        "ganador": None,
        "dificultad": dificultad,
        "jugador1": jugador1,
        "jugador2": jugador2,
        "historial": [],

        "tableroPropio1": jugador1["tablero_propio"],
        "tableroAtacado1": jugador1["tablero_atacado"],
        "tableroPropio2": jugador2["tablero_propio"],
        "tableroAtacado2": jugador2["tablero_atacado"]
    }
    return partida


def nueva_partida_maquina_vs_maquina(configuracion, dificultades=("facil", "facil")):
    """
    Crea y devuelve el estado inicial de una partida entre dos máquinas.

    """
    tamano = configuracion.get("tamano", configuracion.get("tamaño", 8))

    dif1 = dificultades[0] if isinstance(dificultades, (list, tuple)) and len(dificultades) > 0 else "facil"
    dif2 = dificultades[1] if isinstance(dificultades, (list, tuple)) and len(dificultades) > 1 else "facil"

    jugador1 = crear_estructura_jugador("Máquina 1", "maquina", tamano)
    jugador2 = crear_estructura_jugador("Máquina 2", "maquina", tamano)

    partida = {
        "tipo_partida": "maquina_vs_maquina",
        "tamano_cubo": tamano,
        "turno_actual": "jugador1",
        "numero_turno": 1,
        "ganador": None,
        "dificultad": (dif1, dif2),
        "jugador1": jugador1,
        "jugador2": jugador2,
        "historial": [],

        "tableroPropio1": jugador1["tablero_propio"],
        "tableroAtacado1": jugador1["tablero_atacado"],
        "tableroPropio2": jugador2["tablero_propio"],
        "tableroAtacado2": jugador2["tablero_atacado"]
    }
    return partida


# ==============================================================================
# 3. FUNCIONES AUXILIARES DE GESTIÓN DE TURNOS Y JUGADORES
# ==============================================================================

def obtener_jugador_actual(estado):
    """
    Devuelve la estructura del jugador a quien le corresponde realizar la jugada actual.

    """
    clave = estado["turno_actual"]  # 'jugador1' o 'jugador2'
    return estado[clave]


def obtener_jugador_rival(estado):
    """
    Devuelve la estructura del jugador rival (el que defiende en este turno).

    """
    if estado["turno_actual"] == "jugador1":
        return estado["jugador2"]
    else:
        return estado["jugador1"]


def cambiar_turno(estado):
    """
    Alterna el turno entre jugador1 y jugador2 e incrementa el contador de turnos.

    """
    if estado["turno_actual"] == "jugador1":
        estado["turno_actual"] = "jugador2"
    else:
        estado["turno_actual"] = "jugador1"
        estado["numero_turno"] = estado["numero_turno"] + 1


# ==============================================================================
# 4. FUNCIONES PÚBLICAS REQUERIDAS (SECCIÓN 10)
# ==============================================================================

def hay_ganador(estado):
    """
    Verifica si alguno de los dos jugadores ha ganado la partida (si hundió toda la flota rival).

    """
    flota_j1 = estado["jugador1"]["flota"]
    flota_j2 = estado["jugador2"]["flota"]

    # Si la flota del jugador 2 está completamente destruida, gana el jugador 1
    if len(flota_j2) > 0 and flota.toda_la_flota_hundida(flota_j2):
        estado["ganador"] = "jugador1"
        return "jugador1"

    # Si la flota del jugador 1 está completamente destruida, gana el jugador 2
    if len(flota_j1) > 0 and flota.toda_la_flota_hundida(flota_j1):
        estado["ganador"] = "jugador2"
        return "jugador2"

    return None


def ejecutar_turno(estado, jugada):
    """
    Ejecuta el turno del jugador actual según la jugada especificada.
    
    """
    atacante = obtener_jugador_actual(estado)
    defensor = obtener_jugador_rival(estado)

    arma = jugada.get("arma", "T")
    objetivo = jugada.get("objetivo")

    if not objetivo:
        raise TurnoInvalidoError("La jugada debe incluir un objetivo de disparo.")

    # 1. Validar y descontar munición del arma
    municion_disponible = atacante["municion"].get(arma, 0)
    if municion_disponible <= 0:
        raise TurnoInvalidoError(f"No queda munición disponible para el arma '{arma}'.")

    # El torpedo 'T' tiene munición infinita, el resto descuenta 1
    if arma != "T":
        atacante["municion"][arma] = atacante["municion"][arma] - 1

    # 2. Registrar el impacto sobre la flota rival
    resultado_impacto = flota.registrar_impacto(defensor["flota"], objetivo)

    # 3. Actualizar el tablero atacado del atacante con el símbolo reglamentario
    z, x, y = flota.parsear_punto(objetivo)
    if resultado_impacto["resultado"] == "agua":
        atacante["tablero_atacado"][z - 1][x - 1][y - 1] = "o"
    else:
        atacante["tablero_atacado"][z - 1][x - 1][y - 1] = "X"

    # 4. Guardar registro en el historial de la partida
    registro_jugada = {
        "turno": estado["numero_turno"],
        "jugador": atacante["nombre"],
        "arma": arma,
        "objetivo": (z, x, y),
        "resultado": resultado_impacto["resultado"],
        "mensaje": resultado_impacto["mensaje"]
    }
    estado["historial"].append(registro_jugada)

    # 5. Revisar si con esta jugada hubo un ganador
    ganador = hay_ganador(estado)
    if not ganador:
        # Alternar el turno al rival
        cambiar_turno(estado)

    return estado


def turno_maquina(estado):
    """
    Ejecuta automáticamente el turno de la máquina eligiendo una celda no atacada.

    """
    import random
    atacante = obtener_jugador_actual(estado)
    tamano = estado["tamano_cubo"]

    # Buscar celdas donde la máquina todavía no haya disparado ('~')
    celdas_disponibles = []
    for z in range(1, tamano + 1):
        for x in range(1, tamano + 1):
            for y in range(1, tamano + 1):
                if atacante["tablero_atacado"][z - 1][x - 1][y - 1] == '~':
                    celdas_disponibles.append((z, x, y))

    if not celdas_disponibles:
        raise TurnoInvalidoError("No quedan celdas sin explorar para la máquina.")

    objetivo_elegido = random.choice(celdas_disponibles)
    jugada = {
        "arma": "T",
        "objetivo": objetivo_elegido
    }
    return ejecutar_turno(estado, jugada)


# ==============================================================================
# 5. MENÚ PRINCIPAL E INICIO DE LA APLICACIÓN
# ==============================================================================

configuracionG = {
    "tamaño": 8,
}

def main():
    """Bucle principal de opciones para el menú de consola."""
    entrada = -1
    while entrada < 1 or entrada > 5:
        print("===== OPERACION CUBO =====")
        print("1 - Partida uno contra uno")
        print("2 - Partida uno contra la maquina")
        print("3 - Partida maquina contra maquina")
        print("4 - Continuar una partida guardada")
        print("5 - Salir")
        print()

        try:
            texto_ingresado = input("Opción: ").strip()
            # Validación con expresión regular según condiciones técnicas
            if not re.match(r'^[1-5]$', texto_ingresado):
                print("Opción inválida. Ingrese un número entre 1 y 5.\n")
                continue
            entrada = int(texto_ingresado)
            print()
        except ValueError:
            print("Por favor, ingrese un número válido.\n")
            entrada = -1

    if entrada == 1:
        estado_partida = nueva_partida_1v1(configuracionG)
    elif entrada == 2:
        estado_partida = nueva_partida_vs_maquina(configuracionG)
    elif entrada == 3:
        estado_partida = nueva_partida_maquina_vs_maquina(configuracionG)
    elif entrada == 4:
        # TODO: Continuar partida guardada
        return 1
    elif entrada == 5:
        print("Saliendo del juego...")
        return 0

    print(f"Partida '{estado_partida['tipo_partida']}' creada exitosamente.")
    print(f"Turno inicial: {estado_partida['jugador1']['nombre']}")
    return 1


if __name__ == "__main__":
    while main():
        pass

#Dejar esto en funcion partida
def ejecucion_radar(tablero_atacado, tablero_propio2, pos): 
    print(menu_radares())
    ingreso = int(input("tipo de radar? (Ingrese indice)"))
    
    match ingreso: 
        case 1: 
            tablero_atacado = radar.buscar_nave_lineal(tablero_atacado, tablero_propio2, pos)
        ##case 2:
          ##  tablero_atacado = buscar_nave_optimizado(tablero_atacado, tablero_propio2, pos)

    return tablero_atacado

def menu_radares():
    return """
1- Busqueda lineal
"""