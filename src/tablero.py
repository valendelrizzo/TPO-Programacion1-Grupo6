
def obtener_rebanada(mapa,eje,indice):
  if eje=='z':
    return [[y for y in x]for x in mapa[indice]]
  elif eje=='x':
    return [[y for y in mapa[z][indice]]for z in range(len(mapa))]
  elif eje=='y':
    return [[mapa[z][x][indice]for x in range(len(mapa[0]))]for z in range(len(mapa))]

def aplicar_rebanada(mapa,rebanada,eje,indice):
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


========= CAPA y = 3 =========
x1 x2 x3 x4 x5 x6 x7 x8
z1 ~ ~ ~ ~ P ~ ~ ~
z2 ~ ~ X ~ ~ ~ ~ ~
z3 ~ ~ X ~ o ~ ~ ~
z4 ~ ~ ~ ~ ~ ~ ? ~


def crear_tablero(tamano,char):
  return [[[char for _ in range(tamano)]for _ in range(tamano)]for _ in range(tamano)]
