# Arquitectura del Sistema — Ship Resistance Game

**Versión:** 1.0
**Fecha:** 23 de Septiembre de 2026

---

## 1. Diagrama de Módulos

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SHIP RESISTANCE GAME — ARQUITECTURA              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │   CAPA DE       │  │   CAPA DE       │  │   CAPA DE           │  │
│  │   PRESENTACIÓN  │  │   LÓGICA        │  │   DATOS             │  │
│  │   (UI/UX)       │  │   (Motor)       │  │   (Configuración)   │  │
│  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘  │
│           │                    │                       │             │
│           ▼                    ▼                       ▼             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    NÚCLEO DE SIMULACIÓN                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │    │
│  │  │ PhysicsEngine│  │ LoadManager  │  │ StabilityChecker │  │    │
│  │  │              │  │              │  │                  │  │    │
│  │  │ - V(x)       │  │ - Bodegas    │  │ - GM             │  │    │
│  │  │ - M(x)       │  │ - Tanques    │  │ - Curva GZ       │  │    │
│  │  │ - σ(x)       │  │ - Compatibil.│  │ - Área bajo curva│  │    │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │    │
│  │         │                  │                    │            │    │
│  │  ┌──────┴──────────────────┴────────────────────┴─────────┐  │    │
│  │  │              Sistema de Alertas (AlertSystem)           │  │    │
│  │  │  ┌─────────┐  ┌──────────────┐  ┌───────────────────┐  │  │    │
│  │  │  │ Semáforo│  │ Generador    │  │ Registro de       │  │  │    │
│  │  │  │ V/A/R   │  │ de Alertas   │  │ Incidentes        │  │  │    │
│  │  │  └─────────┘  └──────────────┘  └───────────────────┘  │  │    │
│  │  └────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    MODO DE JUEGO                             │    │
│  │  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐  │    │
│  │  │ Tutorial │  │  Simulador   │  │ Casos Históricos     │  │    │
│  │  │ /Puzle   │  │  Realista    │  │ (Kurdistan, etc.)    │  │    │
│  │  └──────────┘  └──────────────┘  └──────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Estructura de Módulos de Código

```
src/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── physics_engine.py      # Cálculo V(x), M(x), σ(x)
│   ├── load_manager.py        # Gestión de carga y lastre
│   ├── stability_checker.py   # Cálculo de GM y estabilidad
│   └── alert_system.py        # Sistema de alertas semafórico
├── models/
│   ├── __init__.py
│   ├── ship_config.py         # Dataclasses de configuración
│   ├── section.py             # Sección del buque
│   └── simulation_result.py   # Resultados de simulación
├── ui/
│   ├── __init__.py
│   ├── cli.py                 # Interfaz de línea de comandos
│   ├── plotter.py             # Renderizado de diagramas (matplotlib)
│   └── colors.py              # Paleta de colores semafórica
├── modes/
│   ├── __init__.py
│   ├── tutorial.py            # Modo tutorial/puzle
│   ├── simulator.py           # Modo simulador realista
│   └── historical_cases.py    # Casos de estudio históricos
├── data/
│   ├── __init__.py
│   ├── ship_presets.py        # Presets de buques predefinidos
│   └── historical_scenarios.py # Datos de casos históricos
└── utils/
    ├── __init__.py
    ├── constants.py           # Constantes físicas y materiales
    └── validators.py          # Validadores de entrada
```

---

## 3. Responsabilidades por Módulo

### 3.1 `core/physics_engine.py` — Motor de Física

| Método | Responsabilidad |
|--------|-----------------|
| `compute_load_distribution()` | Calcula w(x) − b(x) por sección |
| `compute_shear_and_moment()` | Integra para obtener V(x) y M(x) |
| `compute_stress()` | Aplica σ = M·y/I_z |
| `apply_sea_state()` | Amplifica momentos según estado de mar |
| `_estimate_gm()` | Calcula altura metacéntrica |

### 3.2 `core/load_manager.py` — Gestor de Carga

| Método | Responsabilidad |
|--------|-----------------|
| `set_load(section, value)` | Asigna carga con validación de capacidad |
| `set_ballast(section, value)` | Ajusta lastre |
| `get_total_weight()` | Peso total del buque |
| `check_compatibility()` | Verifica restricciones de carga |
| `get_center_of_gravity()` | Calculo de KG y posición longitudinal de CG |

### 3.3 `core/stability_checker.py` — Verificador de Estabilidad

| Método | Responsabilidad |
|--------|-----------------|
| `compute_gm()` | Altura metacéntrica |
| `compute_gz_arm()` | Curva de brazos de adrizamiento |
| `check_criteria()` | Verifica criterios de estabilidad (OMI/IMO) |
| `get_stability_status()` | Devuelve VERDE/AMARILLO/ROJO |

### 3.4 `core/alert_system.py` — Sistema de Alertas

| Método | Responsabilidad |
|--------|-----------------|
| `evaluate_stress()` | Compara σ con límites |
| `evaluate_buckling()` | Verifica pandeo |
| `evaluate_stability()` | Verifica GM |
| `get_status()` | Devuelve estado global |
| `generate_warnings()` | Lista de alertas activas |

---

## 4. Layout Visual de la Interfaz (UI/UX)

### 4.1 Esquema de Pantalla Principal

