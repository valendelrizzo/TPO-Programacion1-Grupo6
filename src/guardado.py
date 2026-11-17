import os
import json

RUTA=os.path.join(os.path.dirname(__file__),"../datos/datosGlobales.json")
fileState=[];
fileStateLoaded=False

def cargarEstadoGlobal():
  global fileStateLoaded
  global fileState
  try:
    # abro el archivo con a+ asi si no existe lo crea
    with open(RUTA,"a+",encoding="utf-8") as archivo:
      archivo.seek(0)
      fileState=json.load(archivo)
  except FileNotFoundError:
    print("error de sistema operativo al leer el archivo")
    exit()
  except json.JSONDecodeError:
    print("error leyendo la informacion global, creando una nueva")
    os.remove(RUTA)
    _guardarPartidaLogica(None)
  except OSError:
    print("error de sistema operativo al leer el archivo, pasate a linux")
    exit()
  except Exception as e:
    print("Ocurrio un error no esperado\n", e)
    exit()
  fileStateLoaded=True

def cargarPartida():
  global fileStateLoaded
  global fileState
  if not fileStateLoaded:
    cargarEstadoGlobal()
  nombres=[f"{i}-{d['nombre']}" for i,d in enumerate(fileState,start=1)]
  cantOpciones=len(nombres)
  nombres='\n'.join(nombres)
  if cantOpciones<1:
    print("\nno hay partidas para cargar")
    return 1
  print(nombres)
  cargar=0
  while True:
    try:
      cargar=int(input("\ningrese la partida que quiere cargar? "))
    except ValueError:
      print("La opcion debe ser un numero")
      print(nombres)
    if cargar>0 and cargar<=cantOpciones:
      break
    print("Opcion invalida")
    print(nombres)
  return fileState.pop(cargar-1)

def guardarPartida(estado):
  """Guarda el estado recibido como una partida y pide un nombre para identificarla
  REBIENTA TOTALMETE EL PROCESO SIN PASAR POR MENUS O CHEQUEOS"""
  nombre=input("Ingrese el nombre con el que guardar la partida o CANCELAR:\n")
  if nombre=="CANCELAR":
    return 0
  _guardarPartidaLogica({"nombre":nombre,"partida":estado})
  exit()
  return 0

def _guardarPartidaLogica(partida):
  """guarda el estado pasado, si recibe `None` crea el archivo con una lista vacia"""
  global fileState
  fileState.append(partida)
  with open(RUTA,"w",encoding="utf-8") as archivo:
    json.dump([] if fileState==None else fileState,archivo,
              ensure_ascii=True,separators=(',', ':'))
    pass
