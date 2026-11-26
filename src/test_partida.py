import partida
import flota
import tablero


# ---------------------------------------------------------
# 1. PRUEBAS DE CREACIÓN DE PARTIDA, TURNOS Y DIFICULTAD
# ---------------------------------------------------------

def test_nueva_partida_1v1_y_cambio_de_turno():
    estado = partida.nueva_partida_1v1({'tamano': 8})

    assert estado['tipo_partida'] == '1v1'
    assert estado['turno_actual'] == 'jugador1'
    assert estado['numero_turno'] == 1
    assert estado['dificultad'] is None

    partida.cambiar_turno(estado)
    assert estado['turno_actual'] == 'jugador2'
    assert estado['numero_turno'] == 1

    partida.cambiar_turno(estado)
    assert estado['turno_actual'] == 'jugador1'
    assert estado['numero_turno'] == 2


def test_dificultades_vs_maquina_y_maquina_vs_maquina():
    estado_vm = partida.nueva_partida_vs_maquina({'tamano': 8}, 'imposible')
    assert estado_vm['tipo_partida'] == 'vs_maquina'
    assert estado_vm['jugador2']['tipo'] == 'maquina'
    assert partida.obtener_dificultad_actual(estado_vm) == 'imposible'

    estado_mm = partida.nueva_partida_maquina_vs_maquina({'tamano': 8}, ('facil', 'imposible'))
    assert partida.obtener_dificultad_actual(estado_mm) == 'facil'
    partida.cambiar_turno(estado_mm)
    assert partida.obtener_dificultad_actual(estado_mm) == 'imposible'


def test_tamano_cubo_invalido_lanza_error():
    lanzo_error = False
    try:
        partida.nueva_partida_1v1({'tamano': 0})
    except tablero.ErrorJuego:
        lanzo_error = True

    assert lanzo_error is True


# ---------------------------------------------------------
# 2. PRUEBAS DE TURNOS, DISPARO Y GANADOR
# ---------------------------------------------------------

def test_ejecutar_turno_sin_flotas_lanza_error():
    estado = partida.nueva_partida_1v1({'tamano': 8})

    lanzo_error = False
    try:
        partida.ejecutar_turno(estado, {'arma': 'T', 'objetivo': (1, 1, 1)})
    except partida.TurnoInvalidoError:
        lanzo_error = True

    assert lanzo_error is True


def test_disparo_ganador_y_partida_terminada():
    estado = partida.nueva_partida_1v1({'tamano': 8})

    j1 = estado['jugador1']
    j2 = estado['jugador2']
    flota.ubicar_nave(j1['tablero_propio'], j1['flota'], 'F', '1,1,1', '1,1,2')
    flota.ubicar_nave(j2['tablero_propio'], j2['flota'], 'F', '2,2,2', '2,2,3')

    assert partida.hay_ganador(estado) is None

    partida.ejecutar_turno(estado, {'arma': 'T', 'objetivo': (2, 2, 2)})
    assert partida.hay_ganador(estado) is None

    partida.ejecutar_turno(estado, {'arma': 'T', 'objetivo': (5, 5, 5)})

    partida.ejecutar_turno(estado, {'arma': 'T', 'objetivo': (2, 2, 3)})
    assert partida.hay_ganador(estado) == 'jugador1'

    lanzo_error = False
    try:
        partida.ejecutar_turno(estado, {'arma': 'T', 'objetivo': (3, 3, 3)})
    except partida.TurnoInvalidoError:
        lanzo_error = True

    assert lanzo_error is True


# ---------------------------------------------------------
# 3. PRUEBAS DE LA MÁQUINA (FÁCIL E IMPOSIBLE)
# ---------------------------------------------------------

def test_maquina_en_turno_humano_lanza_error():
    estado = partida.nueva_partida_vs_maquina({'tamano': 8}, 'imposible')

    lanzo_error = False
    try:
        partida.maquinaLevelImposible(estado)
    except partida.TurnoInvalidoError:
        lanzo_error = True

    assert lanzo_error is True


def test_turno_maquina_facil_e_imposible():
    for dificultad in ('facil', 'imposible'):
        estado = partida.nueva_partida_vs_maquina({'tamano': 8}, dificultad)
        partida.ubicar_flota_automatica(estado['jugador1'])
        partida.ubicar_flota_automatica(estado['jugador2'])

        partida.cambiar_turno(estado)

        if dificultad == 'facil':
            partida.turno_maquina(estado)
        else:
            partida.maquinaLevelImposible(estado)

        assert len(estado['historial']) == 1
        assert estado['turno_actual'] == 'jugador1'