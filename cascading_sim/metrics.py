import networkx as nx


def compute_giant_component_ratio(G: nx.Graph) -> float:
    """
    Calculate the size of the largest connected component (giant component)
    among surviving healthy nodes, relative to the total initial node count.
    """
    total_nodes = G.number_of_nodes()
    if total_nodes == 0:
        return 0.0

    healthy_nodes = [n for n in G.nodes() if G.nodes[n].get("status") == "healthy"]
    if not healthy_nodes:
        return 0.0

    subgraph = G.subgraph(healthy_nodes)
    if subgraph.number_of_nodes() == 0:
        return 0.0

    largest_cc = max(nx.connected_components(subgraph), key=len)
    return float(len(largest_cc) / total_nodes)


def compute_cascade_metrics(sim_result: dict) -> dict:
    """
    Extract key complexity metrics from a cascade simulation result.
    """
    G = sim_result["graph"]
    total_nodes = G.number_of_nodes()
    failed_count = sim_result["total_failures"]
    failed_pct = sim_result["failure_percentage"]
    steps = sim_result["steps"]
    giant_cc_ratio = compute_giant_component_ratio(G)

    cascade_speed = float(failed_count / steps) if steps > 0 else 0.0

    return {
        "total_nodes": total_nodes,
        "failed_nodes": failed_count,
        "failed_percentage": failed_pct,
        "giant_component_ratio": giant_cc_ratio,
        "steps_to_converge": steps,
        "cascade_speed": cascade_speed,
    }
