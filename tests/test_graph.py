import pytest
from cascading_sim.graph import generate_network, SUPPORTED_TOPOLOGIES


def test_supported_topologies():
    num_nodes = 50
    alpha = 0.25
    
    for topo in SUPPORTED_TOPOLOGIES:
        G = generate_network(topology=topo, num_nodes=num_nodes, alpha=alpha, seed=42)
        assert len(G.nodes) == num_nodes
        assert G.number_of_edges() > 0
        
        for node in G.nodes():
            attrs = G.nodes[node]
            assert attrs["status"] == "healthy"
            assert attrs["capacity"] == pytest.approx((1.0 + alpha) * attrs["load"])


def test_invalid_topology():
    with pytest.raises(ValueError, match="Unknown topology"):
        generate_network(topology="invalid_topo")


def test_load_strategies():
    for strat in ["degree", "betweenness", "uniform"]:
        G = generate_network(topology="barabasi_albert", num_nodes=30, load_strategy=strat, seed=42)
        assert len(G.nodes) == 30
        for node in G.nodes():
            assert G.nodes[node]["load"] >= 0

