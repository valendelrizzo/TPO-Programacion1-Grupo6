import re
import tablero
import flota
import radar
import armamento
import registro
import random


class ErrorPartida(tablero.ErrorJuego):
    """Clase base para errores en el modulo de partida"""
    pass


class OpcionInvalidaError(ErrorPartida):
    """Lanzada cuando se ingresa una opcion inexistente en los menus"""
    pass


class TurnoInvalidoError(ErrorPartida):
    """Lanzada cuando una jugada o accion de turno no puede llevarse a cabo"""
    pass


#DEFINICION DE ESTRUCTURA DEL JUGADOR Y LA PARTIDA

def crear_estructura_jugador(nombre, tipo, tamano_cubo):
    """
    Crea y devuelve la estructura de datos correspondiente a un jugador.
    
    Cada jugador tiene:
    - nombre: nombre para mostrar en pantalla ('Jugador 1', 'Jugador 2', 'Maquina').
    - tipo: 'humano' o 'maquina'.
    - tablero_propio: Matriz donde ubica sus naves ('~' para agua, letra para nave).
    - tablero_atacado: Matriz donde ve los disparos realizados al rival ('~' sin explorar).
    - flota: Lista de diccionarios con cada nave ubicada, sus celdas e impactos.

    """
    return {
        "nombre": nombre,
        "tipo": tipo,
        "tablero_propio": tablero.crear_tablero(tamano_cubo),
        "tablero_atacado": tablero.crear_tablero(tamano_cubo, '~'),
        "flota": [],
        "municion": armamento.crear_municion_jugador(),
        "indice_naves": {}
    }


def nueva_partida_1v1(configuracion):
    """
    Recibe configuracion y devuelve el estado inicial de dos humanos.
    Lanza ErrorTablero si el tamano no es valido.
    """
    tamano=configuracion.get("tamano", 8)

    jugador1=crear_estructura_jugador("Jugador 1", "humano", tamano)
    jugador2=crear_estructura_jugador("Jugador 2", "humano", tamano)

    partida={
        "tipo_partida": "1v1",
        "tamano_cubo": tamano,
        "turno_actual": "jugador1",
        "numero_turno": 1,
        "ganador": None,
        "dificultad": None,
        "jugador1": jugador1,
        "jugador2": jugador2,
        "historial": [],

        # Claves de compatibilidad directa con versiones previas
        #TODO: y esto? REVISAR
        "tableroPropio1": jugador1["tablero_propio"],
        "tableroAtacado1": jugador1["tablero_atacado"],
        "tableroPropio2": jugador2["tablero_propio"],
        "tableroAtacado2": jugador2["tablero_atacado"]
    }
    return partida


def nueva_partida_vs_maquina(configuracion, dificultad="facil"):
    """Recibe configuracion y dificultad; devuelve estado contra maquina. Lanza ErrorTablero"""
    partida = nueva_partida_1v1(configuracion)
    partida['tipo_partida'] = 'vs_maquina'
    partida['dificultad'] = dificultad
    partida['jugador2']['nombre'] = 'Maquina'
    partida['jugador2']['tipo'] = 'maquina'
    return partida


def nueva_partida_maquina_vs_maquina(configuracion, dificultades=("facil", "facil")):
    """Devuelve un estado entre maquinas sin ubicar flotas. Lanza ErrorTablero por tamano"""
    partida = nueva_partida_vs_maquina(configuracion)
    partida['tipo_partida'] = 'maquina_vs_maquina'
    partida['dificultad'] = dificultades
    partida['jugador1']['nombre'] = 'Maquina 1'
    partida['jugador1']['tipo'] = 'maquina'
    partida['jugador2']['nombre'] = 'Maquina 2'
    return partida


#FUNCIONES AUXILIARES GESTION DE TURNOS

def obtener_jugador_actual(estado):
    """
    Devuelve la estructura del jugador a quien le corresponde realizar la jugada actual.

    """
    clave = estado["turno_actual"]  # 'jugador1' o 'jugador2'
    return estado[clave]


