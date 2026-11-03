import random
import re
import tablero


CATALOGO_NAVES = {
    'F': {
        'nombre': 'Fragata',
        'tamano': 2,
        'cantidad': 3,
        'forma': 'lineal',
        'regla': 'sin_restriccion',
        'descripcion': '2 celdas contiguas en linea recta. Sin restriccion de altura.'
    },
    'D': {
        'nombre': 'Destructor',
        'tamano': 3,
        'cantidad': 2,
        'forma': 'lineal',
        'regla': 'sin_restriccion',
        'descripcion': '3 celdas contiguas en linea recta. Sin restriccion de altura.'
    },
    'S': {
        'nombre': 'Submarino',
        'tamano': 3,
        'cantidad': 2,
        'forma': 'lineal',
        'regla': 'mitad_inferior_z',
        'descripcion': '3 celdas contiguas en linea recta. Solo en la mitad inferior de z.'
    },
    'C': {
        'nombre': 'Crucero',
        'tamano': 4,
        'cantidad': 1,
        'forma': 'lineal',
        'regla': 'no_bordes_z',
        'descripcion': '4 celdas contiguas en linea recta. No puede ocupar z = 1 ni z = N.'
    },
    'P': {
        'nombre': 'Portaaviones',
        'tamano': 5,
        'cantidad': 1,
        'forma': 'lineal',
        'regla': 'mitad_superior_z',
        'descripcion': '5 celdas contiguas en linea recta. Solo en la mitad superior de z.'
    },
    'E': {
        'nombre': 'Estacion orbital',
        'tamano': 8,
        'dimensiones': (2, 2, 2),
        'cantidad': 1,
        'forma': 'bloque',
        'regla': 'no_caras_exteriores',
        'descripcion': 'Bloque de 2x2x2 celdas. No puede tocar ninguna cara exterior del cubo.'
    }
}

class UbicacionInvalidaError(tablero.ErrorJuego):
    """Excepcion lanzada cuando una nave no cumple las reglas de colocacion"""
    pass

