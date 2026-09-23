# app.py
"""
Ship Resistance Game — Interactive Streamlit App
================================================

Educational game where naval architecture students learn longitudinal
ship strength by distributing cargo and ballast.

Run with: streamlit run app.py
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.physics_engine import PhysicsEngine
from core.load_manager import LoadManager
from core.alert_system import AlertSystem
from core.stability_checker import StabilityChecker
from data.ship_presets import SHIP_PRESETS, get_ship_preset
from utils.constants import (
    MAX_ALLOWED_STRESS,
    GM_MIN_GREEN,
    GM_MIN_YELLOW,
    SEA_STATE_FACTORS,
    SEA_STATE_DESCRIPTIONS,
)


# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Ship Resistance Game",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #003153;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-green { color: #28a745; font-weight: bold; font-size: 1.3rem; }
    .status-yellow { color: #ffc107; font-weight: bold; font-size: 1.3rem; }
    .status-red { color: #dc3545; font-weight: bold; font-size: 1.3rem; }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-red { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    .alert-yellow { background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
    .alert-green { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize Streamlit session state."""
    if "ship" not in st.session_state:
        st.session_state.ship = get_ship_preset("containership")
    if "result" not in st.session_state:
        st.session_state.result = None
    if "simulation_run" not in st.session_state:
        st.session_state.simulation_run = False


def create_shear_moment_plot(result, ship):
    """Create interactive shear force and bending moment plots."""
    if not result or not result.sections:
        return None

    x = [s.x for s in result.sections]
    shear = [s.shear_force / 1000.0 for s in result.sections]
    moment = [s.bending_moment / 1e6 for s in result.sections]
    stress_deck = [s.stress_deck / 1e6 for s in result.sections]
    stress_keel = [abs(s.stress_keel) / 1e6 for s in result.sections]

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        subplot_titles=("Shear Force V(x)", "Bending Moment M(x)", "Bending Stress σ(x)"),
        vertical_spacing=0.08,
    )

    # Shear force
    fig.add_trace(
        go.Scatter(x=x, y=shear, fill="tozeroy", fillcolor="rgba(70,130,180,0.3)",
                   line=dict(color="steelblue", width=2), name="V(x) [kN]"),
        row=1, col=1,
    )
    fig.add_hline(y=0, line_dash="solid", line_color="black", row=1, col=1)

    # Bending moment
    fig.add_trace(
        go.Scatter(x=x, y=moment, fill="tozeroy", fillcolor="rgba(255,140,0,0.3)",
                   line=dict(color="darkorange", width=2), name="M(x) [MN·m]"),
        row=2, col=1,
    )
    fig.add_hline(y=0, line_dash="solid", line_color="black", row=2, col=1)

    # Stress
    fig.add_trace(
        go.Scatter(x=x, y=stress_deck, line=dict(color="green", width=2),
                   name="Deck σ [MPa]"),
        row=3, col=1,
    )
    fig.add_trace(
        go.Scatter(x=x, y=stress_keel, line=dict(color="purple", width=2),
                   name="Keel σ [MPa]"),
        row=3, col=1,
    )
    fig.add_hline(y=MAX_ALLOWED_STRESS/1e6, line_dash="dash", line_color="red",
                   annotation_text="Limit", row=3, col=1)
    fig.add_hline(y=-MAX_ALLOWED_STRESS/1e6, line_dash="dash", line_color="red", row=3, col=1)

    fig.update_xaxes(title_text="x [m] (from bow)", row=3, col=1)
    fig.update_layout(height=700, showlegend=True, template="plotly_white",
                       title_text=f"Simulation: {ship.name} — Status: {result.status}")

    return fig


def create_ship_visualization(ship, load_manager):
    """Create a schematic ship visualization showing load distribution."""
    sections = ship.sections
    n = len(sections)

    fig = go.Figure()

    # Ship hull outline (simplified)
    max_cap = max(s.capacity for s in sections) / 1000.0

    for i, section in enumerate(sections):
        x_pos = section.x_center
        load_val = section.current_load / 1000.0
        capacity = section.capacity / 1000.0
        fill_pct = load_val / capacity if capacity > 0 else 0

        color = "#28a745" if section.is_ballast else "#007bff"
        if section.is_ballast:
            color = "#ffc107"

        # Draw section as a bar
        fig.add_trace(go.Bar(
            x=[section.length * 0.8],
            y=[load_val],
            base=[0],
            width=section.length * 0.8,
            marker_color=color,
            marker_opacity=0.7,
            name=section.name,
            showlegend=False,
            hovertemplate=f"<b>{section.name}</b><br>Load: {load_val:.0f} kN<br>"
                         f"Capacity: {capacity:.0f} kN<br>Fill: {fill_pct*100:.0f}%<extra></extra>",
        ))

    fig.update_layout(
        title="Ship Load Distribution (click sections to adjust)",
        xaxis_title="Section",
        yaxis_title="Load (kN)",
        barmode="stack",
        template="plotly_white",
        height=300,
    )

    return fig


