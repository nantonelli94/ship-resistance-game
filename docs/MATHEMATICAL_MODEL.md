# Modelo Matemático y Física del Juego

**Versión:** 1.0
**Asignatura:** Teoría del Buque II — Propulsión y Resistencia Estructural

---

## 1. Fundamentos de la Viga Buque

El buque se modela como una **viga flotante** sometida a una distribución de cargas longitudinales. La diferencia entre el peso w(x) y el empuje b(x) genera las fuerzas internas que la estructura debe resistir.

### Convención de signos

| Magnitud | Positivo | Negativo |
|----------|----------|----------|
| Momento flector M(x) | Sag moment (hogging) | Hog moment (sagging) |
| Fuerza cortante V(x) | Subiendo | Bajando |
| Tensión σ | Tracción | Compresión |

---

## 2. Distribución de Pesos w(x)

El peso por unidad de longitud en la posición x es la contribución de:

$$w(x) = w_{\text{estructura}}(x) + w_{\text{carga}}(x) + w_{\text{lastre}}(x) + w_{\text{equipos}}(x)$$

En el simulador, se discretiza en N secciones de longitud Δx:

$$w_i = \frac{W_{\text{estructura},i} + W_{\text{carga},i} + W_{\text{lastre},i}}{\Delta x}$$

### 2.1 Peso de la estructura

Modelado como línea base uniforme o con variación según la zona:
- **Proa:** Estructura reforzada (mayor peso/m).
- **Centro:** Peso mínimo por sección.
- **Popa:** Maquinaria concentrada (alto peso/m en zona de motor).

### 2.2 Peso de la carga

Distribución definida por el jugador dentro de límites físicos de cada bodega:

$$W_{\text{carga},i} \in [0, \, W_{\text{máxima},i}]$$

### 2.3 Peso del lastre

Tanques de lastre a mitad de eslora:

$$W_{\text{lastre},i} = \rho_{\text{agua}} \cdot g \cdot V_{\text{lastre},i}$$

---

## 3. Distribución de Empuje b(x)

El empuje sigue la forma de la carena sumergida. Para una **aproximación de caja**:

$$b(x) = \rho_{\text{agua}} \cdot g \cdot B(x) \cdot T(x)$$

### 3.1 Distribución trapezoidal simplificada

En el juego se usa una distribución trapezoidal:

$$b_i = \begin{cases}
0.2 \cdot B_{\text{total}} / N & \text{extremos (proa/popa)} \\
0.6 \cdot B_{\text{total}} / (N-2) & \text{centro}
\end{cases}$$

### 3.2 Efecto del oleaje (estado de mar)

En mar de oleaje, el calado varía longitudinalmente. El **momento de torsión de ola** se aproxima:

$$M_{\text{ola}} \approx \frac{\Delta \cdot L_{BP}}{12} \cdot C_{\text{ola}} \cdot F_{\text{mar}}$$

Donde:
- Δ = desplazamiento
- LBP = longitud entre perpendiculares
- C_ola ≈ 0.03 – 0.06 (coeficiente según estado de mar)
- F_mar = factor de amplificación (ver tabla en GDD)

---

## 4. Fuerza Cortante V(x)

### 4.1 Definición integral

$$V(x) = -\int_{0}^{x} [w(\xi) - b(\xi)] \, d\xi + V(0)$$

### 4.2 Forma discreta (método del trapecio)

$$V_i = V_{i-1} - (w_i - b_i) \cdot \Delta x$$

Con condición de frontera:
$$V(0) = -\frac{1}{2}(w_1 - b_1) \cdot \Delta x$$

### 4.3 Interpretación física

- **V(x) > 0:** La sección x está soportando más peso que empuje a estribor (o proa).
- **V(x) < 0:** El empuje domina sobre el peso.
- **V(x) = 0:** Puntos de inflexión del momento flector (máximos/mínimos de M).

---

## 5. Momento Flector M(x)

### 5.1 Definición integral

$$M(x) = -\int_{0}^{x} V(\xi) \, d\xi + M(0)$$

### 5.2 Forma discreta