def obtener_jugador_rival(estado):
    """
    Devuelve la estructura del jugador rival (el que defiende en este turno).

    """
    if estado["turno_actual"] == "jugador1":
        return estado["jugador2"]
    else:
        return estado["jugador1"]


def cambiar_turno(estado):
    """
    Alterna el turno entre jugador1 y jugador2 e incrementa el contador de turnos.

    """
    if estado["turno_actual"] == "jugador1":
        estado["turno_actual"] = "jugador2"
    else:
        estado["turno_actual"] = "jugador1"
        estado["numero_turno"] = estado["numero_turno"] + 1


#FUNCIONES PUBLICAS REQUERIDAS

def hay_ganador(estado):
    """
    Verifica si alguno de los dos jugadores ha ganado la partida (si hundio toda la flota rival).

    """
    flota_j1 = estado["jugador1"]["flota"]
    flota_j2 = estado["jugador2"]["flota"]

    #Si la flota del jugador 2 esta completamente destruida, gana el jugador 1
    if len(flota_j2) > 0 and flota.toda_la_flota_hundida(flota_j2):
        estado["ganador"] = "jugador1"
        return "jugador1"

    #igual pero alrevez
    if len(flota_j1) > 0 and flota.toda_la_flota_hundida(flota_j1):
        estado["ganador"] = "jugador2"
        return "jugador2"

    return None


def aplicar_efectos_especiales(resultado, atacante, defensor):
    """Aplica efectos de destructor y estacion al estado y devuelve mensajes adicionales"""
    mensajes=[]
    for celda in resultado['celdas']:
        detalle=celda.get('detalle', {})
        efecto=detalle.get('efecto_especial')
        if efecto=='revelar_celda_rival':
            revelada=False
            for nave in atacante['flota']:
                for punto in nave['celdas']:
                    if not revelada and tablero.leer_celda(defensor['tablero_atacado'],punto)==tablero.AGUA_SIN_EXPLORAR:
                        tablero.escribir_celda(defensor['tablero_atacado'], punto, tablero.DETECTADO)
                        mensajes.append(f'El destructor revela una celda rival: {punto}.')
                        revelada = True
        elif efecto=='otorgar_municion_extra':
            #la consigna dice que dar asi que doy uno de cada arma que tiene usos limitados
            for arma in ('R','C','S','L'):
                atacante['municion'][arma]+=1
            mensajes.append('La estacion hundida otorga una municion extra a todas als armas.')
    return mensajes


def ejecutar_turno(estado,jugada):
    """Recibe estado y jugada;devuelve estado actualizado. Lanza ErrorJuego si la jugada falla"""
    if hay_ganador(estado):
        raise TurnoInvalidoError('La partida ya termino.')
    atacante=obtener_jugador_actual(estado)
    defensor=obtener_jugador_rival(estado)
    if not atacante['flota'] or not defensor['flota']:
        raise TurnoInvalidoError('Primero deben ubicarse ambas flotas.')
    arma=jugada.get('arma','T')
    objetivo=jugada.get('objetivo')
    if objetivo is not None:
        objetivo=flota.parsear_punto(objetivo)
    resultado=armamento.selec_catalogo(
        arma,objetivo,atacante['tablero_atacado'],defensor['tablero_propio'],
        atacante['municion'],defensor['flota'],jugada.get('eje'),jugada.get('valor'))
    mensajes=[]
    for celda in resultado['celdas']:
        if celda['resultado'] in(tablero.IMPACTO,tablero.AGUA_MARCADA):
            mensajes.append(f"{celda['punto']}: {celda['detalle']['mensaje']}")
    if resultado['codigo_arma']=='S':
        mensajes.append(f"Sonar sobre {resultado['eje']}={resultado['valor']} "
                        f"{resultado['contactos']} contactos detectados.")
    mensajes+=aplicar_efectos_especiales(resultado,atacante,defensor)
    if not mensajes:
        mensajes.append('El barrido no alcanzo celdas nuevas')
    registro.registrar_jugada(estado,{
        'turno': estado['numero_turno'],'jugador': atacante['nombre'],
        'arma': resultado['codigo_arma'],'objetivo': objetivo,
        'eje': jugada.get('eje'),'valor': jugada.get('valor'),
        'resultado': resultado['estado'],'celdas': resultado['celdas'],
        'mensaje': '\n'.join(mensajes)
    })
    if not hay_ganador(estado):
        cambiar_turno(estado)
    return estado


