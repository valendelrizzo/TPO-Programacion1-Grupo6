import os
import registro
import tablero


# ---------------------------------------------------------
# 1. PRUEBAS DE REGISTRO EN MEMORIA
# ---------------------------------------------------------

def test_registro_en_memoria_y_error_sin_iniciar():
    registro.gPartidaActual = {}

    lanzo_error = False
    try:
        registro.registrar_ataque('T', [[1, 1, 1]])
    except registro.ErrorRegistro:
        lanzo_error = True

    assert lanzo_error is True

    registro.iniciar_partida(['F'], ['D'], 'Batalla 1')
    registro.registrar_ataque('T', [[2, 3, 4]])
    final = registro.terminar_partida()

    assert final['nombre'] == 'Batalla 1'
    assert len(final['movimientos']) == 1
    assert final['movimientos'][0]['arma'] == 'T'


# ---------------------------------------------------------
# 2. PRUEBAS DE HISTORIAL, ESTADÍSTICAS E IMPACTO ACTIVO
# ---------------------------------------------------------

def test_registrar_jugada_y_estadisticas():
    estado = {
        'ganador': 'jugador1',
        'jugador1': {'nombre': 'Jugador 1'},
        'jugador2': {'nombre': 'Jugador 2'},
        'historial': []
    }

    registro.registrar_jugada(estado, {
        'jugador': 'Jugador 1',
        'arma': 'R',
        'celdas': [
            {'punto': [1, 1, 1], 'resultado': tablero.IMPACTO, 'detalle': {'resultado': 'impacto'}},
            {'punto': [1, 1, 2], 'resultado': tablero.AGUA_MARCADA, 'detalle': {'resultado': 'agua'}}
        ]
    })

    registro.registrar_jugada(estado, {
        'jugador': 'Jugador 1',
        'arma': 'S',
        'celdas': []
    })

    stats = registro.estadisticas(estado)
    j1 = stats['jugador1']

    assert j1['turnos'] == 2
    assert j1['disparos'] == 1
    assert j1['sonares'] == 1
    assert j1['impactos'] == 1
    assert j1['agua'] == 1
    assert j1['precision'] == 50.0
    assert registro.resumen_partida(estado)['ganador'] == 'jugador1'


def test_obtener_ultimo_impacto_activo():
    cubo_atacado = tablero.crear_tablero(8, tablero.AGUA_SIN_EXPLORAR)
    tablero.escribir_celda(cubo_atacado, [2, 2, 2], tablero.IMPACTO)

    estado = {
        'historial': [
            {
                'jugador': 'Jugador 1',
                'celdas': [{'punto': [2, 2, 2], 'resultado': tablero.IMPACTO}]
            }
        ]
    }

    assert registro.obtener_ultimo_impacto_activo(estado, 'Jugador 1', cubo_atacado) == [2, 2, 2]

    tablero.escribir_celda(cubo_atacado, [2, 2, 2], tablero.HUNDIDO)
    assert registro.obtener_ultimo_impacto_activo(estado, 'Jugador 1', cubo_atacado) is None


# ---------------------------------------------------------
# 3. PRUEBAS DE PERSISTENCIA EN JSON (GUARDAR, LISTAR, CARGAR)
# ---------------------------------------------------------

def test_guardar_listar_y_cargar_partida_json():
    ruta_original = registro.RUTA
    registro.RUTA = os.path.join(os.path.dirname(__file__), 'temp_datos_test.json')

    try:
        registro.guardar_partida(None, None)

        estado_ejemplo = {'turno_actual': 'jugador1', 'numero_turno': 4}
        registro.guardar_partida(estado_ejemplo, 'Partida Guardada 1')

        assert registro.listar_partidas() == ['1-Partida Guardada 1']

        recuperada = registro.cargar_partida('Partida Guardada 1')
        assert recuperada['numero_turno'] == 4
        assert registro.listar_partidas() == []

        lanzo_error = False
        try:
            registro.cargar_partida('No Existe')
        except registro.ErrorRegistro:
            lanzo_error = True

        assert lanzo_error is True

    finally:
        if os.path.exists(registro.RUTA):
            os.remove(registro.RUTA)
        registro.RUTA = ruta_original
        registro.fileState = []
        registro.fileStateLoaded = False


def test_guardar_partida_invalida_lanza_error():
    ruta_original = registro.RUTA
    registro.RUTA = os.path.join(os.path.dirname(__file__), 'temp_datos_test.json')

    try:
        registro.guardar_partida(None, None)

        lanzo_error = False
        try:
            registro.guardar_partida({'turno_actual': 'jugador1'}, '   ')
        except registro.ErrorRegistro:
            lanzo_error = True

        assert lanzo_error is True

    finally:
        if os.path.exists(registro.RUTA):
            os.remove(registro.RUTA)
        registro.RUTA = ruta_original
        registro.fileState = []
        registro.fileStateLoaded = False