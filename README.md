# 🚢 Ship Resistance Game

**Simulador Educativo de Resistencia Longitudinal del Buque y Prevención de Fallos Estructurales**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0-green.svg)]()
[![Status](https://img.shields.io/badge/Status-Prototype-orange.svg)]()

> Juego educativo de simulación náutica para aprender resistencia longitudinal de la viga buque, prevención de fallos por fluencia/pandeo, y gestión de estabilidad durante operaciones de carga y descarga.

---

## 📖 Descripción

**Ship Resistance Game** es un videojuego educativo y de simulación sobre la resistencia longitudinal de la viga buque y prevención de fallos por fluencia/pandeo durante operaciones de carga y descarga.

El jugador asume el rol de ingeniero naval jefe y debe:
- Distribuir correctamente la carga entre las bodegas
- Ajustar el lastre para mantener la estabilidad
- Mantener los esfuerzos estructurales dentro de límites seguros
- Navegar en distintos estados de mar sin comprometer la integridad del buque

### Características Principales

- ✅ **Cálculo dinámico** de fuerza cortante V(x) y momento flector M(x)
- ✅ **Tensiones de flexión** σ = M·y/I_z en cubierta y quilla
- ✅ **Sistema de alertas** semafórico (Verde/Amarillo/Rojo)
- ✅ **Estabilidad transversal** con cálculo de GM
- ✅ **Estados de mar** con amplificación dinámica de momentos
- ✅ **Visualización gráfica** de diagramas de esfuerzo
- ✅ **Modos de juego**: Tutorial, Simulador Realista, Casos Históricos

---

## 🎮 Modos de Juego

| Modo | Descripción | Objetivo |
|------|-------------|----------|
| **Tutorial / Puzle** | Aprendizaje guiado paso a paso | Dominar V(x), M(x), σ(x) |
| **Simulador Realista** | Experimentación libre | Operaciones seguras eficientes |
| **Casos Históricos** | Reconstrucción de accidentes | Aprender de errores reales |

---

## 📋 Requisitos

- **Python:** 3.8 o superior
- **pip:** gestor de paquetes de Python
- **matplotlib:** para visualización gráfica (opcional pero recomendado)
- **numpy:** dependencia de matplotlib

### Sistema Operativo
- Windows 10/11 ✅
- macOS 10.15+ ✅
- Linux (Ubuntu 20.04+) ✅

---

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/nantonelli94/ship-resistance-game.git
cd ship-resistance-game
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias:**
```
matplotlib>=3.5.0
numpy>=1.21.0
```

### 4. Ejecutar el simulador

```bash
python prototypes/ship_simulator.py
```

---

## 🚀 Uso Rápido

### Simulador CLI (Interfaz de Línea de Comandos)

```bash
$ python prototypes/ship_simulator.py

======================================================================
  SHIP RESISTANCE GAME v1.0
  Simulador Educativo de Resistencia Longitudinal del Buque
======================================================================

  Buque: MV Containership-200
  Eslota: 200 m | Manga: 32 m | Calado: 10 m
  Desplazamiento: 441.0 MN

----------------------------------------
  MENÚ PRINCIPAL
----------------------------------------
  1. Ver configuración del buque
  2. Modificar carga por sección
  3. Modificar lastre
  4. Ejecutar simulación
  5. Cambiar estado de mar
  6. Restablecer cargas
  0. Salir

  Opción: 4

======================================================================
  ESTADO GENERAL: VERDE
======================================================================

  Tensiones máximas:
    Posición: 100.0 m desde proa
    Valor:    125.50 MPa
    Límite:   156.67 MPa
    Factor de seguridad: 1.88

  Balance de fuerzas:
    Peso total:  430500.0 kN
    Empuje:       430500.0 kN
    Diferencia:   0.0 kN

  Estabilidad:
    GM estimado: 0.452 m
```

### API de Python

```python
from src.core.physics_engine import PhysicsEngine
from src.models.ship_config import ShipConfig

# Crear configuración del buque
ship = ShipConfig(
    name="Mi Buque",
    length_overall=200.0,
    beam=32.0,
    depth=18.0,
    draft_design=10.0,
    displacement=45_000_000.0,
    moment_of_inertia_zz=12.5,
    y_deck=8.5,
    y_keel=-9.0,
)

# Añadir secciones...

# Crear motor de física
engine = PhysicsEngine(ship)

# Ejecutar simulación
result = engine.compute_shear_and_moment()

print(f"Estado: {result.status}")
print(f"Tensión máxima: {result.max_stress/1e6:.1f} MPa")
print(f"GM: {result.gm_estimate:.3f} m")
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [GAME_DESIGN_DOCUMENT.md](docs/GAME_DESIGN_DOCUMENT.md) | Diseño del juego: mecánicas, modos, progresión |
| [MATHEMATICAL_MODEL.md](docs/MATHEMATICAL_MODEL.md) | Modelo matemático y física implementada |
| [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | Arquitectura del sistema y módulos |

---

## 🧪 Tests

Ejecutar pruebas unitarias:

```bash
python -m pytest tests/ -v
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. **Fork** el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. **Commit** tus cambios (`git commit -am 'Añade nueva característica'`)
4. **Push** a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un **Pull Request**

### Guía de Estilo

- Código en **PEP 8** (Python)
- Comentarios en español o inglés
- Docstrings en formato Google
- Tests obligatorios para nuevas funcionalidades

---

## 📁 Estructura del Proyecto

```
ship-resistance-game/
├── docs/                        # Documentación
│   ├── GAME_DESIGN_DOCUMENT.md
│   ├── MATHEMATICAL_MODEL.md
│   └── SYSTEM_ARCHITECTURE.md
├── src/                         # Código fuente
│   ├── core/                    # Motor de simulación
│   ├── models/                  # Modelos de datos
│   ├── ui/                      # Interfaz de usuario
│   ├── modes/                   # Modos de juego
│   ├── data/                    # Datos y presets
│   └── utils/                   # Utilidades
├── prototypes/                  # Prototipos ejecutables
│   └── ship_simulator.py
├── tests/                       # Pruebas unitarias
├── assets/                      # Recursos gráficos
├── requirements.txt             # Dependencias
├── .gitignore
└── README.md
```

---

## 📝 Licencia

Este proyecto está licenciado bajo **MIT License** — ver [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Nicolás Antonelli**
- GitHub: [@nantonelli94](https://github.com/nantonelli94)
- Arquitectura Naval — Teoría del Buque II

---

## 🙏 Agradecimientos

- Basado en los fundamentos de **Teoría del Buque II: Propulsión**
- Referencias: ITTC, Lloyd's Register, OMI/IMO
- A la comunidad de arquitectura naval por el conocimiento compartido

---

<div align="center">

⚓ **¡Buena navegación, ingeniero!** ⚓

</div>
