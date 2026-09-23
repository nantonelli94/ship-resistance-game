# Game Design Document (GDD) — Ship Resistance Game

**Versión:** 1.0
**Fecha:** 23 de Septiembre de 2026
**Autor:** Proyecto Educativo de Arquitectura Naval

---

## 1. Nombre y Pitch

**Nombre conceptual:** *Ship Resistance Game — Simulador de Resistencia Longitudinal y Prevención de Fallos Estructurales del Buque*

> Ship Resistance Game es un videojuego educativo de simulación náutica que pone al jugador en el rol de un ingeniero naval jefe durante operaciones de carga y descarga. El objetivo es distribuir correctamente la carga y lastre en un buque para mantener los esfuerzos estructurales dentro de los límites de seguridad, previniendo fallos por fluencia del acero, pandeo de estructuras y pérdida de estabilidad, mientras se navega en distintos estados de mar.

---

## 2. Core Loop de Jugabilidad

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE LOOP PRINCIPAL                       │
│                                                              │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│   │  PLANEAR │───▶│ CARGAR   │───▶│ NAVEGAR  │              │
│   │  VIAJE   │    │ /LASTRE  │    │ (mar)    │              │
│   └──────────┘    └──────────┘    └──────────┘              │
│        │               │               │                    │
│        │               ▼               │                    │
│        │          ┌──────────┐         │                    │
│        │          │ CALCULAR │         │                    │
│        │          │  V(x),   │         │                    │
│        │          │  M(x), σ │         │                    │
│        │          └──────────┘         │                    │
│        │               │               │                    │
│        │               ▼               │                    │
│        │          ┌──────────┐         │                    │
│        │          │ ¿ES      │         │                    │
│        │          │ SEGURO?  │         │                    │
│        │          └──────────┘         │                    │
│        │               │               │                    │
│        │         SÍ ◀──┼──▶ NO         │                    │
│        │          │     │     │         │                    │
│        ▼          ▼     │     ▼         │                    │
│   ┌──────────┐  ┌─────┐│┌─────────┐    │                    │
│   │ SIGUIENTE│  │AJUSTA│││ ALERTA  │    │                    │
│   │  VIAJE   │  │CARGA│││ ROJA    │    │                    │
│   └──────────┘  └─────┘│└─────────┘    │                    │
│                        └───────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### Descripción del ciclo:

1. **Planear:** El jugador recibe el manifiesto de carga (tipo de carga, peso, origen/destino) y las condiciones meteorológicas previstas.
2. **Cargar/Lastrar:** Distribuye la carga entre las bodegas y ajusta el lastre en los tanques para mantener el calado y la estabilidad.
3. **Navegar:** El buque sale a mar con un estado de mar asignado que amplifica dinámicamente los momentos flectores.
4. **Calcular:** El motor de física calcula V(x), M(x) y σ(x) en tiempo real (o al pulsar "Simular").
5. **Evaluar:** El sistema compara las tensiones con los límites de seguridad:
   - **Verde (σ < 75% límite):** Operación segura → continuar.
   - **Amarillo (75-100% límite):** Zona de precaución → se recomienda ajustar.
   - **Rojo (σ > límite):** Fluencia inminente → ajuste obligatorio.
6. **Ajustar o Continuar:** Si hay alerta, el jugador redistribuce carga; si no, avanza a la siguiente fase del viaje.

---

## 3. Mecánicas Principales

### 3.1 Gestión de Carga y Lastre

| Mecánica | Descripción |
|----------|-------------|
| **Bodegas de carga** | Compartimentos con capacidad máxima limitada. Peso variable que contribuye a w(x). |
| **Tanques de lastre** | Permiten añadir/eliminar agua para ajustar calado y GM. Afectan tanto a w(x) como a la estabilidad. |
| **Restricciones de compatibilidad** | Ciertos tipos de carga solo pueden ir en bodegas específicas (ej: contenedores pesados bajas, tanques de combustible cambiados de popa). |
| **Tiempo de carga/descarga** | Cada operación consume recursos (dinero/tiempo). Cargar rápido puede generar distribuciones desbalanceadas. |

### 3.2 Cálculo Dinámico de Momentos

```
Peso total:     W = Σ wᵢ(x) · Δx
Empuje total:   B = ∫ b(x) dx  (distribución sobre la eslora)
Carga neta:     q(x) = w(x) − b(x)

Fuerza cortante:  V(x) = −∫ q(x) dx
Momento flector:  M(x) = −∫ V(x) dx

Momento dinámico (efecto de oleaje):
                  M_dinámico(x) = M_estático(x) × F_mar(estado_de_mar)
```

### 3.3 Estados de Mar

| Estado | Descripción | Factor dinámico | Amplitud típica |
|--------|-------------|-----------------|-----------------|
| 0 | Calma | ×1.00 | < 0.5 m |
| 1 | Marejada ligera | ×1.05 | 0.5 – 1.25 m |
| 2 | Marejada moderada | ×1.10 | 1.25 – 2.5 m |
| 3 | Marejada fuerte | ×1.20 | 2.5 – 4.0 m |
| 4 | Mar gruesa | ×1.35 | 4.0 – 6.0 m |
| 5 | Tormenta | ×1.50 | > 6.0 m |

### 3.4 Tensiones Estructurales

