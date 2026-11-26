import radar
import tablero


def armar_estado_prueba():
    """Arma un estado mínimo con 1 fragata de 2 celdas para cada jugador."""
    cubo_p1 = tablero.crear_tablero(8)
    cubo_a1 = tablero.crear_tablero(8)
    cubo_p2 = tablero.crear_tablero(8)
    cubo_a2 = tablero.crear_tablero(8)

    cubo_p1[0][0][0] = 'F'
    cubo_p1[0][0][1] = 'F'

    cubo_p2[1][1][1] = 'F'
    cubo_p2[1][1][2] = 'F'

    return {
        'jugador1': {
            'tablero_propio': cubo_p1,
            'tablero_atacado': cubo_a1,
            'indice_naves': radar.crear_indice_naves(cubo_p1)
        },
        'jugador2': {
            'tablero_propio': cubo_p2,
            'tablero_atacado': cubo_a2,
            'indice_naves': radar.crear_indice_naves(cubo_p2)
        }
    }


# ---------------------------------------------------------
# 1. PRUEBAS DE LOS 3 MÉTODOS DE BÚSQUEDA Y MÉTRICAS
# ---------------------------------------------------------

def test_busquedas_sin_ganador_y_comparaciones():
    estado = armar_estado_prueba()

    gan_lin, met_lin = radar.busqueda_nave_lineal(estado)
    gan_opt, met_opt = radar.busqueda_nave_optimizada(estado)
    gan_rec, met_rec = radar.busqueda_nave_recursiva(estado)

    assert gan_lin is None
    assert gan_opt is None
    assert gan_rec is None

    assert met_opt['comparaciones'] < met_lin['comparaciones']
    assert met_rec['profundidad_max'] == 9


def test_busquedas_detectan_ganador():
    estado = armar_estado_prueba()

    estado['jugador1']['tablero_atacado'][1][1][1] = radar.HUNDIDO
    estado['jugador1']['tablero_atacado'][1][1][2] = radar.HUNDIDO

    assert radar.busqueda_nave_lineal(estado)[0] == 'jugador1'
    assert radar.busqueda_nave_optimizada(estado)[0] == 'jugador1'
    assert radar.busqueda_nave_recursiva(estado)[0] == 'jugador1'


# ---------------------------------------------------------
# 2. PRUEBAS DE ÍNDICE DE NAVES Y SONAR POR PLANOS
# ---------------------------------------------------------

def test_crear_indice_naves_y_sonar_por_planos():
    rival = tablero.crear_tablero(8)
    rival[0][2][3] = 'D'
    rival[0][2][4] = 'D'

    indice = radar.crear_indice_naves(rival)
    assert indice == {'D': [[1, 3, 4], [1, 3, 5]]}

    atacado = tablero.crear_tablero(8)
    contactos, atacado = radar.sonar_por_planos(atacado, rival, 'z', 0)

    assert contactos == 2
    assert atacado[0][2][3] == tablero.DETECTADO
    assert atacado[0][2][4] == tablero.DETECTADO


# ---------------------------------------------------------
# 3. PRUEBAS DE MAPA DE PROBABILIDAD Y DIBUJO
# ---------------------------------------------------------

def test_mapa_probabilidad_y_mejor_objetivo():
    atacado = tablero.crear_tablero(8)
    atacado[3][3][3] = tablero.IMPACTO
    atacado[0][0][0] = tablero.AGUA_MARCADA

    mejor_punto, puntaje, mapa = radar.mejor_objetivo_probabilidad(atacado)

    vecinos_esperados = [
        [5, 4, 4], [3, 4, 4],
        [4, 5, 4], [4, 3, 4],
        [4, 4, 5], [4, 4, 3]
    ]
    assert mejor_punto in vecinos_esperados
    assert puntaje > 0
    assert mapa[0][0][0] == 0


def test_dibujar_plano_probabilidad_valor_invalido():
    mapa = tablero.crear_tablero(8, 0)

    lanzo_error = False
    try:
        radar.dibujar_plano_probabilidad(mapa, 'z', '1')
    except tablero.ErrorTablero:
        lanzo_error = True

    assert lanzo_error is True