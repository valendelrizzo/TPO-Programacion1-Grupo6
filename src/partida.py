import tablero


#debe devovler "estado actualizado"
def ejecutar_turno(estado,jugador):
  return 0

#debe devolver "estado actualizado, jugado por la máquina."
def turno_maquina(estado,jugador):
  return 0

# debe devolver "ganador, o ninguno"
def hay_gandor(estado):
  return False


#debe devolver "estado inicial de una partida de dos jugadores"
def nueva_partida_1v1(confguracion):
  return{
   "tableroPropio1"     :tablero.crear_tablero(confguracion["tamaño"],'o'),
   "tableroAtacado1"    :tablero.crear_tablero(confguracion["tamaño"],'~'),
   "funcionJugador1"    :ejecutar_turno,

   "tableroPropio2"     :tablero.crear_tablero(confguracion["tamaño"],'o'),
   "tableroAtacado2"    :tablero.crear_tablero(confguracion["tamaño"],'~'),
   "funcionJugador2"    :ejecutar_turno,
  }

#debe devolver estado inicial de una partida contra la máquina
def nueva_partida_vs_maquina(confguracion):
  return{
   "tableroPropio1"     :tablero.crear_tablero(confguracion["tamaño"],'o'),
   "tableroAtacado1"    :tablero.crear_tablero(confguracion["tamaño"],'~'),
   "funcionJugador1"    :ejecutar_turno,

   "tableroPropio2"     :tablero.crear_tablero(confguracion["tamaño"],'o'),
   "tableroAtacado2"    :tablero.crear_tablero(confguracion["tamaño"],'~'),
   "funcionJugador2"    :turno_maquina,
  }

#debe devolver "estado inicial de una partida entre dos máquinas"
def nueva_maquina_vs_maquina(confguracion):
  return{
   "tableroPropio1"     :tablero.crear_tablero(confguracion["tamaño"],'o'),
   "tableroAtacado1"    :tablero.crear_tablero(confguracion["tamaño"],'~'),
   "funcionJugador1"    :turno_maquina,

   "tableroPropio2"     :tablero.crear_tablero(confguracion["tamaño"],'o'),
   "tableroAtacado2"    :tablero.crear_tablero(confguracion["tamaño"],'~'),
   "funcionJugador2"    :turno_maquina,
  }



def ubicar_flota():
  return


# EJEMPLOS ESTRUCTURAS
estadoPartida={
 "tableroPropio1"   :[],
 "tableroAtacado1"  :[],
 "ataqueJugador1"   :None,

 "tableroPropio2"   :[],
 "tableroAtacado2"  :[],
 "ataqueJugador2"   :None,
}

configuracionG={
  "tamaño"          :8,
}

def main():
  entrada=-1
  while entrada<1 or entrada>5:
    print("===== OPERACION CUBO =====")
    print("1 - Partida uno contra uno")
    print("2 - Partida uno contra la maquina")
    print("3 - Partida maquina contra maquina")
    print("4 - Continuar una partida guardada")
    print("5 - Salir")
    entrada=int(input("opcion:"))
  estadoPartida={}
  match entrada:
    case 1:
      estadoPartida=nueva_partida_1v1(configuracionG)
    case 2:
      estadoPartida=nueva_partida_vs_maquina(configuracionG)
    case 3:
      estadoPartida=nueva_maquina_vs_maquina(configuracionG)
    case 4:
      #TODO
      return 1
    case 5:
      return 0
  # Loop jugable
  print(estadoPartida)
  return 1

while(main()):
  continue
