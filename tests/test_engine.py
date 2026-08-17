import pytest
from cascading_sim.graph import generate_network
from cascading_sim.engine import simulate_cascade, select_initial_failures


def test_initial_failure_selection():
    G = generate_network(topology="barabasi_albert", num_nodes=30, seed=42)
    hubs = select_initial_failures(G, num_failures=3, strategy="target_hub")
    assert len(hubs) == 3
    
    # Hubs should have highest load
    loads = [G.nodes[n]["load"] for n in G.nodes()]
    assert G.nodes[hubs[0]]["load"] == max(loads)


def test_high_tolerance_no_cascade():
    # High alpha = high resilience safety buffer
    G = generate_network(topology="erdos_renyi", num_nodes=40, alpha=5.0, seed=42)
    res = simulate_cascade(G, initial_failures=1, strategy="random", seed=42)
    
    assert res["total_failures"] == 1
    assert res["steps"] == 1


def test_low_tolerance_cascade_propagation():
    # Low alpha = fragile system near critical threshold
    G = generate_network(topology="barabasi_albert", num_nodes=50, alpha=0.01, seed=42)
    res = simulate_cascade(G, initial_failures=1, strategy="target_hub", seed=42)
    
    assert res["total_failures"] > 1
    assert res["steps"] >= 1
    assert len(res["history"]) == res["steps"] + 1