def turno_maquina(estado):
    """Elige un torpedo valido y devuelve el estado actualizado. Lanza TurnoInvalidoError si falla"""
    atacante=obtener_jugador_actual(estado)
    defensor=obtener_jugador_rival(estado)
    if atacante['tipo'] !='maquina':
        raise TurnoInvalidoError('El turno actual no es de la maquina.')
    celdas_disponibles=[]
    for z in range(1,estado['tamano_cubo']+1):
        for x in range(1,estado['tamano_cubo']+1):
            for y in range(1,estado['tamano_cubo']+1):
                punto=(z,x,y)
                marca=tablero.leer_celda(atacante['tablero_atacado'],punto)
                if marca in(tablero.AGUA_SIN_EXPLORAR,tablero.DETECTADO):
                    celdas_disponibles.append(punto)
                elif marca==tablero.IMPACTO:
                    nave=flota.obtener_nave_en_punto(defensor['flota'],punto)
                    if nave is not None and nave['tipo']=='P':
                        if nave['impactos_por_celda'].get(punto,0)<2:
                            celdas_disponibles.append(punto)
    if not celdas_disponibles:
        raise TurnoInvalidoError('No quedan celdas para disparar')
    return ejecutar_turno(estado,{'arma': 'T','objetivo': random.choice(celdas_disponibles)})


configuracionG={'tamano':8}


def leer_opcion(mensaje,patron):
    """Pide texto validado por regex y lo devuelve. Repite ante errores;puede lanzar EOFError"""
    while True:
        try:
            texto=input(mensaje).strip()
            if not re.fullmatch(patron,texto):
                raise OpcionInvalidaError('Opcion invalida. intente de nuevo.')
        except OpcionInvalidaError as error:
            print(error)
        else:
            return texto


def leer_entero(mensaje,minimo,maximo=None,predeterminado=None):
    """Pide y devuelve un entero en rango. Repite ante errores;puede lanzar EOFError"""
    while True:
        texto=leer_opcion(mensaje,r'[0-9]*')
        try:
            if texto=='' and predeterminado is not None:
                valor=predeterminado
            else:
                valor=int(texto)
            if valor<minimo or(maximo is not None and valor>maximo):
                raise OpcionInvalidaError('Valor fuera del rango permitido.')
        except(ValueError,OpcionInvalidaError)as error:
            print(error)
        else:
            return valor


def leer_punto(cubo):
    """Pide z,x,y y devuelve una tupla valida desde 1. Repite ante datos invalidos"""
    while True:
        try:
            punto=flota.parsear_punto(input('Objetivo(z,x,y): '))
            if not tablero.validar_punto(cubo,punto):
                raise OpcionInvalidaError('El punto queda fuera del cubo')
        except(tablero.ErrorJuego,ValueError)as error:
            print(error)
        else:
            return punto


def ubicar_flota_manual(jugador):
    """Pide las naves pendientes y actualiza el jugador. Repite ante ubicaciones invalidas"""
    pendientes = {}
    for letra in flota.CATALOGO_NAVES:
        pendientes[letra] = flota.CATALOGO_NAVES[letra]['cantidad']
    while sum(pendientes.values()) > 0:
        print('Pendientes:', '  '.join(f'{letra} x{pendientes[letra]}' for letra in pendientes))
        letra = leer_opcion('Nave (F/D/S/C/P/E): ', r'[FfDdSsCcPpEe]').upper()
        try:
            if pendientes[letra] == 0:
                raise OpcionInvalidaError('Ya se ubicaron todas las naves de ese tipo')
            tramo = input('Desde-hasta (z,x,y-z,x,y): ').strip()
            if not re.fullmatch(r'\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*-\s*[0-9]+\s*,\s*[0-9]+\s*,\s*[0-9]+\s*', tramo):
                raise OpcionInvalidaError('Formato de tramo invalido.')
            desde, hasta = tramo.split('-')
            flota.ubicar_nave(jugador['tablero_propio'], jugador['flota'], letra, desde, hasta)
        except (tablero.ErrorJuego, ValueError) as error:
            print(error)
        else:
            pendientes[letra] -= 1
            print('Ubicada.')