```
┌─────────────────────────────────────────────────────────────────────┐
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PANEL SUPERIOR                             │   │
│  │  Buque: MV Containership-200  |  Estado: ● VERDE            │   │
│  │  Eslota: 200m  |  GM: 0.45 m  |  F.S.: 2.8                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────┐  ┌───────────────────────────────┐   │
│  │   PANEL DE SECCIONES     │  │   DIAGRAMAS                  │   │
│  │                          │  │                               │   │
│  │  [Bodega 1]  5000 kN     │  │   V(x) [kN]                   │   │
│  │  [Bodega 2]  8000 kN     │  │   ┌───────────────────────┐   │   │
│  │  [Tanque 1]  2000 kN     │  │   │    ╱╲    ╱╲            │   │   │
│  │  [Bodega 3] 12000 kN     │  │   │   ╱  ╲  ╱  ╲           │   │   │
│  │  ...                     │  │   │  ╱    ╲╱    ╲          │   │   │
│  │                          │  │   └───────────────────────┘   │   │
│  │  [Modificar Carga]       │  │                               │   │
│  │  [Modificar Lastre]     │  │   M(x) [MN·m]                  │   │
│  │                          │  │   ┌───────────────────────┐   │   │
│  │                          │  │   │  ╱‾‾‾‾╲     ╱‾‾‾‾╲   │   │   │
│  │                          │  │   │ ╱      ╲   ╱      ╲   │   │   │
│  │                          │  │   │╱        ╲_╱        ╲  │   │   │
│  │                          │  │   └───────────────────────┘   │   │
│  └──────────────────────────┘  │                               │   │
│                                │   σ(x) [MPa]                   │   │
│  ┌──────────────────────────┐  │   ┌───────────────────────┐   │   │
│  │   PANEL DE CONTROL       │  │   │  ZONA VERDE  (<117)   │   │   │
│  │                          │  │   │  ZONA AMARILLA        │   │   │
│  │  Estado de mar: [▼ 2]    │  │   │    (117-157)          │   │   │
│  │  [Ejecutar Simulación]   │  │   │  ZONA ROJA    (>157)  │   │   │
│  │  [Restablecer]           │  │   │         ___           │   │   │
│  │  [Cargar Escenario]      │  │   │        /   \  Límite  │   │   │
│  │                          │  │   │       /     \  157    │   │   │
│  │  ⚠ Alertas:              │  │   │      /       \        │   │   │
│  │  ──────────────────────  │  │   └───────────────────────┘   │   │
│  │  Sin alertas activas     │  │                               │   │
│  └──────────────────────────┘  └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Zonas de Color Semafórico

| Color | Rango de σ | Significado | Acción del Jugador |
|-------|-----------|------------|-------------------|
| 🟢 **Verde** | σ < 75% σ_admisible | Operación segura | Continuar |
| 🟡 **Amarillo** | 75% ≤ σ < 100% σ_admisible | Precaución | Se recomienda ajustar |
| 🔴 **Rojo** | σ ≥ σ_admisible | Peligro de fluencia | Ajuste obligatorio |

### 4.3 Diagramas de Esfuerzo

**Diagrama de Fuerza Cortante V(x):**
- Eje Y: V(x) en kN
- Eje X: posición longitudinal en m
- Curva azul con relleno
- Línea de referencia en V=0

**Diagrama de Momento Flector M(x):**
- Eje Y: M(x) en MN·m
- Eje X: posición longitudinal en m
- Curva roja con relleno
- Máximos/mínimos marcados con puntos

**Diagrama de Tensiones σ(x):**
- Eje Y: σ en MPa
- Eje X: posición longitudinal en m
- Dos curvas: cubierta (verde) y quilla (magenta)
- Bandas de color: verde (0-75%), amarillo (75-100%), rojo (>100%)
- Línea discontinua horizontal en σ_admisible

---

## 5. Flujo de Datos

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Usuario     │────▶│  LoadManager │────▶│  ShipConfig  │
│  (input)     │     │  (validación)│     │  (estado)    │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                               │
                                               ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  AlertSystem │◀────│ PhysicsEngine│◀────│ ShipConfig   │
│  (semáforo)  │     │ (cálculos)   │     │              │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│  Plotter     │────▶│  Usuario     │
│  (gráficos)  │     │  (decisión)  │
└──────────────┘     └──────────────┘
```

---

## 6. Decisiones Técnicas

| Decisión | Justificación |
|----------|---------------|
| **Python como lenguaje principal** | Amplio ecosistema científico (numpy, matplotlib), ideal para simulación y educación. |
| **Dataclasses para configuración** | Sintaxis limpia, type hints, inmutabilidad parcial. |
| **Integración numérica por trapecio** | Simple, suficiente para N=10 secciones, fácil de depurar. |
| **matplotlib para visualización** | Estándar de facto en Python, exportable a PNG/SVG/PDF. |
| **Sin framework de juego (pygame) en v1** | El prototipo es educativo; la UI es CLI + gráficos estáticos. |
| **Patrón Strategy para modos de juego** | Permite añadir nuevos modos (tutorial, simulador, casos) sin modificar el núcleo. |

---

## 7. Extensiones Futuras

| Versión | Característica |
|---------|----------------|
| **v1.1** | Interfaz gráfica con tkinter/PyQt |
| **v1.2** | Web app con Flask/FastAPI + HTML5 Canvas |
| **v2.0** | Motor de física 3D con cálculo de secciones reales |
| **v2.1** | Multijugador (competencia de eficiencia de carga) |
| **v3.0** | Realidad virtual (VR) para inspección del buque |

---

*Fin de la Arquitectura v1.0*
