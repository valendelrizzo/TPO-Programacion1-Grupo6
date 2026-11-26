# Bitácora de Trabajo — Grupo 6 («Operación Cubo»)

**Materia:** Programación 1 / Algoritmo y Estructura de Datos 1 (UADE)  
**Trabajo Práctico Integrador:** Batalla Naval 3D — «Operación Cubo»

---

## 1. Integrantes del Equipo

El proyecto fue desarrollado íntegramente por **4 integrantes**:

| Integrante | Usuario de GitHub | Responsabilidad Principal de Módulo |Trabajo Transversal y Conjunto |
| :--- | :--- | :--- | :--- |
| **Valentín Del Rizzo** | `@valendelrizzo` | `flota.py` | `tablero.py`, `partida.py`, integración y decisiones de arquitectura |
| **Santiago de los Ríos** | `@rulo089` | `radar.py` | `tablero.py`, `partida.py`, integración y decisiones de arquitectura |
| **Tobías Bloise** | `@TobiBloisee` | `armamento.py` y suite de tests (`test_*.py`) | `tablero.py`, `partida.py`, integración y decisiones de arquitectura |
| **Héctor Manuel Santarelli** | `@manuelsanta06` | `registro.py` | `tablero.py`, `partida.py`, integración y decisiones de arquitectura |

---

## 2. Metodología de Trabajo y Organización de Git

### División de Módulos y Toma de Decisiones
* **Módulos desarrollados en conjunto (`tablero.py` y `partida.py`):** Dado que `tablero.py` define las estructuras base del cubo tridimensional y las excepciones principales (`ErrorJuego`), y `partida.py` actúa como el módulo integrador de todo el sistema (menús, flujo de turnos, comunicación entre módulos y manejo de entrada/salida), ambos archivos fueron diseñados, programados y mantenidos en conjunto por los 4 integrantes a lo largo de todas las entregas.
* **Módulos de dominio individuales (`flota.py`, `radar.py`, `armamento.py`, `registro.py`):** Cada uno de los cuatro módulos restantes quedó a cargo de un integrante responsable para su implementación puntual. No obstante, **todas las decisiones de diseño, firmas de funciones, estructuras de diccionarios y contratos entre módulos se tomaron en conjunto** durante todo el cuatrimestre.
* **Sesiones colaborativas (VS Code Live Share):** Además del trabajo individual de cada integrante desde su entorno local, el equipo realizó sesiones sincrónicas de programación conjunta mediante **Live Share**, registrando dicha colaboración en el historial de Git mediante commits con múltiples autores (`Co-authored-by`).

### Estrategia de Ramas en Git (Por Entrega)
En lugar de dividir las ramas por módulo o por integrante, el equipo adoptó una **estructura de ramas por etapa/entrega**, lo que permitió que los 4 integrantes trabajaran sobre una base integrada en cada instancia y validaran continuamente la interacción con `tablero.py` y `partida.py`:

* `main`: Rama estable donde se fusionaron las entregas completadas mediante *Pull Requests*.
* `entrega1-dev`: Rama de desarrollo conjunto para la **Entrega 1**.
* `entrega2-dev`: Rama de desarrollo conjunto para la **Entrega 2**.
* `tpo-entrega-3`: Rama de desarrollo conjunto para la **Entrega 3**. Se cambio el nombre para la entrega (de entrega3-dev a tpo-entrega-3)
* `entrega-final-dev`: Rama de desarrollo para la **Entrega Final** (integración final, ajustes de validaciones y suite completa de pruebas unitarias con `pytest`).
* `tpo-entrega-final`: Rama de con la **Entrega Final** (Merge de todos los cambios a esta rama)