import armamento
import tablero as cubo


def crear_tablero_vacio():
    """Arma un cubo de 8x8x8 lleno de agua para usar en las pruebas."""
    return [[['~' for _ in range(8)] for _ in range(8)] for _ in range(8)]


# ---------------------------------------------------------
# 1. PRUEBAS DE MUNICIÓN
# ---------------------------------------------------------

def test_municion_inicial_y_descuento():
    municion = armamento.crear_municion_jugador()

    assert municion['T'] is None
    assert municion['O'] == 1
    assert armamento.tiene_municion('O', municion) is True

    restante = armamento.descontar_municion('O', municion, 1)
    assert restante == 0
    assert armamento.tiene_municion('O', municion) is False

    lanzo_error = False
    try:
        armamento.descontar_municion('O', municion, 1)
    except armamento.ErrorArmamento:
        lanzo_error = True

    assert lanzo_error is True


# ---------------------------------------------------------
# 2. PRUEBAS DE DISPAROS BÁSICOS Y VALIDACIONES
# ---------------------------------------------------------

def test_torpedo_al_agua():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    resultado = armamento.disparar_arma('T', (2, 3, 4), tablero, {}, municion, [])

    assert resultado['exito'] is True
    assert resultado['cantidad_impactos'] == 0
    assert cubo.leer_celda(tablero, (2, 3, 4)) == cubo.AGUA_MARCADA


def test_disparo_repetido_lanza_error():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    armamento.disparar_arma('T', (2, 2, 2), tablero, {}, municion, [])

    lanzo_error = False
    try:
        armamento.disparar_arma('T', (2, 2, 2), tablero, {}, municion, [])
    except armamento.ErrorArmamento:
        lanzo_error = True

    assert lanzo_error is True


def test_coordenada_fuera_de_rango_lanza_error():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    lanzo_error = False
    try:
        armamento.disparar_arma('T', (9, 1, 1), tablero, {}, municion, [])
    except armamento.ErrorArmamento:
        lanzo_error = True

    assert lanzo_error is True


def test_misil_racimo_y_carga_profundidad():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    res_racimo = armamento.disparar_arma('R', (4, 4, 4), tablero, {}, municion, [])
    assert len(res_racimo['celdas']) == 7
    assert res_racimo['municion_restante'] == 2

    res_carga = armamento.disparar_arma('C', (1, 6, 6), tablero, {}, municion, [])
    assert len(res_carga['celdas']) == 8
    assert res_carga['municion_restante'] == 1


def test_barrido_laser_eje_invalido():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    lanzo_error = False
    try:
        armamento.disparar_arma('L', (3, 3, 3), tablero, {}, municion, [], eje='z')
    except armamento.ErrorArmamento:
        lanzo_error = True

    assert lanzo_error is True


# ---------------------------------------------------------
# 3. PRUEBAS DE LAS ARMAS RECURSIVAS (O y G)
# ---------------------------------------------------------

def test_onda_expansiva_recursiva_centro():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    resultado = armamento.disparar_arma('O', [4, 4, 4], tablero, {}, municion, [])

    assert resultado['exito'] is True
    assert resultado['municion_restante'] == 0
    assert len(resultado['celdas']) > 7


def test_onda_expansiva_en_esquina_no_se_sale_ni_repite():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    resultado = armamento.disparar_arma('O', (1, 1, 1), tablero, {}, municion, [])

    assert resultado['exito'] is True

    vistas = []
    for item in resultado['celdas']:
        punto = item['punto']
        assert punto not in vistas
        assert armamento.en_rango(tablero, punto) is True
        vistas.append(punto)


def test_torpedo_guiado_sin_nave_lanza_error():
    tablero = crear_tablero_vacio()
    municion = armamento.crear_municion_jugador()

    lanzo_error = False
    try:
        armamento.disparar_arma('G', (5, 5, 5), tablero, {}, municion, [])
    except armamento.ErrorArmamento:
        lanzo_error = True

    assert lanzo_error is True