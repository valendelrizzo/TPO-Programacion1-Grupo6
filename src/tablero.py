
AGUA_SIN_EXPLORAR   ='~'
NAVE_OCULTA         ='N'
AGUA_MARCADA        ='o'
IMPACTO             ='X'
HUNDIDO             ='#'
DETECTADO           ='?'


class ErrorJuego(Exception):
  """Base de las excepciones propias del juego."""
  pass


class ErrorTablero(ErrorJuego):
  """Punto,plano o tamano de tablero invalido."""
  pass


def validar_plano(mapa,eje,indice):
  """Recibe cubo,eje e indice desde 0. Lanza ErrorTablero si no existe."""
  if eje not in('z','x','y'):
    raise ErrorTablero('El eje debe ser z,x o y.')
  if type(indice)!=int or not 0<=indice<len(mapa):
    raise ErrorTablero('El plano queda fuera del cubo.')


def obtener_rebanada(mapa,eje,indice):
  """Devuelve una copia del plano. El indice parte de 0;lanza ErrorTablero."""
  validar_plano(mapa,eje,indice)
  if eje=='z':
    return [[y for y in x]for x in mapa[indice]]
  elif eje=='x':
    return [[y for y in mapa[z][indice]]for z in range(len(mapa))]
  elif eje=='y':
    return [[mapa[z][x][indice]for x in range(len(mapa[0]))]for z in range(len(mapa))]

def aplicar_rebanada(mapa,rebanada,eje,indice):
  """Escribe un plano con indice desde 0. Lanza ErrorTablero si no es valido."""
  validar_plano(mapa,eje,indice)
  if len(rebanada)!=len(mapa):
    raise ErrorTablero('La rebanada debe tener el tamano del cubo.')
  for fila in rebanada:
    if len(fila)!=len(mapa):
      raise ErrorTablero('La rebanada debe ser cuadrada.')
  if eje=='z':
    for x in range(len(rebanada)):
      for y in range(len(rebanada[0])):
        mapa[indice][x][y]=rebanada[x][y]
  elif eje=='x':
    for z in range(len(rebanada)):
      for y in range(len(rebanada[0])):
        mapa[z][indice][y]=rebanada[z][y]
  elif eje=='y':
    for z in range(len(rebanada)):
      for x in range(len(rebanada[0])):
        mapa[z][x][indice]=rebanada[z][x]

def crear_tablero(tamano=8,char=AGUA_SIN_EXPLORAR):
  """Devuelve un cubo independiente de listas. Lanza ErrorTablero si tamano no es positivo."""
  if type(tamano)!=int or tamano<1:
    raise ErrorTablero('El tamano debe ser un entero positivo.')
  return [[[char for _ in range(tamano)]for _ in range(tamano)]for _ in range(tamano)]


def validar_punto(cubo,punto):
  """Devuelve si el punto(z,x,y)tiene enteros entre 1 y N. No lanza excepciones."""
  if not isinstance(punto,(tuple,list))or len(punto)!=3:
    return False
  for valor in punto:
    if type(valor)!=int or not 1<=valor<=len(cubo):
      return False
  return True


def leer_celda(cubo,punto):
  """Devuelve el contenido de un punto desde 1. Lanza ErrorTablero si queda fuera."""
  if not validar_punto(cubo,punto):
    raise ErrorTablero('El punto debe estar entre 1 y el tamano del cubo.')
  z,x,y=punto
  return cubo[z-1][x-1][y-1]


def escribir_celda(cubo,punto,valor):
  """Escribe un valor y devuelve el cubo. Lanza ErrorTablero si el punto no existe."""
  leer_celda(cubo,punto)
  z,x,y=punto
  cubo[z-1][x-1][y-1]=valor
  return cubo


def vecinos(cubo,punto):
  """Devuelve hasta seis vecinos ortogonales desde 1. Lanza ErrorTablero si no existe."""
  leer_celda(cubo,punto)
  z,x,y=punto
  candidatos=[(z+1,x,y),(z-1,x,y),(z,x+1,y),
(z,x-1,y),(z,x,y+1),(z,x,y-1)]
  resultado=[]
  for candidato in candidatos:
    if validar_punto(cubo,candidato):
      resultado.append(candidato)
  return resultado


def dibujar_plano(cubo,eje,valor,ocultar_naves=False):
  """Devuelve el dibujo de un plano con valor desde 1. Lanza ErrorTablero si no existe."""
  if type(valor)!=int:
    raise ErrorTablero('El valor del plano debe ser entero.')
  plano=obtener_rebanada(cubo,eje,valor-1)
  ejes={'z':('x','y'),'x':('y','z'),'y':('x','z')}
  columnas,filas=ejes[eje]
  lineas=[f'=========PLANO {eje}={valor}=========']
  encabezado='    '
  for i in range(len(cubo)):
    encabezado+=f'{columnas}{i+1:<3}'
  lineas.append(encabezado)
  for fila in range(len(cubo)):
    texto=f'{filas}{fila+1:<3}'
    for columna in range(len(cubo)):
      if eje=='z':
        celda=plano[columna][fila]
      else:
        celda=plano[fila][columna]
      if ocultar_naves and celda in('F','D','S','C','P','E',NAVE_OCULTA):
        celda=AGUA_SIN_EXPLORAR
      texto+=f'{celda:<4}'
    lineas.append(texto)
  lineas.append('~ sin explorar | o agua | X impacto | # hundido | ? detectado')
  return '\n'.join(lineas)
