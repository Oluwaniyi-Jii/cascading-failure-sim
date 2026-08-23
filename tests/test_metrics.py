import pytest
import networkx as nx
from cascading_sim.graph import generate_network
from cascading_sim.engine import simulate_cascade
from cascading_sim.metrics import compute_giant_component_ratio, compute_cascade_metrics


def test_giant_component_ratio():
    G = generate_network(topology="barabasi_albert", num_nodes=20, seed=42)
    # Fully healthy connected graph -> giant component ratio should be 1.0
    ratio = compute_giant_component_ratio(G)
    assert ratio == pytest.approx(1.0)

    # Fail all nodes -> giant component ratio should be 0.0
    for n in G.nodes():
        G.nodes[n]["status"] = "failed"
    assert compute_giant_component_ratio(G) == 0.0


def test_cascade_metrics():
    G = generate_network(topology="erdos_renyi", num_nodes=30, alpha=0.1, seed=42)
    res = simulate_cascade(G, initial_failures=1, strategy="target_hub", seed=42)
    metrics = compute_cascade_metrics(res)

    assert "total_nodes" in metrics
    assert "failed_percentage" in metrics
    assert "giant_component_ratio" in metrics
    assert "cascade_speed" in metrics
    assert 0.0 <= metrics["giant_component_ratio"] <= 1.0
    assert 0.0 <= metrics["failed_percentage"] <= 100.0