$$M_i = M_{i-1} + V_i \cdot \Delta x$$

Con condición de frontera (buque libre, sin apoyos):
$$M(0) = M(L) = 0$$

### 5.3 Corrección de frontera

En la práctica, la integración numérica acumula error. Se aplica corrección lineal:

$$M_i^{\text{corregido}} = M_i - \frac{i}{N} \cdot M_N$$

### 5.4 Valores típicos (buque real)

| Tipo de buque | M_hogging | M_sagging |
|---------------|-----------|-----------|
| Portacontenedores 200m | 150 MN·m | 120 MN·m |
| Granelero 250m | 300 MN·m | 250 MN·m |
| Petrolero VLCC 330m | 800 MN·m | 600 MN·m |

---

## 6. Tensión de Flexión σ(x)

### 6.1 Fórmula fundamental (Teoría de Euler-Bernoulli)

$$\sigma(x, y) = \frac{M(x) \cdot y}{I_z}$$

Donde:
- **M(x):** Momento flector en la sección [N·m]
- **y:** Distancia desde el eje neutro [m]
- **I_z:** Momento de inercia de la sección transversal alrededor del eje horizontal neutro [m⁴]

### 6.2 Puntos críticos

**Cubierta superior (y = +y_deck):**
$$\sigma_{\text{deck}} = \frac{M(x) \cdot y_{\text{deck}}}{I_z}$$

**Quilla inferior (y = −y_keel):**
$$\sigma_{\text{keel}} = \frac{M(x) \cdot y_{\text{keel}}}{I_z}$$

### 6.3 Momento de inercia I_z

Para una sección tipo caja (simplificación del buque real):

$$I_z \approx \frac{B \cdot D^3}{12} - \frac{(B - 2t) \cdot (D - 2t)^3}{12}$$

Donde:
- B = manga del buque
- D = puntal (profundidad)
- t = espesor estructural

En el juego, I_z es un parámetro configurable.

### 6.4 Distribución de tensiones en la sección

```
        Cubierta (y = +y_deck)
    ←────── Compresión (M > 0) ──────→
    ┌─────────────────────────────────┐
    │                                 │
    │      σ = M·y / I_z              │
    │                                 │
    │    ● Eje neutro (y = 0)         │
    │      σ = 0                      │
    │                                 │
    │                                 │
    └─────────────────────────────────┘
        Quilla (y = −y_keel)
    ←────── Tracción (M > 0) ────────→
```

---

## 7. Límite Elástico y Deformación Plástica

### 7.1 Criterio de fluencia (von Mises simplificado)

Para el caso uniaxial de la viga buque:

$$\sigma_{\text{von Mises}} = |\sigma(x)| \leq \frac{\sigma_{\text{yield}}}{FS_{\text{yield}}}$$

### 7.2 Parámetros del acero naval

| Propiedad | Valor | Unidad |
|-----------|-------|--------|
| Módulo de Young (E) | 200 | GPa |
| Límite elástico (σ_y) | 235 | MPa (AH36) |
| Resistencia última (σ_u) | 490 | MPa |
| Densidad (ρ) | 7850 | kg/m³ |
| Coeficiente de Poisson (ν) | 0.30 | — |

### 7.3 Curva tensión-deformación

```
 σ (MPa)
   │
490├─────────────────────● Resistencia última
   │                   ╱
   │                 ╱
235├───────────────●─── Límite elástico (fluencia)
   │             ╱ │
   │           ╱   │ Zona plástica
   │         ╱     │
   │       ╱       │
  0├──────╱────────┴────── ε
   0     ε_y     ε_u
```

Donde:
- ε_y = σ_y / E = 235e6 / 200e9 ≈ 0.001175 (0.12%)
- Zona elástica: deformación recuperable
- Zona plástica: deformación permanente

### 7.4 Transición elástico-plástica en el juego

