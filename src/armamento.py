def validacion_cordenadas(tablero, punto):
    try:
        if len(punto) != 3:
            return "no ejecutado"

        z, x, y = punto

        # Verificar que las coordenadas sean enteros
        if not all(type(valor) is int for valor in punto):
            return "no ejecutado"

        # Verificar los límites del tablero
        if z < 0 or z >= len(tablero):
            return "no ejecutado"

        if x < 0 or x >= len(tablero[z]):
            return "no ejecutado"

        if y < 0 or y >= len(tablero[z][x]):
            return "no ejecutado"

        # Verificar si la celda está disponible
        if tablero[z][x][y] != "~":
            return "no ejecutado"

        return "ejecutado"

    except (TypeError, ValueError, IndexError):
        return "no ejecutado"

def ataque_cordenadas(tablero, punto, informacion):
    z, x, y = punto

    if z < 0 or z >= len(tablero):
        return {
            "punto": punto,
            "resultado": "invalida"
        }

    if x < 0 or x >= len(tablero[z]):
        return {
            "punto": punto,
            "resultado": "invalida"
        }

    if y < 0 or y >= len(tablero[z][x]):
        return {
            "punto": punto,
            "resultado": "invalida"
        }

    if tablero[z][x][y] == "X" or tablero[z][x][y] == "0":
        return {
            "punto": punto,
            "resultado": "invalida"
        }

    if informacion[z][x][y] == "#":

        tablero[z][x][y] = "X"

        return {
            "punto": punto,
            "resultado": "X"
        }

    tablero[z][x][y] = "0"

    return {
        "punto": punto,
        "resultado": "0"
    }

def celdas_torpedo(tablero, punto, informacion):
    estado = validacion_cordenadas(tablero, punto)
    resultados = ataque_cordenadas(tablero, punto, informacion)
    resultadoFinal = crear_resultado_arma("T", punto, estado, resultados)
    return resultadoFinal


def celdas_misilracimo(tablero, punto, informacion):
    z, x, y = punto

    estado = validacion_cordenadas(tablero, punto)

    celdas = [
        (z, x, y),       # Centro
        (z + 1, x, y),   # Arriba / profundidad +
        (z - 1, x, y),   # Abajo / profundidad -
        (z, x + 1, y),   # X +
        (z, x - 1, y),   # X -
        (z, x, y + 1),   # Y +
        (z, x, y - 1)    # Y -
    ]

    resultados = []

    for celda in celdas:
        resultado = ataque_cordenadas(tablero, celda, informacion)
        resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("R", punto, estado, resultados)

    return resultadoFinal


def celdas_cargaprofundidad(tablero, punto, informacion):
    _, x, y = punto
    estado = validacion_cordenadas(tablero, punto)
    resultados = []

    for z in range(len(tablero)):
        celda = (z, x, y)
        resultado = ataque_cordenadas(tablero, celda, informacion)
        resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("C", punto, estado, resultados)
    return resultadoFinal

def celdas_barridolaser(tablero, punto, informacion, eje):
    z, x, y = punto
    estado = validacion_cordenadas(tablero, punto)
    resultados = []

    if eje == "Y":
        for i in range(len(tablero)):
                celda = (z, x, i)
                resultado = ataque_cordenadas(tablero, celda, informacion)
                resultados.append(resultado)
    elif eje == "X":
        for j in range(len(tablero)):
                celda = (z, j, y)
                resultado = ataque_cordenadas(tablero, celda, informacion)
                resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("L", punto, estado, resultados)
    return resultadoFinal

def crear_resultado_arma(codigo_arma, punto, estado, celdas):

    if celdas is None:
        celdas = []

    return {
        "codigo_arma": codigo_arma,
        "punto_origen": punto,
        "estado": estado,
        "consumo_municion": 1 if estado == "ejecutado" else 0,
        "celdas": celdas
    }


CATALOGO_ARMAS = {
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
        'nombre': 'Barrido Láser',
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

def catalogo(tablero, informacion):

    print("""
====== CATALOGO ======

T - TORPEDO
R - MISIL DE RACIMO
C - CARGA DE PROFUNDIDAD
S - SONAR
L - BARRIDO LASER
O - ONDA EXPANSIVA
G - TORPEDO GUIADO
""")

def selec_catalogo(opcion, punto, tablero, informacion):

    opcion = opcion.upper()

    match opcion:

        case "T":
            resultado = celdas_torpedo(tablero, punto, informacion)

        case "R":
            resultado = celdas_misilracimo(tablero, punto, informacion)

        case "C":
            resultado = celdas_cargaprofundidad(tablero, punto, informacion)

        case "S":
            print("Proxima Actualizacion") #SONAR IMPORTAR DE RADAR 

        case "L":
            eje = input("INGRESE EL EJE QUE QUIERE ELIMINAR: (INGRESE (Y) O (X))")
            eje = eje.upper
            while eje != "Y" or eje != "X":
                print("ERROR - EJE INVALIDO")
                eje = input("INGRESE EL EJE QUE QUIERE ELIMINAR: (INGRESE (Y) O (X))")
                eje = eje.upper
            resultado = celdas_barridolaser(tablero, punto, informacion, eje)

        case "O":
            print("Proxima Actualizacion")

        case "G":
            print("Proxima Actualizacion")
        
        case _:
            return {
                "punto": punto,
                "resultado": "invalida",
                "arma": opcion
            }

    return resultado