from radar import sonar_por_planos

# ================= CATALOGO Y MUNICION =================

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


def crear_municion_jugador():
    municion = {}
    for codigo in CATALOGO_ARMAS:
        municion[codigo] = CATALOGO_ARMAS[codigo]["municion_inicial"]
    return municion


# Diccionario general para administrar la munición de ambos jugadores
MUNICION_JUGADORES = {
    1: crear_municion_jugador(),
    2: crear_municion_jugador()
}


def tiene_municion(codigo_arma, municion_jugador):
    if codigo_arma not in municion_jugador:
        return False

    cantidad = municion_jugador[codigo_arma]

    # None significa munición ilimitada (Torpedo)
    if cantidad == None:
        return True

    return cantidad > 0


def descontar_municion(codigo_arma, municion_jugador, consumo):
    # Si no es ilimitada, le restamos el consumo (que vale 1 o 0)
    if municion_jugador[codigo_arma] != None:
        municion_jugador[codigo_arma] = municion_jugador[codigo_arma] - consumo

    return municion_jugador[codigo_arma]


# ================= VALIDACIONES Y ATAQUE BASE =================

def en_rango(tablero, punto):
    # 1. Verificar que tenga 3 coordenadas
    if len(punto) != 3:
        return False

    # 2. Verificar que las 3 sean números enteros
    for valor in punto:
        if type(valor) != int:
            return False

    z, x, y = punto

    # 3. Verificar que no se salga de los límites del tablero
    if z < 0 or z >= len(tablero):
        return False

    if x < 0 or x >= len(tablero[z]):
        return False

    return not (y < 0 or y >= len(tablero[z][x]))


def validacion_cordenadas(tablero, punto):
    if not en_rango(tablero, punto):
        return "no ejecutado"

    z, x, y = punto
    celda = tablero[z][x][y]

    # Es válido disparar si hay agua ("~" o " ") o si fue marcada por el Sonar ("?")
    if celda != "~" and celda != "?" and celda != " ":
        return "no ejecutado"

    return "ejecutado"


def ataque_cordenadas(tablero, punto, informacion):
    if not en_rango(tablero, punto):
        return {
            "punto": punto,
            "resultado": "invalida"
        }

    z, x, y = punto
    celda_atacada = tablero[z][x][y]
    celda_rival = informacion[z][x][y]

    # 1. Si ya fue atacada antes ("X" impacto o "o" agua), no se vuelve a atacar
    if celda_atacada == "X" or celda_atacada == "o":
        return {
            "punto": punto,
            "resultado": "invalida"
        }

    # 2. Si hay una nave presente (mismo criterio que radar.py)
    if celda_rival != "~" and celda_rival != "o" and celda_rival != " ":
        tablero[z][x][y] = "X"
        return {
            "punto": punto,
            "resultado": "X"
        }

    # 3. Disparo al agua: se marca con "o" minúscula
    tablero[z][x][y] = "o"
    return {
        "punto": punto,
        "resultado": "o"
    }


def crear_resultado_arma(codigo_arma, punto, estado, celdas, municion_restante=None, motivo="ok"):
    if celdas is None:
        celdas = []

    # Separamos las coordenadas según lo que pasó en cada una
    impactos = []
    agua = []
    invalidas = []

    for item in celdas:
        if item["resultado"] == "X":
            impactos.append(item["punto"])
        elif item["resultado"] == "o":
            agua.append(item["punto"])
        else:
            invalidas.append(item["punto"])

    if estado == "ejecutado":
        consumo = 1
        exito = True
    else:
        consumo = 0
        exito = False
        if motivo == "ok":
            motivo = "coordenada invalida"

    return {
        "codigo_arma": codigo_arma,
        "punto_origen": punto,
        "estado": estado,
        "exito": exito,
        "motivo": motivo,
        "consumo_municion": consumo,
        "municion_restante": municion_restante,
        "celdas": celdas,
        "impactos": impactos,
        "agua": agua,
        "invalidas": invalidas,
        "cantidad_impactos": len(impactos)
    }


# ================= FUNCIONES DE ARMAS =================

def celdas_torpedo(tablero, punto, informacion):
    estado = validacion_cordenadas(tablero, punto)
    resultados = []

    if estado == "ejecutado":
        resultado = ataque_cordenadas(tablero, punto, informacion)
        resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("T", punto, estado, resultados)
    return resultadoFinal


def celdas_misilracimo(tablero, punto, informacion):
    estado = validacion_cordenadas(tablero, punto)
    resultados = []

    if estado == "ejecutado":
        z, x, y = punto
        celdas = [
            (z, x, y),      # Centro
            (z + 1, x, y),  # Arriba / profundidad +
            (z - 1, x, y),  # Abajo / profundidad -
            (z, x + 1, y),  # X +
            (z, x - 1, y),  # X -
            (z, x, y + 1),  # Y +
            (z, x, y - 1)   # Y -
        ]

        for celda in celdas:
            resultado = ataque_cordenadas(tablero, celda, informacion)
            resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("R", punto, estado, resultados)
    return resultadoFinal