def ubicar_flota_automatica(jugador):
    """Ubica la flota y actualiza el jugador. Lanza UbicacionInvalidaError si no hay lugar"""
    jugador['flota'] = flota.ubicacion_automatica(jugador['tablero_propio'])


def preparar_flotas(estado):
    """Pide ubicacion a humanos y ubica maquinas; construye los indices una vez por partida"""
    opciones = {'1': ubicar_flota_manual, '2': ubicar_flota_automatica}
    for clave in ('jugador1', 'jugador2'):
        jugador = estado[clave]
        print(f"--- Flota de {jugador['nombre']} ---")
        if jugador['tipo'] == 'maquina':
            ubicar_flota_automatica(jugador)
        else:
            print('1 - Ubicacion manual\n2 - Ubicacion automatica')
            opcion = leer_opcion('Opcion: ', r'[12]')
            opciones[opcion](jugador)
        jugador['indice_naves'] = radar.crear_indice_naves(jugador['tablero_propio'])
        if jugador['tipo'] == 'humano':
            input('Flota lista. enter para pasar al siguiente jugador: ')
            print('\n' * 40)


def mostrar_cubo(estado):
    """Pide propio o atacado y un plano; muestra el dibujo sin consumir turno"""
    jugador = obtener_jugador_actual(estado)
    print('1 - Cubo propio\n2 - Cubo atacado')
    claves = {'1': 'tablero_propio', '2': 'tablero_atacado'}
    clave = claves[leer_opcion('Opcion: ', r'[12]')]
    eje = leer_opcion('Eje gijo (z/x/y): ', r'[zZxXyY]').lower()
    valor = leer_entero('Valor del plano: ', 1, estado['tamano_cubo'])
    cubo = jugador[clave]
    if clave == 'tablero_propio':
        cubo = [[[celda for celda in fila] for fila in capa] for capa in cubo]
        disparos_rivales = obtener_jugador_rival(estado)['tablero_atacado']
        for z in range(estado['tamano_cubo']):
            for x in range(estado['tamano_cubo']):
                for y in range(estado['tamano_cubo']):
                    marca = disparos_rivales[z][x][y]
                    if marca in (tablero.AGUA_MARCADA, tablero.IMPACTO, tablero.HUNDIDO):
                        cubo[z][x][y] = marca
    print(tablero.dibujar_plano(cubo, eje, valor))


def ejecucion_radar(estado):
    """Pide metodo y letra; muestra puntos y metricas de busqueda sobre el cubo propio"""
    jugador = obtener_jugador_actual(estado)
    print('1 - Busqueda lineal\n2 - Busqueda optimizada')
    metodos = {'1': radar.busqueda_nave_lineal, '2': radar.busqueda_nave_optimizada}
    datos = {'1': jugador['tablero_propio'], '2': jugador['indice_naves']}
    opcion = leer_opcion('Opcion: ', r'[12]')
    letra = leer_opcion('Nave (F/D/S/C/P/E): ', r'[FfDdSsCcPpEe]').upper()
    puntos, metricas = metodos[opcion](datos[opcion], letra)
    print('Celdas de las naves de ese tipo:', puntos)
    print('Metricas:', metricas)


def mostrar_estadisticas(estado):
    """Muestra las estadisticas del historial del estado, sin consumir turno"""
    datos = registro.estadisticas(estado)
    for clave in ('jugador1', 'jugador2'):
        print(estado[clave]['nombre'], datos[clave])


