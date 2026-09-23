# 🚢 Ship Resistance Game

**Interactive Educational Game of Ship Longitudinal Strength and Structural Failure Prevention**

[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![Canvas](https://img.shields.io/badge/Canvas-000000?style=flat&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/Version-1.0-green.svg)]()

> Interactive educational game where naval architecture students learn longitudinal ship strength by distributing cargo and ballast — with real-time physics, traffic-light alerts, and animated sea states.

---

## 📖 Description

**Ship Resistance Game** is a fully interactive, visually rich HTML5/Canvas game that teaches ship longitudinal strength and structural failure prevention during loading and unloading operations.

The player takes on the role of a chief naval engineer and must:
- Properly distribute cargo between holds using drag-and-drop sliders
- Adjust ballast to maintain stability
- Keep structural stresses within safe limits
- Navigate in different sea states without compromising hull integrity
- Learn from real historical maritime disasters (MV Kurdistan, SS Edmund Fitzgerald, MV Prestige)

### Key Features

- 🎮 **Interactive gameplay** — drag sliders to load/unload, run simulations, see results in real time
- 🌊 **Animated sea** — waves get rougher with higher sea states, ship rocks with the swell
- 📊 **Real-time metrics** — max stress, bending moment, shear force, safety factor, GM
- 🚦 **Traffic light alerts** — sections glow green/yellow/red based on stress levels
- 💥 **Visual feedback** — containers, ballast water, stress zones all rendered on the ship
- 📚 **Historical cases** — rebuild the conditions that caused real maritime accidents
- 🎯 **Challenge mode** — keep all sections green in storm conditions
- 💻 **No installation needed** — runs in any modern browser

---

## 🚀 Quick Start

**Play now:**

```bash
# Open in browser
open game.html        # macOS
start game.html       # Windows
xdg-open game.html    # Linux
```

Or serve locally:

```bash
python -m http.server 8000
# Open http://localhost:8000/game.html
```

---

## 🎮 Game Modes

| Mode | Description | Objective |
|------|-------------|-----------|
| **Tutorial / Puzzle** | Step-by-step guided learning | Master V(x), M(x), σ(x) |
| **Realistic Simulator** | Free experimentation | Safe and efficient operations |
| **Historical Cases** | Reconstruction of real accidents | Learn from actual maritime disasters |

---

## 📋 Requirements

- **Python:** 3.8 or higher
- **pip:** Python package manager
- **matplotlib:** for graphical visualization (optional but recommended)
- **numpy:** matplotlib dependency
- **streamlit:** for the web app interface

### Operating System
- Windows 10/11 ✅
- macOS 10.15+ ✅
- Linux (Ubuntu 20.04+) ✅

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/nantonelli94/ship-resistance-game.git
cd ship-resistance-game
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
```
matplotlib>=3.5.0
numpy>=1.21.0
streamlit>=1.20.0
plotly>=5.10.0
pandas>=1.5.0
```

### 4. Run the Streamlit app

```bash
streamlit run app.py
```

Or run the CLI prototype:

```bash
python prototypes/ship_simulator.py
```

---

## 🚀 Quick Start

### Streamlit Web App

```bash
$ streamlit run app.py
```

The app opens in your browser with:
- **Left sidebar:** controls to adjust cargo/ballast, select ship and sea state
- **Main panel:** interactive results with status indicators, metrics, and stress diagrams
- **Interactive Plotly charts** showing V(x), M(x), and σ(x)
- **Stability analysis** with IMO criteria verification

### Python API

```python
from src.core.physics_engine import PhysicsEngine
from src.models.ship_config import ShipConfig

# Create ship configuration
ship = ShipConfig(
    name="My Ship",
    length_overall=200.0,
    beam=32.0,
    depth=18.0,
    draft_design=10.0,
    displacement=45_000_000.0,
    moment_of_inertia_zz=12.5,
    y_deck=8.5,
    y_keel=-9.0,
)

# Add sections...

# Create physics engine
engine = PhysicsEngine(ship)

# Run simulation
result = engine.compute_shear_and_moment()

print(f"Status: {result.status}")
print(f"Max stress: {result.max_stress/1e6:.1f} MPa")
print(f"GM: {result.gm_estimate:.3f} m")
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [GAME_DESIGN_DOCUMENT.md](docs/GAME_DESIGN_DOCUMENT.md) | Game design: mechanics, modes, progression |
| [MATHEMATICAL_MODEL.md](docs/MATHEMATICAL_MODEL.md) | Mathematical model and physics implemented |
| [SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) | System architecture and modules |

---

## 🧪 Tests

Run unit tests:

```bash
python -m pytest tests/ -v
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. **Commit** your changes (`git commit -am 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/new-feature`)
5. Open a **Pull Request**

### Style Guide
- Code in **PEP 8** (Python)
- Comments in English or Spanish
- Google-style docstrings
- Tests mandatory for new features

---

## 📁 Project Structure

```
ship-resistance-game/
├── app.py                       # Streamlit web app (NEW)
├── docs/                        # Documentation
│   ├── GAME_DESIGN_DOCUMENT.md
│   ├── MATHEMATICAL_MODEL.md
│   └── SYSTEM_ARCHITECTURE.md
├── src/                         # Source code
│   ├── core/                    # Simulation engine
│   ├── models/                  # Data models
│   ├── ui/                      # User interface (CLI + plotter)
│   ├── modes/                   # Game modes
│   ├── data/                    # Data and presets
│   └── utils/                   # Utilities
├── prototypes/                  # Executable prototypes
│   └── ship_simulator.py
├── tests/                       # Unit tests
├── assets/                      # Graphical resources
├── requirements.txt             # Dependencies
├── .gitignore
└── README.md
```

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Nicolás Antonelli**
- GitHub: [@nantonelli94](https://github.com/nantonelli94)
- UTN FRMDP — Marine Engineering Professor & Researcher
- PhD Candidate (UNMDP/CONICET) — Ship Hydrodynamics

---

## 🙏 Acknowledgments

- Based on the fundamentals of **Ship Theory II: Propulsion**
- References: ITTC, Lloyd's Register, IMO
- To the naval architecture community for shared knowledge

---

<div align="center">

⚓ **Fair winds, engineer!** ⚓

</div>
