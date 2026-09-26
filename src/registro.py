
gPartidaActual={}

def _crear_partida(navesJ1,navesJ2,nombre=""):
  return {
    "nombre":nombre,
    "naves1":navesj1,
    "naves2":navesJ2,
    "movimientos":[],
  }
def _crear_movimiento(arma,celdas):
  return {
    "arma":arma,
    "celdasAfectadas":celdas
  }

def get_estado_actual():
  return gPartidaActual

def registrar_ataque(arma,celdasAfectadas):
  gPartidaActual["movimientos"].append(_crear_movimiento(arma,celdasAfectadas))

def iniciar_partida(navesJ1,navesJ2,nombre=""):
  gPartidaActual=_crear_partida(navesJ1,navesJ2,nombre)
  #...
  return

def terminar_partida(nombre=None):
  if not gPartidaActual or len(gPartidaActual["movimientos"])==0:
    return _crear_partida([],[])
  
  if len(gPartidaActual["nombre"])!=0 or not nombre or len(nombre)==0:
    return gPartidaActual
  
  gPartidaActual["nombre"]=nombre
  return gPartidaActual

# debe devolver "archivo escrito"
def guardar_partida(estado,nombre):
  return 0

# debe devolver "estado, o excepción"
def listar_partidas(nombre):
  return 0

# debe devolver "nombres de las partidas guardadas."
def cargar_partida():
  return 0