```python
if sigma_max > STEEL_YIELD_STRESS / SAFETY_FACTOR_YIELD:
    # Estado ROJO: fluencia
    status = "ROJO"
    deformacion_permanente = True
elif sigma_max > STEEL_YIELD_STRESS / SAFETY_FACTOR_YIELD * 0.75:
    # Estado AMARILLO: zona elástica pero cerca del límite
    status = "AMARILLO"
else:
    # Estado VERDE: operación segura
    status = "VERDE"
```

---

## 8. Pandeo de Estructuras

### 8.1 Pandeo de placa de cubierta (compresión longitudinal)

La tensión crítica de pandeo para una placa simplemente apoyada:

$$\sigma_{\text{cr}} = k \cdot \frac{\pi^2 \cdot E}{12(1 - \nu^2)} \cdot \left(\frac{t}{b}\right)^2$$

Donde:
- k = coeficiente de apoyo (≈ 4 para placas largas simplemente apoyadas)
- t = espesor de la placa
- b = luz entre refuerzos

### 8.2 Pandeo de la viga completa (ELSA)

Para pandeo global de la viga buque:

$$\sigma_{\text{cr,global}} = \frac{\pi^2 \cdot E \cdot I_z}{A \cdot L_{\text{eff}}^2}$$

### 8.3 Factor de seguridad al pandeo

$$FS_{\text{pandeo}} = \frac{\sigma_{\text{cr}}}{\sigma_{\text{aplicada}}} \geq 2.0$$

---

## 9. Estabilidad Transversal — GM

### 9.1 Altura metacéntrica

$$GM = KB + BM - KG$$

**KB (centro de carena al centro de flotación):**
$$KB \approx \frac{T}{2}$$

**BM (radio metacéntrico):**
$$BM = \frac{I_{\text{flota}}}{V} = \frac{L \cdot B^3 / 12}{L \cdot B \cdot T} = \frac{B^2}{12T}$$

**KG (centro de gravedad vertical):**
$$KG = \frac{\sum m_i \cdot z_i}{\sum m_i}$$

### 9.2 Valores de referencia

| Tipo de buque | GM típico [m] | Estabilidad |
|---------------|---------------|-------------|
| Portacontenedores | 0.5 – 1.5 | Moderada |
| Granelero | 0.3 – 0.8 | Baja (peligro de vuelco) |
| Petrolero | 1.0 – 3.0 | Alta (lastre obligatorio) |
| Buque de pasajeros | 0.8 – 2.0 | Alta |

### 9.3 Condiciones de estabilidad en el juego

| GM (m) | Estado | Descripción |
|--------|--------|-------------|
| > 0.30 | VERDE | Estable |
| 0.15 – 0.30 | AMARILLO | Margen reducido |
| < 0.15 | ROJO | Vuelco inminente |
| < 0 | ROJO | Inestable (vuelco) |

---

## 10. Modelo de Daño por Fatiga (Nivel Avanzado)

### 10.1 Regla de Miner

$$D = \sum_{i} \frac{n_i}{N_i}$$

Donde:
- n_i = número de ciclos en el rango de tensión i
- N_i = número de ciclos hasta la falla en ese rango (curva S-N)
- D ≥ 1 → falla por fatiga

### 10.2 Curva S-N para acero naval

$$\log(N) = \log(C) - m \cdot \log(\Delta\sigma)$$

Parámetros típicos (clase F de Lloyd's Register):
- m = 3.0
- log(C) = 12.5

---

## 11. Resumen de Ecuaciones Implementadas en el Prototipo

| # | Ecuación | Variable | Unidad |
|---|----------|----------|--------|
| 1 | w_i = W_total,i / Δx | Carga distribuida | N/m |
| 2 | b_i = B_total × peso_i / Σpesos | Empuje | N/m |
| 3 | V_i = V_{i-1} − (w_i − b_i)·Δx | Fuerza cortante | N |
| 4 | M_i = M_{i-1} + V_i·Δx | Momento flector | N·m |
| 5 | σ = M·y / I_z | Tensión de flexión | Pa |
| 6 | GM = B²/(12T) − KG + T/2 | Altura metacéntrica | m |
| 7 | σ_admisible = σ_y / FS | Límite de seguridad | Pa |

---

*Fin del Modelo Matemático v1.0*
