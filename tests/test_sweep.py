import pytest
from cascading_sim.sweep import run_alpha_sweep


def test_alpha_sweep_execution():
    alphas = [0.05, 0.25, 0.50]
    results = run_alpha_sweep(
        alpha_values=alphas,
        topology="barabasi_albert",
        num_nodes=30,
        num_trials=2,
        base_seed=42,
    )

    assert len(results["alpha"]) == 3
    assert len(results["failed_pct_mean"]) == 3
    assert len(results["giant_cc_mean"]) == 3

    # Typically, higher alpha (tolerance) yields lower failure percentage
    assert results["failed_pct_mean"][0] >= results["failed_pct_mean"][-1]
