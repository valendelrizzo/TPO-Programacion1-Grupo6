import tablero


# ---------------------------------------------------------
# 1. PRUEBAS DE CREACION, LECTURA Y ESCRITURA
# ---------------------------------------------------------

def test_crear_tablero_independiente_y_error_tamano():
    cubo = tablero.crear_tablero(8)

    assert len(cubo) == 8
    cubo[0][0][0] = 'F'
    assert cubo[1][0][0] == tablero.AGUA_SIN_EXPLORAR

    lanzo_error = False
    try:
        tablero.crear_tablero(0)
    except tablero.ErrorTablero:
        lanzo_error = True

    assert lanzo_error is True


def test_validar_leer_y_escribir_celda():
    cubo = tablero.crear_tablero(8)

    assert tablero.validar_punto(cubo, (1, 1, 1)) is True
    assert tablero.validar_punto(cubo, [8, 8, 8]) is True
    assert tablero.validar_punto(cubo, (0, 1, 1)) is False
    assert tablero.validar_punto(cubo, (9, 1, 1)) is False

    tablero.escribir_celda(cubo, (2, 3, 4), tablero.IMPACTO)
    assert tablero.leer_celda(cubo, (2, 3, 4)) == tablero.IMPACTO

    lanzo_error = False
    try:
        tablero.leer_celda(cubo, (9, 1, 1))
    except tablero.ErrorTablero:
        lanzo_error = True

    assert lanzo_error is True


# ---------------------------------------------------------
# 2. PRUEBAS DE VECINOS ORTOGONALES
# ---------------------------------------------------------

def test_vecinos_centro_y_esquina():
    cubo = tablero.crear_tablero(8)

    vecinos_centro = tablero.vecinos(cubo, (4, 4, 4))
    assert len(vecinos_centro) == 6

    vecinos_esquina = tablero.vecinos(cubo, (1, 1, 1))
    assert len(vecinos_esquina) == 3
    assert [2, 1, 1] in vecinos_esquina
    assert [1, 2, 1] in vecinos_esquina
    assert [1, 1, 2] in vecinos_esquina


# ---------------------------------------------------------
# 3. PRUEBAS DE REBANADAS (PLANOS) Y DIBUJO
# ---------------------------------------------------------

def test_obtener_y_aplicar_rebanada():
    cubo = tablero.crear_tablero(8)

    plano = tablero.obtener_rebanada(cubo, 'z', 0)
    plano[2][3] = tablero.DETECTADO
    assert tablero.leer_celda(cubo, (1, 3, 4)) == tablero.AGUA_SIN_EXPLORAR

    tablero.aplicar_rebanada(cubo, plano, 'z', 0)
    assert tablero.leer_celda(cubo, (1, 3, 4)) == tablero.DETECTADO

    lanzo_error = False
    try:
        tablero.validar_plano(cubo, 'w', 0)
    except tablero.ErrorTablero:
        lanzo_error = True

    assert lanzo_error is True


def test_dibujar_plano_y_ocultar_naves():
    cubo = tablero.crear_tablero(8)
    tablero.escribir_celda(cubo, (1, 1, 1), 'F')

    dibujo_propio = tablero.dibujar_plano(cubo, 'z', 1, ocultar_naves=False)
    assert '=========PLANO z=1=========' in dibujo_propio
    assert 'F' in dibujo_propio

    dibujo_oculto = tablero.dibujar_plano(cubo, 'z', 1, ocultar_naves=True)
    assert 'F' not in dibujo_oculto