def celdas_cargaprofundidad(tablero, punto, informacion):
    estado = validacion_cordenadas(tablero, punto)
    resultados = []

    if estado == "ejecutado":
        _, x, y = punto
        for z in range(len(tablero)):
            celda = (z, x, y)
            resultado = ataque_cordenadas(tablero, celda, informacion)
            resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("C", punto, estado, resultados)
    return resultadoFinal


def celdas_barridolaser(tablero, punto, informacion, eje):
    estado = validacion_cordenadas(tablero, punto)
    resultados = []

    if estado == "ejecutado":
        z, x, y = punto

        if eje == "Y":
            for i in range(len(tablero[z][x])):
                celda = (z, x, i)
                resultado = ataque_cordenadas(tablero, celda, informacion)
                resultados.append(resultado)

        elif eje == "X":
            for j in range(len(tablero[z])):
                celda = (z, j, y)
                resultado = ataque_cordenadas(tablero, celda, informacion)
                resultados.append(resultado)

    resultadoFinal = crear_resultado_arma("L", punto, estado, resultados)
    return resultadoFinal


def ejecutar_sonar(tablero, informacion, eje, indice, municion_jugador):
    # 1. Validar que el índice del plano exista en el cubo
    if indice < 0 or indice >= len(tablero):
        print("ERROR - INDICE FUERA DEL TABLERO")
        return None

    # 2. Llamar a la función de radar.py (tablero = tablero_atacado, informacion = matriz_rival)
    contactos, tablero = sonar_por_planos(tablero, informacion, eje, indice)

    # 3. Descontar 1 de munición al Sonar ("S")
    descontar_municion("S", municion_jugador, 1)

    print(f"Sonar ejecutado en {eje} = {indice}. Contactos detectados: {contactos}")

    # Devuelve None porque no produce daño ni envía paquete de ataque a registro.py
    return None


# ================= MENU Y SELECCION =================

def catalogo(municion_jugador=None):
    print("\n====== CATALOGO ======")
    for codigo in CATALOGO_ARMAS:
        nombre = CATALOGO_ARMAS[codigo]["nombre"].upper()

        if municion_jugador != None and codigo in municion_jugador:
            balas = municion_jugador[codigo]
            if balas == None:
                texto_balas = " (ILIMITADA)"
            else:
                texto_balas = f" ({balas} disponibles)"
        else:
            texto_balas = ""

        print(f"{codigo} - {nombre}{texto_balas}")
    print("======================\n")


def selec_catalogo(opcion, punto, tablero, informacion, municion_jugador):
    opcion = opcion.strip().upper()

    # 1. Validar que el arma exista en el catálogo
    if opcion not in CATALOGO_ARMAS:
        return crear_resultado_arma(opcion, punto, "no ejecutado", [], None, "arma inexistente")

    # 2. Validar que el jugador tenga munición disponible
    if not tiene_municion(opcion, municion_jugador):
        balas_actuales = municion_jugador[opcion]
        return crear_resultado_arma(opcion, punto, "no ejecutado", [], balas_actuales, "sin municion")

    # 3. Ejecutar el arma elegida
    match opcion:
        case "T":
            resultado = celdas_torpedo(tablero, punto, informacion)

        case "R":
            resultado = celdas_misilracimo(tablero, punto, informacion)

        case "C":
            resultado = celdas_cargaprofundidad(tablero, punto, informacion)

        case "S":
            eje = input("INGRESE EL EJE A ESCANEAR (Z, X o Y): ").strip().upper()
            while eje not in ("Z", "X", "Y"):
                print("ERROR - EJE INVALIDO")
                eje = input("INGRESE EL EJE A ESCANEAR (Z, X o Y): ").strip().upper()

            indice = int(input(f"INGRESE EL VALOR DEL PLANO {eje}: "))

            # Ejecuta el sonar, descuenta la bala y corta acá con return
            return ejecutar_sonar(tablero, informacion, eje, indice, municion_jugador)

        case "L":
            eje = input("INGRESE EL EJE QUE QUIERE ELIMINAR (Y o X): ").strip().upper()
            while eje not in ("Y", "X"):
                print("ERROR - EJE INVALIDO")
                eje = input("INGRESE EL EJE QUE QUIERE ELIMINAR (Y o X): ").strip().upper()
            resultado = celdas_barridolaser(tablero, punto, informacion, eje)

        case "O":
            print("Proxima Actualizacion")
            resultado = crear_resultado_arma("O", punto, "no ejecutado", [], municion_jugador["O"], "no disponible")

        case "G":
            print("Proxima Actualizacion")
            resultado = crear_resultado_arma("G", punto, "no ejecutado", [], municion_jugador["G"], "no disponible")

    # 4. Descontar munición para las armas de ataque (resta 1 si fue "ejecutado", o 0 si falló)
    consumo = resultado["consumo_municion"]
    restantes = descontar_municion(opcion, municion_jugador, consumo)

    # 5. Guardar cuántas balas quedaron en el diccionario final para registro.py
    resultado["municion_restante"] = restantes

    return resultado