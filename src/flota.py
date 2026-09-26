import copy
import random
import re

## Para el inicio de la partida, en partida.py se debe crear una lista por usuario para definir desde el inicio la cantidad de naves que tiene que poner, a medida que vaya
## agregando las naves, se va a restar la cantidad pendiente del primer elemento de la lista, y se agrega en el segundo elemento de la lista, la nave a la flota con la estructura
## definida abajo. 
## A esa lista del usuario, es la principal en la partida, no solo se debe editar el cubo a medida que pasen los turnos, si no que se debe actualizar la flota del jugador.
## se podrian agregar mas elementos a la lista. como nombre, puntos si es que hay, etc.

# partida={
#   ...
#   flotaJugador1={
#       colocadas=[]
#   }
#}

CATALOGO_NAVES = {
    'F': {
        'nombre': 'Fragata',
        'tamano': 2,
        'cantidad': 3,
        'forma': 'lineal',
        'regla': 'sin_restriccion',
        'descripcion': '2 celdas contiguas en línea recta. Sin restricción de altura.'
    },
    'D': {
        'nombre': 'Destructor',
        'tamano': 3,
        'cantidad': 2,
        'forma': 'lineal',
        'regla': 'sin_restriccion',
        'descripcion': '3 celdas contiguas en línea recta. Sin restricción de altura.'
    },
    'S': {
        'nombre': 'Submarino',
        'tamano': 3,
        'cantidad': 2,
        'forma': 'lineal',
        'regla': 'mitad_inferior_z',
        'descripcion': '3 celdas contiguas en línea recta. Solo en la mitad inferior de z.'
    },
    'C': {
        'nombre': 'Crucero',
        'tamano': 4,
        'cantidad': 1,
        'forma': 'lineal',
        'regla': 'no_bordes_z',
        'descripcion': '4 celdas contiguas en línea recta. No puede ocupar z = 1 ni z = N.'
    },
    'P': {
        'nombre': 'Portaaviones',
        'tamano': 5,
        'cantidad': 1,
        'forma': 'lineal',
        'regla': 'mitad_superior_z',
        'descripcion': '5 celdas contiguas en línea recta. Solo en la mitad superior de z.'
    },
    'E': {
        'nombre': 'Estación orbital',
        'tamano': 8,
        'dimensiones': (2, 2, 2),
        'cantidad': 1,
        'forma': 'bloque',
        'regla': 'no_caras_exteriores',
        'descripcion': 'Bloque de 2x2x2 celdas. No puede tocar ninguna cara exterior del cubo.'
    }
}

class UbicacionInvalidaError(Exception): ## algo generico dado que no vimos todavia excepciones
    """Excepción lanzada cuando una nave no cumple las reglas de colocación."""
    pass

def parsear_punto(punto):
    """
    Recibe un punto como texto ("z,x,y") o como tupla/lista ((z, x, y)).
    Devuelve siempre una tupla con los tres enteros (z, x, y).
    """

    # -------------------------------------------------------------
    # INTENTO 1: Suponemos que el usuario ingresó un texto ("z,x,y")
    # -------------------------------------------------------------
    try:
        # Expresión regular que valida exactamente 3 números separados por comas  3,5,4-3,5,5 
        patron = r'^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$'
        coincidencia = re.match(patron, punto)

        if coincidencia: ## Si cumple el formato entonces
            texto_z = coincidencia.group(1)
            texto_x = coincidencia.group(2)
            texto_y = coincidencia.group(3)

            z = int(texto_z)
            x = int(texto_x)
            y = int(texto_y)

            return (z, x, y)
        else:
            # Si era texto pero no cumplía el formato "z,x,y"
            raise UbicacionInvalidaError(
                f"Formato incorrecto: '{punto}'. Debe ingresarse como 'z,x,y' (por ejemplo: '3,5,4')."
            )

    except TypeError:
        # re.match lanza TypeError si 'punto' no es un string (por ejemplo, si vino una tupla o lista)
        pass

    # -------------------------------------------------------------
    # INTENTO 2: Si no era texto, probamos si es una secuencia (tupla/lista)
    # -------------------------------------------------------------
    try:
        if len(punto) != 3:
            raise UbicacionInvalidaError("El punto debe contener exactamente 3 coordenadas (z, x, y).")

        z = int(punto[0])
        x = int(punto[1])
        y = int(punto[2])

        return (z, x, y)

    except (TypeError, ValueError):
        # TypeError: el dato no tiene longitud ni índices (ej: un número suelto o None)
        # ValueError: alguno de los elementos no se pudo transformar a int
        raise UbicacionInvalidaError(
            f"El valor '{punto}' no es una coordenada válida."
        )

