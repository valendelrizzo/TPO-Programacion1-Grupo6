# Batalla Naval 3D — «Operación Cubo»

**Trabajo Práctico Integrador · Programación 1 / Algoritmo y Estructura de Datos 1 (UADE)**  
**Grupo 6**

Juego de batalla naval en tres dimensiones por consola desarrollado en Python. El tablero clásico bidimensional se reemplaza por un cubo de N x N x N celdas (representado mediante matrices anidadas), donde cada jugador ubica una flota de naves con reglas espaciales y comportamientos propios, y utiliza un arsenal de armas especiales, radares de búsqueda y mapas de probabilidad para hundir la flota rival.

---

## Tabla de Contenidos
1. [Requisitos e Instalación](#1-requisitos-e-instalación)
2. [Ejecución del Programa y Pruebas](#2-ejecución-del-programa-y-pruebas)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Explicación de los Menús y Flujo de Juego](#4-explicación-de-los-menús-y-flujo-de-juego)
   - [Menú Principal](#41-menú-principal)
   - [Configuración Inicial y Dificultad](#42-configuración-inicial-y-dificultad)
   - [Submenú de Ubicación de la Flota](#43-submenú-de-ubicación-de-la-flota)
   - [Menú de Turno en Partida](#44-menú-de-turno-en-partida)
   - [Guardado y Carga de Partidas](#45-guardado-y-carga-de-partidas)
5. [Referencia Rápida: Coordenadas, Flota y Arsenal](#5-referencia-rápida-coordenadas-flota-y-arsenal)

---

## 1. Requisitos e Instalación

* **Python:** `3.10` o superior.
* **Dependencias:** El juego utiliza exclusivamente la biblioteca estándar de Python (`re`, `json`, `os`, `random`, `time`). Para ejecutar la suite de pruebas unitarias se requiere `pytest`.

### Pasos de instalación

1. Clonar el repositorio y ubicarse en la carpeta raíz del proyecto:
   ```bash
   git clone https://github.com/valendelrizzo/TPO-Programacion1-Grupo6.git
   cd TPO-Programacion1-Grupo6
   ```

2. *(Opcional pero recomendado)* Crear y activar un entorno virtual:
   ```bash
   python3 -m venv .venv
   # En macOS / Linux:
   source .venv/bin/activate
   # En Windows:
   .venv\Scripts\activate
   ```

3. Instalar las dependencias declaradas en `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Ejecución del Programa y Pruebas

### Iniciar el juego
Desde la raíz del proyecto, ejecutar el módulo integrador `src/partida.py`:

```bash
python3 src/partida.py
```
*(En Windows, puede utilizarse `python src/partida.py`).*

### Ejecutar las pruebas unitarias (`pytest`)
Cada módulo del sistema cuenta con su propio archivo de pruebas unitarias en `src/test_*.py`. Para correr todos los tests:

```bash
pytest
```
O especificando el directorio `src`:
```bash
pytest src/
```

---

## 3. Estructura del Proyecto

El sistema sigue una arquitectura modular estricta donde toda la entrada/salida por consola (`input` / `print`) reside en el módulo integrador (`partida.py`), mientras que los cinco módulos de dominio procesan y retornan estructuras de datos:

```text
TPO-Programacion1-Grupo6/
├── README.md                 # Documentación de instalación, ejecución y menús
├── requirements.txt          # Dependencias del proyecto (pytest)
├── docs/
│   └── bitacora.md           # Bitácora del equipo, metodología y trabajo por entrega
├── datos/
│   └── datosGlobales.json    # Archivo JSON autogenerado con las partidas guardadas
└── src/
    ├── tablero.py            # Cubo 3D, validación de coordenadas, rebanadas/planos y dibujo
    ├── flota.py              # Catálogo de naves, reglas de ubicación, impactos y hundimientos
    ├── radar.py              # Búsquedas (lineal, optimizada, recursiva), sonar y mapa de probabilidad
    ├── armamento.py          # Catálogo de armas, despacho por diccionario, efectos y munición
    ├── registro.py           # Historial de jugadas, estadísticas y persistencia en JSON
    ├── partida.py            # Módulo integrador: menús, ciclo de turnos, IA y manejo de errores
    ├── test_tablero.py       # Pruebas unitarias de tablero.py
    ├── test_flota.py         # Pruebas unitarias de flota.py
    ├── test_radar.py         # Pruebas unitarias de radar.py
    ├── test_armamento.py     # Pruebas unitarias de armamento.py
    ├── test_registro.py      # Pruebas unitarias de registro.py
    └── test_partida.py       # Pruebas unitarias de partida.py
```

---

## 4. Explicación de los Menús y Flujo de Juego

Toda la interacción se realiza seleccionando opciones numéricas o ingresando coordenadas validadas mediante expresiones regulares. Ningún dato inválido interrumpe la ejecución: el sistema captura la excepción propia correspondiente, informa el motivo del error y vuelve a solicitar el dato.

### 4.1. Menú Principal
Al iniciar el programa se despliega el menú principal:

```text
===== OPERACION CUBO =====
1 - Partida uno contra uno
2 - Partida uno contra la maquina
3 - Partida maquina contra maquina
4 - Continuar una partida guardada
5 - Salir
Opcion:
```

* **`1 - Partida uno contra uno`:** Inicia una partida local entre dos jugadores humanos (`Jugador 1` vs. `Jugador 2`).
* **`2 - Partida uno contra la maquina`:** Inicia una partida de un jugador humano contra la computadora (`Maquina`), permitiendo elegir su nivel de dificultad.
* **`3 - Partida maquina contra maquina`:** Simula una partida automática completa entre `Maquina 1` y `Maquina 2`, permitiendo configurar la dificultad de cada una por separado.
* **`4 - Continuar una partida guardada`:** Lista todas las partidas almacenadas en `datos/datosGlobales.json` y permite retomar cualquiera desde el turno exacto en que fue guardada.
* **`5 - Salir`:** Finaliza la ejecución del sistema de forma segura.

---

### 4.2. Configuración Inicial y Dificultad
1. **Selección de Dificultad (modos con máquina):**
   Cuando interviene al menos una máquina, el sistema solicita su nivel antes de comenzar:
   ```text
   1 - Facil
   2 - Imposible
   Dificultad:
   ```
   * **Fácil:** La máquina elige objetivos disponibles al azar con las armas que tengan munición.
   * **Imposible:** Si existe un impacto previo sobre una nave rival aún no hundida, rastrea recursivamente sus celdas vecinas para rematarla; en caso contrario, consulta el mapa de probabilidad del radar para atacar la celda con mayor puntaje estratégico.

2. **Tamaño del Cubo:**
   A continuación se solicita la dimensión N del cubo (N x N x N):
   ```text
   El tamano por defecto es 8. el portaaviones necesita al menos 5
   Tamano del cubo (Enter para 8):
   ```
   Presionando `Enter` se utiliza el valor por defecto (`8`). El mínimo permitido es `5` para garantizar que quepa toda la flota.

---

### 4.3. Submenú de Ubicación de la Flota
Antes de comenzar los turnos, cada jugador ubica sus 10 naves. Las flotas de la máquina se ubican siempre de manera automática. Para los jugadores humanos se presenta el siguiente submenú:

```text
--- Flota de Jugador 1 ---
1 - Ubicacion manual
2 - Ubicacion automatica
Opcion:
```

* **`1 - Ubicacion manual`:**
  Muestra en cada paso las naves pendientes de colocar:
  ```text
  Pendientes: F x3  D x2  S x2  C x1  P x1  E x1
  Nave (F/D/S/C/P/E): F
  Desde-hasta (z,x,y-z,x,y): 3,5,4-3,5,5
  Ubicada.
  ```
  * Se ingresa la letra de la nave (`F`, `D`, `S`, `C`, `P`, `E`) y el tramo `z1,x1,y1-z2,x2,y2`.
  * Si el tramo viola alguna regla (fuera de rango, diagonal, tamaño incorrecto, restricción de altura `z`, contacto con bordes o menos de 1 celda de separación —incluyendo diagonales— respecto de otra nave), se informa el error y se vuelve a pedir.
* **`2 - Ubicacion automatica`:**
  Ubica de forma aleatoria e instantánea toda la flota del jugador cumpliendo todas las reglas geométricas y de separación.

Una vez ubicadas ambas flotas, el sistema solicita confirmación para comenzar la batalla:
```text
Iniciar partida? (s/n):
```

---

### 4.4. Menú de Turno en Partida
Durante el turno de un jugador humano se presenta el menú de acciones:

```text
--- Turno de Jugador 1 ---
1 - Disparar
2 - Ver el cubo
3 - Guardar y salir
4 - Busquedas
5 - Estadisticas
6 - Mapa de probabilidad
Opcion:
```

1. **`1 - Disparar` *(consume el turno)*:**
   Muestra el catálogo de armas junto con la munición disponible del jugador y solicita la letra del arma (`T/R/C/S/L/O/G`):
   * Para **Torpedo (`T`)**, **Misil de racimo (`R`)**, **Carga de profundidad (`C`)** y **Onda expansiva (`O`)**: solicita `Objetivo(z,x,y): `.
   * Para **Barrido láser (`L`)**: solicita `Objetivo(z,x,y): ` y luego `Eje del barrido (x/y): `.
   * Para **Sonar (`S`)**: solicita `Eje (z/x/y): ` y `Valor: ` del plano que se desea escanear.
   * Para **Torpedo guiado (`G`)**: no requiere tipear coordenadas; toma automáticamente el último impacto activo sobre una nave rival no hundida y busca recursivamente una celda contigua para impactarla.

2. **`2 - Ver el cubo` *(no consume turno)*:**
   Permite inspeccionar cualquiera de los dos tableros mediante cortes planos en cualquiera de los 3 ejes:
   ```text
   1 - Cubo propio
   2 - Cubo atacado
   Opcion: 1
   Eje fijo (z/x/y): z
   Valor del plano: 3
   ```
   Dibuja en consola la matriz 2D correspondiente al plano elegido con las referencias:
   `~ sin explorar | o agua | X impacto | # hundido | ? detectado` (y las letras de las naves en el cubo propio).

3. **`3 - Guardar y salir`:**
   Permite asignar un nombre a la partida actual (validado con expresiones regulares: letras, números, espacios, guiones o guión bajo) o escribir `CANCELAR` para volver al turno. Al guardar, almacena el estado completo en `datos/datosGlobales.json` y regresa al menú principal.

4. **`4 - Busquedas` *(no consume turno)*:**
   Permite ejecutar y comparar en tiempo real los tres algoritmos de búsqueda de naves sobre el estado actual:
   ```text
   1 - Busqueda lineal
   2 - Busqueda optimizada
   3 - Busqueda recursiva
   Opcion:
   ```
   Muestra si existe un ganador y el diccionario de métricas de rendimiento obtenido: `{'comparaciones': ..., 'tiempo_ms': ..., 'profundidad_max': ...}`.

5. **`5 - Estadisticas` *(no consume turno)*:**
   Muestra el resumen estadístico acumulado de ambos jugadores hasta el momento: turnos jugados, disparos realizados, impactos, tiros al agua, usos de sonar, naves hundidas y porcentaje de precisión (`%`).

6. **`6 - Mapa de probabilidad` *(no consume turno)*:**
   Solicita un eje (`z/x/y`) y un valor de plano (`1` a `N`), calcula la matriz tridimensional de pesos de probabilidad según las naves rivales restantes, impactos activos (`X`) y contactos de sonar (`?`), dibuja el plano numérico en pantalla e informa la coordenada sugerida de mayor probabilidad.

---

### 4.5. Guardado y Carga de Partidas
Al elegir `4 - Continuar una partida guardada` en el Menú Principal:
* El sistema lee `datos/datosGlobales.json` y muestra una lista numerada con los nombres de las partidas guardadas (ej. `1-partida_viernes`).
* Al ingresar el número correspondiente, se restaura íntegramente el estado (tableros, flotas, impactos, municiones, turno actual e historial), removiendo la partida de la lista de pendientes para evitar duplicados, y continúa el ciclo de turnos.

---

## 5. Referencia Rápida: Coordenadas, Flota y Arsenal

### Formato de Coordenadas
* **Orden de ejes:** `z, x, y` (valores enteros de `1` a `N`).
* **Punto individual:** `3,5,4` (`z = 3`, `x = 5`, `y = 4`).
* **Tramo de ubicación:** `3,5,4-3,5,5` (punto inicial y punto final separados por guión `-`).

### Catálogo de la Flota
| Nave | Código | Tamaño | Cant. | Restricción Espacial | Comportamiento Especial |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Fragata** | `F` | 2 celdas | 3 | Sin restricción | — |
| **Destructor** | `D` | 3 celdas | 2 | Sin restricción | Al ser impactado revela una celda ocupada del rival (`?`) |
| **Submarino** | `S` | 3 celdas | 2 | Solo mitad inferior (`z <= N // 2`) | Inmune al Barrido láser (`L`) |
| **Crucero** | `C` | 4 celdas | 1 | No puede ocupar `z = 1` ni `z = N` | — |
| **Portaaviones** | `P` | 5 celdas | 1 | Solo mitad superior (`z > N // 2`) | Cada celda requiere **2 impactos** para destruirse |
| **Estación orbital** | `E` | Bloque `2×2×2` | 1 | No puede tocar ninguna cara exterior del cubo | Al hundirse otorga **+1 de munición** a todas las armas limitadas |

### Catálogo del Arsenal
| Arma | Código | Munición Inicial | Efecto |
| :--- | :---: | :---: | :--- |
| **Torpedo** | `T` | Ilimitada | Ataca únicamente la celda apuntada. |
| **Misil de racimo** | `R` | 3 | Ataca la celda apuntada y sus 6 celdas vecinas ortogonales. |
| **Carga de profundidad** | `C` | 2 | Ataca toda la columna vertical sobre el eje `z` que pasa por el punto apuntado. |
| **Sonar** | `S` | 4 | No produce daño. Escanea un plano completo (`z`, `x` o `y`) y marca como `?` las celdas con naves ocultas. |
| **Barrido láser** | `L` | 2 | Ataca toda la recta sobre el eje `x` o `y` elegida que pasa por el punto apuntado (no afecta submarinos). |
| **Onda expansiva** | `O` | 1 | Se propaga **recursivamente** desde el punto apuntado con radio decreciente atacando el volumen alcanzado. |
| **Torpedo guiado** | `G` | 1 | A partir de un impacto previo sobre una nave no hundida, busca **recursivamente** una celda sana contigua de esa nave y la impacta. |
