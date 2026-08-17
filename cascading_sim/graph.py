import networkx as nx

SUPPORTED_TOPOLOGIES = {"erdos_renyi", "barabasi_albert", "watts_strogatz"}
SUPPORTED_LOAD_STRATEGIES = {"degree", "betweenness", "uniform"}


def generate_network(
    topology: str = "barabasi_albert",
    num_nodes: int = 100,
    alpha: float = 0.2,
    load_strategy: str = "degree",
    seed: int | None = None,
    **kwargs
) -> nx.Graph:
    """Generate network graph with capacity and initial load assignments."""
    topo = topology.lower().strip()
    if topo not in SUPPORTED_TOPOLOGIES:
        raise ValueError(f"Unknown topology: {topology}. Choose from {SUPPORTED_TOPOLOGIES}")

    strat = load_strategy.lower().strip()
    if strat not in SUPPORTED_LOAD_STRATEGIES:
        raise ValueError(f"Unknown load strategy: {load_strategy}. Choose from {SUPPORTED_LOAD_STRATEGIES}")

    if topo == "erdos_renyi":
        p = kwargs.get("p", 0.05)
        G = nx.erdos_renyi_graph(n=num_nodes, p=p, seed=seed)
    elif topo == "barabasi_albert":
        m = kwargs.get("m", min(2, num_nodes - 1))
        G = nx.barabasi_albert_graph(n=num_nodes, m=m, seed=seed)
    elif topo == "watts_strogatz":
        k = kwargs.get("k", min(4, num_nodes - 1))
        p = kwargs.get("p", 0.1)
        G = nx.watts_strogatz_graph(n=num_nodes, k=k, p=p, seed=seed)

    if strat == "degree":
        loads = {n: float(d) for n, d in G.degree()}
    elif strat == "betweenness":
        loads = nx.betweenness_centrality(G)
    else:
        loads = {n: 1.0 for n in G.nodes()}

    for node in G.nodes():
        l0 = float(loads[node])
        G.nodes[node]["load"] = l0
        G.nodes[node]["initial_load"] = l0
        G.nodes[node]["capacity"] = (1.0 + alpha) * l0
        G.nodes[node]["status"] = "healthy"

    return G