def generar_celdas_nave(tipo_nave, p_desde, p_hasta):
    """
    Toma el tipo de nave y sus dos puntos extremos (desde y hasta).
    Verifica que la forma geométrica sea válida (línea recta o bloque 2x2x2)
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
    # Deben colocarse en línea recta sobre un único eje (Z, X o Y)
    # =========================================================================
    if forma == 'lineal':
        # Calculamos cuánto cambia la nave en cada eje
        diferencia_z = z_fin - z_inicio
        diferencia_x = x_fin - x_inicio
        diferencia_y = y_fin - y_inicio

        # Contamos cuántos ejes cambiaron de valor
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

        # REGLA 2: No puede ser un solo punto si el tamaño es mayor a 1
        if ejes_que_cambian == 0:
            raise UbicacionInvalidaError(
                f"El punto de inicio y de fin son iguales. La nave {nombre} mide más de 1 celda."
            )

        # REGLA 3: Validar que la longitud coincida con el tamaño de la nave
        # La distancia entre extremos es el valor absoluto de la diferencia, + 1 celda inicial
        longitud_ingresada = max(abs(diferencia_z), abs(diferencia_x), abs(diferencia_y)) + 1
        tamano_requerido = datos_nave['tamano']

        if longitud_ingresada != tamano_requerido:
            raise UbicacionInvalidaError(
                f"Tamaño incorrecto para {nombre}. "
                f"Debe medir {tamano_requerido} celdas, pero el tramo ingresado mide {longitud_ingresada}."
            )

        # 4. Determinar hacia dónde avanza el paso (hacia adelante +1 o hacia atrás -1) Quiza habria que diferenciar para uno solo de los ejes, ya que solo uno de ellos cambia -- REVISAR
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

            # Avanzamos un paso en la dirección correspondiente
            actual_z = actual_z + paso_z
            actual_x = actual_x + paso_x
            actual_y = actual_y + paso_y

        return celdas_ocupadas

    # =========================================================================
    # CASO B: Estación Orbital (forma == 'bloque')
    # Debe ser un cubo cerrado de 2x2x2 (8 celdas en total)
    # =========================================================================
    elif forma == 'bloque':
        # Identificamos el valor menor y mayor en cada dimensión
        # (por si el usuario ingresó los puntos en orden inverso)
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
                "La Estación Orbital debe abarcar exactamente un bloque de 2x2x2 celdas."
            )

        # Generamos las 8 celdas recorriendo cada eje desde el valor menor al mayor
        celdas_ocupadas = []
        for z in range(min_z, max_z + 1):
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    celda = (z, x, y)
                    celdas_ocupadas.append(celda)

        return celdas_ocupadas
    
#debe devolver "cubo y flota actualizados, o excepción"
def ubicar_nave(cubo, flota, nave, puntoD, puntoH):
    """Ubica una nave en el tablero y actualiza la flota. Lanza UbicacionInvalidaError si falla."""

    if nave not in CATALOGO_NAVES:
        raise UbicacionInvalidaError(f"Tipo de nave '{nave}' no reconocido.")

    p_desde = parsear_punto(puntoD)
    p_hasta = parsear_punto(puntoH)

    celdas = generar_celdas_nave(nave, p_desde, p_hasta)
    ## validar_reglas_ubicacion(cubo, nave, celdas) falta implementar -- REVISAR

    # Marcado en el tablero
    for z, x, y in celdas:
        cubo[z - 1][x - 1][y - 1] = nave

    # Registro en la flota
    if flota is None:
        flota = []

    flota.append({
        'tipo': nave,
        'nombre': CATALOGO_NAVES[nave]['nombre'],
        'celdas': celdas,
        'impactos': set(),
        'hundida': False
    })

    return cubo, flota

#debe devolver "flota ubicada"
def ubicacion_automatica(cubo,catalogo,semilla):
  return 0
