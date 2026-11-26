import flota
import tablero


# ---------------------------------------------------------
# 1. PRUEBAS DE UBICACION MANUAL, FORMAS Y SEPARACION
# ---------------------------------------------------------

def test_ubicar_nave_lineal_y_bloque_estacion():
    cubo = tablero.crear_tablero(8)
    lista_flota = []

    flota.ubicar_nave(cubo, lista_flota, 'F', '1,1,1', '1,1,2')
    assert tablero.leer_celda(cubo, (1, 1, 1)) == 'F'
    assert tablero.leer_celda(cubo, (1, 1, 2)) == 'F'

    flota.ubicar_nave(cubo, lista_flota, 'E', '4,4,4', '5,5,5')
    assert len(lista_flota) == 2
    assert len(lista_flota[1]['celdas']) == 8


def test_ubicacion_invalida_diagonal_y_pegadas():
    cubo = tablero.crear_tablero(8)
    lista_flota = []

    lanzo_diagonal = False
    try:
        flota.ubicar_nave(cubo, lista_flota, 'F', '1,1,1', '1,2,2')
    except flota.UbicacionInvalidaError:
        lanzo_diagonal = True
    assert lanzo_diagonal is True

    flota.ubicar_nave(cubo, lista_flota, 'F', '1,1,1', '1,1,2')
    lanzo_pegada = False
    try:
        flota.ubicar_nave(cubo, lista_flota, 'F', '1,2,1', '1,2,2')
    except flota.UbicacionInvalidaError:
        lanzo_pegada = True
    assert lanzo_pegada is True


# ---------------------------------------------------------
# 2. PRUEBAS DE RESTRICCIONES DE ALTURA Y UBICACION AUTOMATICA
# ---------------------------------------------------------

def test_restricciones_altura_submarino_y_portaaviones():
    cubo = tablero.crear_tablero(8)
    lista_flota = []

    lanzo_submarino = False
    try:
        flota.ubicar_nave(cubo, lista_flota, 'S', '6,1,1', '6,1,3')
    except flota.UbicacionInvalidaError:
        lanzo_submarino = True
    assert lanzo_submarino is True

    lanzo_portaaviones = False
    try:
        flota.ubicar_nave(cubo, lista_flota, 'P', '2,1,1', '2,1,5')
    except flota.UbicacionInvalidaError:
        lanzo_portaaviones = True
    assert lanzo_portaaviones is True


def test_ubicacion_automatica_completa():
    cubo = tablero.crear_tablero(8)
    lista_flota = flota.ubicacion_automatica(cubo, semilla=42)

    assert len(lista_flota) == 10
    assert flota.toda_la_flota_hundida(lista_flota) is False


# ---------------------------------------------------------
# 3. PRUEBAS DE IMPACTOS, PORTAAVIONES Y SERIALIZACIÓN
# ---------------------------------------------------------

def test_impacto_agua_hundimiento_y_efectos():
    cubo = tablero.crear_tablero(8)
    lista_flota = []
    flota.ubicar_nave(cubo, lista_flota, 'D', '1,1,1', '1,1,3')

    res_agua = flota.registrar_impacto(lista_flota, (5, 5, 5))
    assert res_agua['resultado'] == 'agua'

    res_impacto = flota.registrar_impacto(lista_flota, (1, 1, 1))
    assert res_impacto['resultado'] == 'impacto'
    assert res_impacto['efecto_especial'] == 'revelar_celda_rival'

    # Terminamos de hundir el Destructor
    flota.registrar_impacto(lista_flota, (1, 1, 2))
    res_hundido = flota.registrar_impacto(lista_flota, (1, 1, 3))
    assert res_hundido['resultado'] == 'hundido'
    assert flota.toda_la_flota_hundida(lista_flota) is True


def test_portaaviones_requiere_doble_impacto_por_celda():
    cubo = tablero.crear_tablero(8)
    lista_flota = []
    flota.ubicar_nave(cubo, lista_flota, 'P', '6,2,1', '6,2,5')

    for y in range(1, 6):
        res = flota.registrar_impacto(lista_flota, (6, 2, y))
        assert res['resultado'] == 'impacto'
    assert flota.nave_esta_hundida(lista_flota[0]) is False

    for y in range(1, 5):
        flota.registrar_impacto(lista_flota, (6, 2, y))
    res_final = flota.registrar_impacto(lista_flota, (6, 2, 5))
    assert res_final['resultado'] == 'hundido'
    assert flota.nave_esta_hundida(lista_flota[0]) is True


def test_guardar_y_reponer_flota():
    cubo = tablero.crear_tablero(8)
    lista_flota = []
    flota.ubicar_nave(cubo, lista_flota, 'F', '1,1,1', '1,1,2')
    flota.registrar_impacto(lista_flota, (1, 1, 1))

    datos_json = flota.datos_flota_para_guardar(lista_flota)

    cubo_nuevo = tablero.crear_tablero(8)
    cubo_nuevo, flota_repuesta = flota.reponer_flota(cubo_nuevo, datos_json)

    assert len(flota_repuesta) == 1
    assert flota_repuesta[0]['impactos'] == [[1, 1, 1]]
    assert tablero.leer_celda(cubo_nuevo, (1, 1, 2)) == 'F'