**Tensión de flexión longitudinal (viga buque):**

$$\sigma(x) = \frac{M(x) \cdot y}{I_z}$$

Donde:
- $M(x)$ = momento flector en la sección [N·m]
- $y$ = distancia desde el eje neutro al punto de evaluación [m]
- $I_z$ = momento de inercia de la sección transversal alrededor del eje horizontal [m⁴]

**Puntos críticos:**
- **Cubierta superior:** σ_deck = M(x) · y_deck / I_z (tracción cuando M > 0)
- **Quilla inferior:** σ_keel = M(x) · y_keel / I_z (compresión cuando M > 0)

### 3.5 Estabilidad Transversal

$$GM = KB + BM - KG$$

- **KB** ≈ T/2 (aproximación para forma de caja)
- **BM** = I_flota / V
- **KG** depende de la distribución vertical de pesos

---

## 4. Condición de Victoria y Condiciones de Fallo

### 🏆 Victoria
Completar el viaje (o serie de operaciones) manteniendo todas las secciones en **VERDE** durante todo el trayecto, con:
- Tensiones estructurales por debajo del 75% del límite elástico.
- GM > 0.30 m en todo momento.
- Entregando la carga completa en destino.

### ❌ Condiciones de Fallo

| Fallo | Condición | Mecánica de juego |
|-------|-----------|-------------------|
| **Fluencia del acero** | σ_max > σ_yield / FS_yield | La estructura se deforma permanentemente → FIN DEL JUEGO |
| **Pandeo de cubierta** | σ_cubierta > σ_cr_critical | Colapso de la cubierta por compresión → FIN DEL JUEGO |
| **Pandeo de quilla** | σ_quilla > σ_cr_keel | Colapso de la quilla por compresión → FIN DEL JUEGO |
| **Pérdida de estabilidad** | GM < 0.15 m | Vuelco del buque → FIN DEL JUEGO |
| **Rotura longitudinal** | M(x) > M_ultimo | Fallo catastrófico de la viga buque → FIN DEL JUEGO |

**Límites para acero naval AH36:**
- σ_yield = 235 MPa
- FS_yield = 1.5 → σ_admisible = 156.67 MPa
- FS_pandeo = 2.0

---

## 5. Modos de Juego

### 5.1 Tutorial / Puzle 🎓
- **Objetivo:** Aprender los conceptos básicos de resistencia longitudinal.
- **Mecánicas:** Cargas predefinidas, un solo estado de mar, tutorial paso a paso.
- **Ejemplo:** "Coloca 5000 kN en la bodega 3 y verifica que el momento flector en centro no exceda X."
- **Recompensa:** Insignias de conocimiento (ej: "¡Dominás el diagrama de fuerzas cortantes!").

### 5.2 Simulador Realista 🚢
- **Objetivo:** Experimentación libre con un buque configurable.
- **Mecánicas:** Buque parametrizable (eslora, manga, calado, número de secciones), múltiples tipos de carga, estados de mar variables, resultados en tiempo real.
- **Casos:** Diversos escenarios de carga con dificultad progresiva.
- **Estadísticas:** Registro de operaciones seguras vs. fallos, eficiencia de carga, tiempo operativo.

### 5.3 Casos de Estudio Históricos 📚
- **Objetivo:** Aprender de accidentes navales reales reconstruidos.
- **Casos incluidos:**
  - **MV Kurdistan (1979):** Rotura en dos en mar gruesa por concentración de momentos flectores.
  - **SS Edmund Fitzgerald (1975):** Hundimiento en el lago Superior por inundación y pérdida de estabilidad.
  - **MV Prestige (2002):** Rotura estructural por fatiga y mal tiempo.
- **Mecánicas:** Reproducción de las condiciones del caso. El jugador debe identificar qué salió mal y proponer la distribución correcta.

---

## 6. Progresión y Dificultad

| Nivel | Desafío | Concepto enseñado |
|-------|---------|-------------------|
| 1-3 | Carga estática, un solo estado de mar | Distribución de pesos, diagrama V(x) |
| 4-6 | Múltiples bodegas, dos estados de mar | Momento flector, σ = My/I |
| 7-9 | GM variable, compatibilidad de cargas | Estabilidad, altura metacéntrica |
| 10-12 | Tormentas, operaciones secuenciales | Fatiga, acumulación de daño |
| 13-15 | Casos históricos reconstruidos | Análisis de fallos, ingeniería forense |

---

## 7. Plataformas y Controles

- **Plataforma principal:** PC (Windows/Linux/macOS) — prototipo Python + matplotlib.
- **Plataforma futura:** Web (HTML5 Canvas / WebGL) accesible desde navegador.
- **Controles:**
  - Ratón para seleccionar bodegas/tanques y ajustar valores.
  - Teclado para valores numéricos exactos.
  - Zoom en diagramas para inspección detallada.

---

## 8. Estilo Visual y Audio

- **Interfaz:** Tema azul marino profesional, estilo "puente de mando".
- **Colores semafóricos:** Verde (seguro), Amarillo (alerta), Rojo (peligro).
- **Diagramas:** Estilo CAD naval con líneas limpias y anotaciones técnicas.
- **Audio:** Ambiente de mar (oleaje, viento), alertas sonoras para ROJO.

---

*Fin del GDD v1.0*