def pedir_disparo(estado):
    """Pide un arma y sus datos y ejecuta la jugada. lanza ErrorJuego si no puede disparar"""
    jugador = obtener_jugador_actual(estado)
    print(armamento.catalogo(jugador['municion']))
    arma = leer_opcion('Arma (T/R/C/S/L): ', r'[TtRrCcSsLl]').upper()
    if not armamento.tiene_municion(arma, jugador['municion']):
        raise TurnoInvalidoError('No queda municion para esa arma')
    jugada = {'arma': arma}
    if arma == 'S':
        jugada['eje'] = leer_opcion('Eje (z/x/y): ', r'[zZxXyY]').lower()
        jugada['valor'] = leer_entero('Valor: ', 1, estado['tamano_cubo'])
    else:
        jugada['objetivo'] = leer_punto(jugador['tablero_atacado'])
        if arma == 'L':
            jugada['eje'] = leer_opcion('Eje del barrido (x/y): ', r'[xXyY]').lower()
    ejecutar_turno(estado, jugada)
    print(estado['historial'][-1]['mensaje'])


def informar_guardado(estado):
    """Informa que guardar y salir corresponde a la siguiente entrega, sin cambiar estado"""
    print('entrega 3')


def jugar_partida(estado):
    """Prepara flotas, alterna turnos hasta la victoria y muestra el resumen final"""
    preparar_flotas(estado)
    if leer_opcion('Iniciar partida? (s/n): ', r'[sSnN]').lower() == 'n':
        return
    acciones={'1':pedir_disparo,'2':mostrar_cubo,'3':informar_guardado,'4':ejecucion_radar,'5':mostrar_estadisticas}
    while not hay_ganador(estado):
        jugador = obtener_jugador_actual(estado)
        print(f"--- Turno de {jugador['nombre']} ---")
        try:
            if jugador['tipo'] == 'maquina':
                turno_maquina(estado)
                print(estado['historial'][-1]['mensaje'])
            else:
                print('1 - Disparar\n2 - Ver el cubo\n3 - Guardar y salir\n4 - Busquedas\n5 - Estadisticas')
                opcion = leer_opcion('Opcion: ', r'[1-5]')
                acciones[opcion](estado)
                if opcion == '1' and not hay_ganador(estado):
                    input('Enter para terminar el turno: ')
                    print('\n' * 40)
        except (tablero.ErrorJuego, ValueError) as error:
            print(error)
    resumen = registro.resumen_partida(estado)
    print(f"Gana {estado[resumen['ganador']]['nombre']}!")
    mostrar_estadisticas(estado)


def comenzar_partida(crear):
    """Pide el tamano del cubo e inicia una partida con la funcion recibida"""
    print('El tamano por defecto es 8. el portaaviones necesita al menos 5')
    tamano = leer_entero('Tamano del cubo (Enter para 8): ', 5, predeterminado=configuracionG['tamano'])
    estado = crear({'tamano': tamano})
    jugar_partida(estado)


def iniciar_1v1():
    """Inicia desde consola una partida de dos humanos"""
    comenzar_partida(nueva_partida_1v1)


def iniciar_vs_maquina():
    """Inicia desde consola una partida contra una maquina de nivel facil"""
    comenzar_partida(nueva_partida_vs_maquina)


def informar_maquinas():
    """Informa el alcance de la partida entre maquinas en esta entrega"""
    print('entrega 3')


def informar_carga():
    """Informa el alcance de la carga de partidas en esta entrega"""
    print('entrega 3')


def salir():
    """Muestra la salida del programa y devuelve 0"""
    print('chauchis')
    return 0


def main():
    """Muestra el menu principal y ejecuta una opcion. Devuelve 0 al salir o 1 para continuar"""
    print('===== OPERACION CUBO =====')
    print('1 - Partida uno contra uno\n2 - Partida uno contra la maquina')
    print('3 - Partida maquina contra maquina\n4 - Continuar una partida guardada\n5 - Salir')
    acciones = {'1': iniciar_1v1, '2': iniciar_vs_maquina, '3': informar_maquinas,
                '4': informar_carga, '5': salir}
    try:
        opcion = leer_opcion('Opcion: ', r'[1-5]')
        resultado = acciones[opcion]()
    except (tablero.ErrorJuego, ValueError) as error:
        print(error)
    else:
        if resultado == 0:
            return 0
    finally:
        print()
    return 1


if __name__ == '__main__':
    try:
        while main():
            pass
    except (EOFError, KeyboardInterrupt):
        print('\nEntrada finalizada. saliendo del juego...')