def validar_reglas_ubicacion(cubo, tipo_nave, celdas):
    """
    Verifica que la nave cumpla con todas las restricciones:
    1. Que ninguna celda quede fuera de los limites del cubo (1 a N).
    2. Que cumpla con la restriccion de altura o posicion propia de su tipo.
    3. Que no choque con otra nave ni este pegada (al menos 1 celda libre en todas direcciones).
    """
    tamano_cubo = len(cubo) 
    datos_nave = CATALOGO_NAVES[tipo_nave]
    regla = datos_nave['regla']
    nombre_nave = datos_nave['nombre']

    # =========================================================================
    # PARTE 1: Validar limites del cubo y reglas de altura/caras por celda
    # =========================================================================
    for celda in celdas:
        z = celda[0]
        x = celda[1]
        y = celda[2]

        if tablero.validar_punto(cubo, celda):
            if tablero.leer_celda(cubo, celda) not in (tablero.AGUA_SIN_EXPLORAR, tablero.AGUA_MARCADA, 0, ' '):
                raise UbicacionInvalidaError('La nave se superpone con otra nave.')

        # REGLA 1: La nave no puede salirse del cubo (coordenadas entre 1 y N)
        fuera_de_z = (z < 1) or (z > tamano_cubo)
        fuera_de_x = (x < 1) or (x > tamano_cubo)
        fuera_de_y = (y < 1) or (y > tamano_cubo)

        if fuera_de_z or fuera_de_x or fuera_de_y:
            raise UbicacionInvalidaError(
                f"La celda ({z}, {x}, {y}) queda fuera del tablero (tamano {tamano_cubo}x{tamano_cubo}x{tamano_cubo})."
            )

        # REGLA 2A: Submarino -> Solo en la mitad inferior de z (ej: en N=8, z <= 4)
        if regla == 'mitad_inferior_z':
            limite_inferior = tamano_cubo // 2
            if z > limite_inferior:
                raise UbicacionInvalidaError(
                    f"El {nombre_nave} solo puede ubicarse en la mitad inferior (z <= {limite_inferior}). "
                    f"La coordenada z={z} no esta permitida."
                )

        # REGLA 2B: Portaaviones -> Solo en la mitad superior de z (ej: en N=8, z >= 5)
        if regla == 'mitad_superior_z':
            limite_superior = (tamano_cubo // 2) + 1
            if z < limite_superior:
                raise UbicacionInvalidaError(
                    f"El {nombre_nave} solo puede ubicarse en la mitad superior (z >= {limite_superior}). "
                    f"La coordenada z={z} no esta permitida."
                )

        # REGLA 2C: Crucero -> No puede ocupar los bordes z = 1 ni z = N
        if regla == 'no_bordes_z':
            if z == 1 or z == tamano_cubo:
                raise UbicacionInvalidaError(
                    f"El {nombre_nave} no puede tocar los bordes z=1 ni z={tamano_cubo}. "
                    f"La coordenada z={z} no esta permitida."
                )

        # REGLA 2D: Estacion orbital -> No puede tocar ninguna de las 6 caras exteriores del cubo
        if regla == 'no_caras_exteriores':
            toca_cara_z = (z == 1 or z == tamano_cubo)
            toca_cara_x = (x == 1 or x == tamano_cubo)
            toca_cara_y = (y == 1 or y == tamano_cubo)

            if toca_cara_z or toca_cara_x or toca_cara_y:
                raise UbicacionInvalidaError(
                    f"La {nombre_nave} no puede tocar las caras exteriores del cubo. "
                    f"La celda ({z}, {x}, {y}) toca un borde exterior."
                )

    # =========================================================================
    # PARTE 2: Validar superposicion y separacion (al menos 1 celda libre alrededor)
    # =========================================================================
    # lista de celdas a un conjunto para busquedas rapidas
    conjunto_celdas_propias = set(celdas)

    # Los desplazamientos posibles respecto a una celda: -1 (atras), 0 (mismo lugar), +1 (adelante)
    desplazamientos = [-1, 0, 1]

    for celda in celdas:
        z_actual = celda[0]
        x_actual = celda[1]
        y_actual = celda[2]

        for dz in desplazamientos:
            for dx in desplazamientos:
                for dy in desplazamientos:
                    vecino_z = z_actual + dz
                    vecino_x = x_actual + dx
                    vecino_y = y_actual + dy

                    vecino_dentro = (1 <= vecino_z <= tamano_cubo and 
                                     1 <= vecino_x <= tamano_cubo and 
                                     1 <= vecino_y <= tamano_cubo)

                    if vecino_dentro:
                        coordenada_vecina = (vecino_z, vecino_x, vecino_y)

                        if coordenada_vecina not in conjunto_celdas_propias:
                            
                            contenido = cubo[vecino_z - 1][vecino_x - 1][vecino_y - 1]

                            if contenido not in ('~', 'o', 0, ' '):
                                raise UbicacionInvalidaError(
                                    f"No se puede ubicar la nave aca: la posicion ({vecino_z}, {vecino_x}, {vecino_y}) "
                                    f"ya esta ocupada por otra nave o esta a menos de una celda de distancia."
                                )

    # Si paso todas las pruebas sin lanzar excepciones, la ubicacion es valida
    return True

def parsear_punto(punto):
    """Devuelve una tupla de enteros desde texto o secuencia. Lanza UbicacionInvalidaError"""
    if isinstance(punto, str):
        patron = r'\s*([0-9]+)\s*,\s*([0-9]+)\s*,\s*([0-9]+)\s*'
        coincidencia = re.fullmatch(patron, punto)
        if coincidencia:
            return (int(coincidencia.group(1)), int(coincidencia.group(2)),
                    int(coincidencia.group(3)))
    elif isinstance(punto, (tuple, list)) and len(punto) == 3:
        if all(type(valor) == int for valor in punto):
            return tuple(punto)
    raise UbicacionInvalidaError('El punto debe tener el formato z,x,y con enteros.')


def generar_celdas_nave(tipo_nave, p_desde, p_hasta):
    """
    Toma el tipo de nave y sus dos puntos extremos (desde y hasta).
    Verifica que la forma geometrica sea valida (linea recta o bloque 2x2x2)
    y genera la lista completa de todas las celdas (z, x, y) que ocupa la nave.
    """
    # 1. Desempaqueto las coordenadas de inicio y fin
    z_inicio, x_inicio, y_inicio = p_desde
    z_fin, x_fin, y_fin = p_hasta

    datos_nave = CATALOGO_NAVES[tipo_nave] ## Sobre los datos de la nave desempaqueto la forma y nombre.
    forma = datos_nave['forma']
    nombre = datos_nave['nombre']

    # =========================================================================
    # CASO A: Naves lineales (Fragata, Destructor, Submarino, Crucero, Portaaviones)
    # Deben colocarse en linea recta sobre un unico eje (Z, X o Y)
    # =========================================================================
    if forma == 'lineal':
        # Calculamos cuanto cambia la nave en cada eje
        diferencia_z = z_fin - z_inicio
        diferencia_x = x_fin - x_inicio
        diferencia_y = y_fin - y_inicio

        # Contamos cuantos ejes cambiaron de valor
        ejes_que_cambian = 0
        if diferencia_z != 0:
            ejes_que_cambian = ejes_que_cambian + 1
        if diferencia_x != 0:
            ejes_que_cambian = ejes_que_cambian + 1
        if diferencia_y != 0:
            ejes_que_cambian = ejes_que_cambian + 1

        # REGLA 1: No puede ir en diagonal. Solo un eje puede variar a la vez.
        if ejes_que_cambian > 1:
            raise UbicacionInvalidaError(
                f"La nave {nombre} no puede colocarse en diagonal. Debe alinearse sobre un solo eje."
            )

        # REGLA 2: No puede ser un solo punto si el tamano es mayor a 1
        if ejes_que_cambian == 0:
            raise UbicacionInvalidaError(
                f"El punto de inicio y de fin son iguales. La nave {nombre} mide mas de 1 celda."
            )

        # REGLA 3: Validar que la longitud coincida con el tamano de la nave
        # La distancia entre extremos es el valor absoluto de la diferencia, + 1 celda inicial
        longitud_ingresada = max(abs(diferencia_z), abs(diferencia_x), abs(diferencia_y)) + 1
        tamano_requerido = datos_nave['tamano']

        if longitud_ingresada != tamano_requerido:
            raise UbicacionInvalidaError(
                f"Tamano incorrecto para {nombre}. "
                f"Debe medir {tamano_requerido} celdas, pero el tramo ingresado mide {longitud_ingresada}."
            )

        # 4. Determinar el paso en cada eje
        paso_z = 0
        if z_fin > z_inicio:
            paso_z = 1
        elif z_fin < z_inicio:
            paso_z = -1

        paso_x = 0
        if x_fin > x_inicio:
            paso_x = 1
        elif x_fin < x_inicio:
            paso_x = -1

        paso_y = 0
        if y_fin > y_inicio:
            paso_y = 1
        elif y_fin < y_inicio:
            paso_y = -1

        # 5. Construir la lista de celdas paso a paso
        celdas_ocupadas = []
        actual_z = z_inicio
        actual_x = x_inicio
        actual_y = y_inicio

        for _ in range(tamano_requerido):
            celda = (actual_z, actual_x, actual_y)
            celdas_ocupadas.append(celda)

            # Avanzamos un paso en la direccion correspondiente
            actual_z = actual_z + paso_z
            actual_x = actual_x + paso_x
            actual_y = actual_y + paso_y

        return celdas_ocupadas

    # =========================================================================
    # CASO B: Estacion Orbital (forma == 'bloque')
    # Debe ser un cubo cerrado de 2x2x2 (8 celdas en total)
    # =========================================================================
    elif forma == 'bloque':
        # Identificamos el valor menor y mayor en cada dimension
        # (por si el usuario ingreso los puntos en orden inverso)
        min_z = min(z_inicio, z_fin)
        max_z = max(z_inicio, z_fin)

        min_x = min(x_inicio, x_fin)
        max_x = max(x_inicio, x_fin)

        min_y = min(y_inicio, y_fin)
        max_y = max(y_inicio, y_fin)

        # Para que sea un bloque de 2 celdas de lado, la diferencia entre max y min debe ser exactamente 1
        ancho_z_valido = (max_z - min_z == 1)
        ancho_x_valido = (max_x - min_x == 1)
        ancho_y_valido = (max_y - min_y == 1)

        if not (ancho_z_valido and ancho_x_valido and ancho_y_valido):
            raise UbicacionInvalidaError(
                "La Estacion Orbital debe abarcar exactamente un bloque de 2x2x2 celdas."
            )

        # Generamos las 8 celdas recorriendo cada eje desde el valor menor al mayor
        celdas_ocupadas = []
        for z in range(min_z, max_z + 1):
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    celda = (z, x, y)
                    celdas_ocupadas.append(celda)

        return celdas_ocupadas
    
#debe devolver "cubo y flota actualizados, o excepcion"
def ubicar_nave(cubo, flota, nave, puntoD, puntoH):
    """Ubica una nave en el tablero y actualiza la flota. Lanza UbicacionInvalidaError si falla"""

    if nave not in CATALOGO_NAVES:
        raise UbicacionInvalidaError(f"Tipo de nave '{nave}' no reconocido.")

    if flota is None:
        flota = []
    cantidad = 0
    for colocada in flota:
        if colocada['tipo'] == nave:
            cantidad += 1
    if cantidad >= CATALOGO_NAVES[nave]['cantidad']:
        raise UbicacionInvalidaError('Ya se ubicaron todas las naves de ese tipo.')

    p_desde = parsear_punto(puntoD)
    p_hasta = parsear_punto(puntoH)

    celdas = generar_celdas_nave(nave, p_desde, p_hasta)
    validar_reglas_ubicacion(cubo, nave, celdas)

    # Marcado en el tablero
    for z, x, y in celdas:
        cubo[z - 1][x - 1][y - 1] = nave

    # Registro en la flota
    flota.append({
        'tipo': nave,
        'nombre': CATALOGO_NAVES[nave]['nombre'],
        'celdas': celdas,
        'impactos': set(),
        'impactos_por_celda': {},
        'hundida': False
    })

    return cubo, flota

def ubicacion_automatica(cubo, catalogo=None, semilla=None):
    """
    Ubica de forma automatica y aleatoria toda la flota.
    
    """
    if catalogo is None:
        catalogo = CATALOGO_NAVES

    if semilla is not None:
        #si hay semilla, se crea un generador con esa semilla fija
        generador = random.Random(semilla)
    else:
        #si no hay semilla, se crea un generador con semilla aleatoria
        generador = random.Random()


    tamano_cubo = len(cubo)
    for tipo in catalogo:
        if tipo not in CATALOGO_NAVES:
            raise UbicacionInvalidaError('Tipo de nave desconocido en el catalogo.')
        if tipo == 'E' and tamano_cubo < 4:
            raise UbicacionInvalidaError('La estacion necesita un cubo de al menos 4.')
        if tipo != 'E' and catalogo[tipo]['tamano'] > tamano_cubo:
            raise UbicacionInvalidaError('El cubo es demasiado chico para esa flota.')
    cubo_original = [[[celda for celda in fila] for fila in capa] for capa in cubo]

    # Se intenta ubicar la flota completa. Si en algun intento el tablero se bloquea,
    # se reinicia el tablero y se vuelve a intentar desde cero (max 100 intentos globales)

    for intento_global in range(100):
        # 1) Limpieza del cubo para comenzar otro intento
        for z in range(tamano_cubo):
            for x in range(tamano_cubo):
                for y in range(tamano_cubo):
                    cubo[z][x][y] = tablero.AGUA_SIN_EXPLORAR

        flota_actual = []
        pudo_ubicar_todo = True

        # Se ordena las naves para colocar primero las mas grandes y restrictivas
        orden_naves = ['E', 'P', 'C', 'S', 'D', 'F']

        for tipo in orden_naves:
            if tipo not in catalogo:
                continue

            cantidad_naves = catalogo[tipo]['cantidad']

            for _ in range(cantidad_naves): ## for con la cantidad de naves que hay que ubicar de ese tipo
                nave_colocada = False
                intentos_nave = 0
                max_intentos_por_nave = 300 ## Valor arbitrario.

                while not nave_colocada and intentos_nave < max_intentos_por_nave:
                    intentos_nave = intentos_nave + 1

                    if tipo == 'E':
                        # Estacion orbital: bloque 2x2x2 que no puede tocar bordes exteriores (2 a N-1)
                        if tamano_cubo < 4:
                            break
                        z_inicio = generador.randint(2, tamano_cubo - 2)
                        x_inicio = generador.randint(2, tamano_cubo - 2)
                        y_inicio = generador.randint(2, tamano_cubo - 2)
                        p_desde = (z_inicio, x_inicio, y_inicio)
                        p_hasta = (z_inicio + 1, x_inicio + 1, y_inicio + 1)
                    else:
                        tamano_nave = catalogo[tipo]['tamano']
                        eje_elegido = generador.choice(['z', 'x', 'y'])

                        if eje_elegido == 'z':
                            # Determinar rango permitido para z segun restricciones de cada nave
                            if tipo == 'S':
                                min_z, max_z = 1, tamano_cubo // 2
                            elif tipo == 'P':
                                min_z, max_z = (tamano_cubo // 2) + 1, tamano_cubo
                            elif tipo == 'C':
                                min_z, max_z = 2, tamano_cubo - 1
                            else:
                                min_z, max_z = 1, tamano_cubo

                            if max_z - min_z + 1 < tamano_nave:
                                continue

                            z_inicio = generador.randint(min_z, max_z - tamano_nave + 1)
                            z_fin = z_inicio + tamano_nave - 1
                            x_inicio = x_fin = generador.randint(1, tamano_cubo)
                            y_inicio = y_fin = generador.randint(1, tamano_cubo)

                        elif eje_elegido == 'x':
                            # Eje X varia
                            if tipo == 'S':
                                z_inicio = z_fin = generador.randint(1, tamano_cubo // 2)
                            elif tipo == 'P':
                                z_inicio = z_fin = generador.randint((tamano_cubo // 2) + 1, tamano_cubo)
                            elif tipo == 'C':
                                z_inicio = z_fin = generador.randint(2, tamano_cubo - 1)
                            else:
                                z_inicio = z_fin = generador.randint(1, tamano_cubo)

                            x_inicio = generador.randint(1, tamano_cubo - tamano_nave + 1)
                            x_fin = x_inicio + tamano_nave - 1
                            y_inicio = y_fin = generador.randint(1, tamano_cubo)

                        else:
                            # Eje Y varia
                            if tipo == 'S':
                                z_inicio = z_fin = generador.randint(1, tamano_cubo // 2)
                            elif tipo == 'P':
                                z_inicio = z_fin = generador.randint((tamano_cubo // 2) + 1, tamano_cubo)
                            elif tipo == 'C':
                                z_inicio = z_fin = generador.randint(2, tamano_cubo - 1)
                            else:
                                z_inicio = z_fin = generador.randint(1, tamano_cubo)

                            y_inicio = generador.randint(1, tamano_cubo - tamano_nave + 1)
                            y_fin = y_inicio + tamano_nave - 1
                            x_inicio = x_fin = generador.randint(1, tamano_cubo)

                        p_desde = (z_inicio, x_inicio, y_inicio)
                        p_hasta = (z_fin, x_fin, y_fin)

                    try:
                        ubicar_nave(cubo, flota_actual, tipo, p_desde, p_hasta)
                        nave_colocada = True
                    except UbicacionInvalidaError:
                        nave_colocada = False

                if not nave_colocada:
                    pudo_ubicar_todo = False
                    break

            if not pudo_ubicar_todo:
                break

        if pudo_ubicar_todo:
            return flota_actual

    for z in range(tamano_cubo):
        for x in range(tamano_cubo):
            for y in range(tamano_cubo):
                cubo[z][x][y] = cubo_original[z][x][y]
    raise UbicacionInvalidaError("No se pudo ubicar la flota automaticamente tras multiples intentos.")


def obtener_nave_en_punto(flota, punto):
    """
    Busca si alguna nave de la flota ocupa la coordenada 'punto'.
    
    """
    coordenada = parsear_punto(punto)

    for nave in flota:
        if coordenada in nave['celdas']:
            return nave

    return None


def nave_esta_hundida(nave):
    """
    Determina si una nave esta completamente destruida (hundida).
    
    Regla general: Todas sus celdas deben haber sido destruidas.
    Regla del Portaaviones ('P'): Cada una de sus celdas requiere 2 impactos.
    Otras naves: Cada celda requiere 1 impacto.
    
    """
    impactos_por_celda = nave.get('impactos_por_celda', {})
    tipo = nave['tipo']
    impactos_necesarios = 2 if tipo == 'P' else 1

    for celda in nave['celdas']:
        impactos_en_esta_celda = impactos_por_celda.get(celda, 0)
        if impactos_en_esta_celda < impactos_necesarios:
            return False

    return True


def toda_la_flota_hundida(flota):
    """
    Verifica si todas las naves de la flota han sido destruidas.
    Se utiliza en partida.py para determinar si hay un ganador.

    """
    if not flota:
        return False

    for nave in flota:
        if not nave.get('hundida', False):
            return False

    return True


def registrar_impacto(flota, punto):
    """
    Registra un disparo sobre la flota en la celda 'punto'.
    
    Evalua si el disparo cae en agua, si impacta una nave, si la averia o si la hunde.
    Tambien reporta los efectos especiales de naves (Destructor, Estacion Orbital).

    """
    coordenada = parsear_punto(punto)
    nave = obtener_nave_en_punto(flota, coordenada)

    # 1. Caso: El disparo cayo en el agua
    if nave is None:
        return {
            "resultado": "agua",
            "tipo_nave": None,
            "nombre_nave": None,
            "mensaje": "Agua.",
            "efecto_especial": None
        }

    # Inicializamos diccionarios de impactos si no estuvieran presentes
    if 'impactos' not in nave:
        nave['impactos'] = set()
    if 'impactos_por_celda' not in nave:
        nave['impactos_por_celda'] = {}

    impactos_actuales = nave['impactos_por_celda'].get(coordenada, 0)
    tipo = nave['tipo']
    impactos_maximos_celda = 2 if tipo == 'P' else 1

    # 2. Caso: La celda ya habia recibido los impactos maximos
    if impactos_actuales >= impactos_maximos_celda:
        return {
            "resultado": "repetido",
            "tipo_nave": tipo,
            "nombre_nave": nave['nombre'],
            "mensaje": f"La celda {coordenada} ya habia sido impactada previamente.",
            "efecto_especial": None
        }

    # 3. Caso: Impacto exitoso sobre la celda
    nave['impactos'].add(coordenada)
    nave['impactos_por_celda'][coordenada] = impactos_actuales + 1

    # Efecto especial del Destructor ('D'): Al ser impactada revela una celda ocupada del rival
    efecto_especial = None
    if tipo == 'D':
        efecto_especial = "revelar_celda_rival"

    # Se evalua si con este impacto la nave se hunde
    if nave_esta_hundida(nave):
        nave['hundida'] = True

        # Efecto especial de la Estacion Orbital ('E'): Al hundirse otorga municion extra
        if tipo == 'E':
            efecto_especial = "otorgar_municion_extra"

        return {
            "resultado": "hundido",
            "tipo_nave": tipo,
            "nombre_nave": nave['nombre'],
            "mensaje": f"Hundido! {nave['nombre']} completamente destruido.",
            "efecto_especial": efecto_especial
        }

    # Si la nave recibio un impacto pero aun no esta hundida (averiada)
    celdas_impactadas = sum(nave['impactos_por_celda'].values())
    total_celdas = len(nave['celdas']) * impactos_maximos_celda

    return {
        "resultado": "impacto",
        "tipo_nave": tipo,
        "nombre_nave": nave['nombre'],
        "mensaje": f"Impacto. {nave['nombre']} averiado ({celdas_impactadas} de {total_celdas}).",
        "efecto_especial": efecto_especial
    }