# ── Main App ─────────────────────────────────────────────────
def main():
    init_session_state()

    # Header
    st.markdown('<p class="main-header">⚓ Ship Resistance Game</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Learn longitudinal ship strength by distributing cargo and ballast</p>',
        unsafe_allow_html=True,
    )

    # Sidebar controls
    with st.sidebar:
        st.header("🎮 Controls")

        # Ship selection
        st.subheader("Ship Selection")
        ship_choice = st.selectbox(
            "Choose a ship preset",
            options=list(SHIP_PRESETS.keys()),
            index=list(SHIP_PRESETS.keys()).index("containership"),
            format_func=lambda x: x.replace("_", " ").title(),
        )

        if st.button("Change Ship", key="change_ship"):
            st.session_state.ship = get_ship_preset(ship_choice)
            st.session_state.result = None
            st.session_state.simulation_run = False
            st.rerun()

        ship = st.session_state.ship

        # Sea state
        st.subheader("Sea State")
        sea_state = st.selectbox(
            "Sea state (Douglas scale)",
            options=list(SEA_STATE_FACTORS.keys()),
            index=ship.sea_state,
            format_func=lambda x: f"State {x}: {SEA_STATE_DESCRIPTIONS.get(x, 'Unknown')}",
        )
        ship.sea_state = sea_state

        st.markdown("---")

        # Load controls
        st.subheader("📦 Load Management")
        load_manager = LoadManager(ship)

        # Cargo sections
        cargo_sections = load_manager.get_cargo_sections()
        if cargo_sections:
            st.markdown("**Cargo Sections**")
            for i, section in enumerate(cargo_sections):
                current = section.current_load / 1000.0
                capacity = section.capacity / 1000.0
                new_val = st.slider(
                    f"{section.name}",
                    min_value=0.0,
                    max_value=capacity,
                    value=min(current, capacity),
                    step=capacity / 100 if capacity > 0 else 1.0,
                    key=f"cargo_{i}",
                )
                section.set_load(new_val * 1000.0)

        # Ballast sections
        ballast_sections = load_manager.get_ballast_sections()
        if ballast_sections:
            st.markdown("**Ballast Tanks**")
            for i, section in enumerate(ballast_sections):
                current = section.current_load / 1000.0
                capacity = section.capacity / 1000.0
                new_val = st.slider(
                    f"{section.name}",
                    min_value=0.0,
                    max_value=capacity,
                    value=min(current, capacity),
                    step=capacity / 100 if capacity > 0 else 1.0,
                    key=f"ballast_{i}",
                )
                section.set_load(new_val * 1000.0)

        st.markdown("---")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            run_sim = st.button("🚀 Run Simulation", type="primary", use_container_width=True)
        with col2:
            reset = st.button("🔄 Reset", use_container_width=True)

        if reset:
            load_manager.reset_all_loads()
            st.session_state.result = None
            st.session_state.simulation_run = False
            st.rerun()

    # Run simulation
    if run_sim:
        engine = PhysicsEngine(ship)
        alert_sys = AlertSystem()
        result = engine.compute_shear_and_moment()
        result = alert_sys.evaluate(result)
        st.session_state.result = result
        st.session_state.simulation_run = True

    # Results area
    if st.session_state.simulation_run and st.session_state.result:
        result = st.session_state.result
        ship = st.session_state.ship

        # Status indicator
        st.markdown("---")
        status_color = {
            "VERDE": "status-green",
            "AMARILLO": "status-yellow",
            "ROJO": "status-red",
        }.get(result.status, "status-green")

        status_emoji = {"VERDE": "🟢", "AMARILLO": "🟡", "ROJO": "🔴"}.get(result.status, "⚪")

        st.markdown(
            f"### Simulation Status: {status_emoji} <span class='{status_color}'>{result.status}</span>",
            unsafe_allow_html=True,
        )

        # Alert boxes
        if result.warnings:
            st.markdown("#### ⚠️ Alerts")
            for warning in result.warnings:
                alert_class = "alert-red" if "ROJO" in warning or "FLUENCIA" in warning or "VUELO" in warning else "alert-yellow"
                st.markdown(
                    f'<div class="alert-box {alert_class}">{warning}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div class="alert-box alert-green">✅ All systems within safe limits</div>',
                unsafe_allow_html=True,
            )

        # Metrics
        st.markdown("#### 📊 Key Metrics")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric("Max Stress", f"{result.max_stress/1e6:.2f} MPa",
                      delta=f"{(result.max_stress/MAX_ALLOWED_STRESS)*100:.1f}% of limit",
                      delta_color="inverse")
        with mcol2:
            st.metric("Metacentric Height (GM)", f"{result.gm_estimate:.3f} m",
                      delta="Safe" if result.gm_estimate >= GM_MIN_GREEN else "Unsafe",
                      delta_color="normal" if result.gm_estimate >= GM_MIN_GREEN else "inverse")
        with mcol3:
            max_moment = max(abs(s.bending_moment) for s in result.sections) / 1e6
            st.metric("Max Bending Moment", f"{max_moment:.2f} MN·m")
        with mcol4:
            max_shear = max(abs(s.shear_force) for s in result.sections) / 1000
            st.metric("Max Shear Force", f"{max_shear:.1f} kN")

        # Stability check
        st.markdown("#### 🛟 Stability Analysis")
        stability = StabilityChecker(ship)
        gm = stability.compute_gm()
        st.progress(min(gm / 1.0, 1.0), text=f"GM = {gm:.3f} m (minimum safe: {GM_MIN_GREEN} m)")

        # IMO criteria
        criteria = stability.check_imo_criteria()
        ccol1, ccol2, ccol3 = st.columns(3)
        with ccol1:
            status_icon = "✅" if criteria["GM_min"]["pass"] else "❌"
            st.markdown(f"{status_icon} GM ≥ 0.15 m: **{criteria['GM_min']['value']:.3f} m**")
        with ccol2:
            status_icon = "✅" if criteria["GZ_max"]["pass"] else "❌"
            st.markdown(f"{status_icon} GZ_max ≥ 0.20 m: **{criteria['GZ_max']['value']:.3f} m**")
        with ccol3:
            status_icon = "✅" if criteria["Area_0_30"]["pass"] else "❌"
            st.markdown(f"{status_icon} Area 0-30° ≥ 0.055 m·rad: **{criteria['Area_0_30']['value']:.4f}**")

        # Plots
        st.markdown("#### 📈 Diagrams")
        fig = create_shear_moment_plot(result, ship)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Section details table
        with st.expander("📋 Section Details"):
            import pandas as pd
            data = []
            for s in result.sections:
                data.append({
                    "x (m)": f"{s.x:.1f}",
                    "V (kN)": f"{s.shear_force/1000:.1f}",
                    "M (MN·m)": f"{s.bending_moment/1e6:.2f}",
                    "σ_deck (MPa)": f"{s.stress_deck/1e6:.2f}",
                    "σ_keel (MPa)": f"{s.stress_keel/1e6:.2f}",
                    "σ_max (MPa)": f"{s.stress_max/1e6:.2f}",
                    "Status": s.status,
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    else:
        # Welcome / instructions
        st.info("👈 Adjust loads in the sidebar and click **Run Simulation** to start!")

        # Ship info
        ship = st.session_state.ship
        st.markdown(f"### Current Ship: {ship.name}")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Length", f"{ship.length_overall:.0f} m")
        col2.metric("Beam", f"{ship.beam:.0f} m")
        col3.metric("Depth", f"{ship.depth:.0f} m")
        col4.metric("Draft", f"{ship.draft_design:.0f} m")

        # Instructions
        st.markdown("""
        ### How to Play
        1. **Select a ship** from the sidebar (Container Ship, Bulk Carrier, or VLCC Tanker)
        2. **Adjust cargo and ballast** using the sliders — try to keep stresses low!
        3. **Change sea state** to see how weather affects structural loads
        4. **Run the simulation** and analyze the results
        5. **Goal**: Keep all sections in the GREEN zone — avoid YELLOW (caution) and RED (failure)!

        ### Theory
        This simulator uses the **Euler-Bernoulli beam theory** to calculate:
        - **V(x)** — Shear force distribution
        - **M(x)** — Bending moment distribution
        - **σ(x)** — Bending stress at deck and keel

        The ship is modeled as a **floating beam** with distributed weight and buoyancy.
        """)


if __name__ == "__main__":
    main()
