from pathlib import Path
import pytest
from cascading_sim.graph import generate_network
from cascading_sim.engine import simulate_cascade
from cascading_sim.sweep import run_alpha_sweep
from cascading_sim.visualize import plot_phase_transition, plot_network_state


def test_plot_phase_transition(tmp_path):
    sweep_res = run_alpha_sweep(
        alpha_values=[0.05, 0.25],
        topology="barabasi_albert",
        num_nodes=20,
        num_trials=2,
        base_seed=42,
    )
    out_png = tmp_path / "phase_plot.png"
    fig = plot_phase_transition(sweep_res, save_path=str(out_png))

    assert fig is not None
    assert Path(out_png).exists()


def test_plot_network_state(tmp_path):
    G = generate_network(topology="barabasi_albert", num_nodes=20, seed=42)
    sim_res = simulate_cascade(G, initial_failures=1, strategy="target_hub", seed=42)

    out_png = tmp_path / "network_plot.png"
    fig = plot_network_state(sim_res["graph"], save_path=str(out_png))

    assert fig is not None
    assert Path(out_png).exists()
