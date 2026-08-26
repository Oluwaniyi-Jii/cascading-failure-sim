import random
from typing import Any
import networkx as nx


def select_initial_failures(
    G: nx.Graph,
    num_failures: int = 1,
    strategy: str = "target_hub",
    seed: int | None = None
) -> list[int]:
    """Select initial node(s) to fail based on strategy."""
    nodes = list(G.nodes())
    if not nodes or num_failures <= 0:
        return []

    num_failures = min(num_failures, len(nodes))

    if strategy == "target_hub":
        sorted_nodes = sorted(nodes, key=lambda n: G.nodes[n]["load"], reverse=True)
        return sorted_nodes[:num_failures]
    elif strategy == "random":
        rng = random.Random(seed)
        return rng.sample(nodes, num_failures)
    else:
        raise ValueError(f"Unknown initial failure strategy: {strategy}")


def compute_shortest_path_loads(G: nx.Graph) -> dict[int, float]:
    """
    Compute Motter-Lai shortest-path betweenness loads for healthy nodes in graph G.
    Returns dictionary mapping healthy node ID -> unnormalized betweenness flow load.
    """
    healthy_nodes = [n for n, data in G.nodes(data=True) if data.get("status") == "healthy"]
    if not healthy_nodes:
        return {}

    subG = G.subgraph(healthy_nodes)
    bw = nx.betweenness_centrality(subG, normalized=False)
    return bw


def simulate_cascade(
    G: nx.Graph,
    initial_failures: list[int] | int = 1,
    strategy: str = "target_hub",
    redistribution_model: str = "neighbor",
    max_steps: int = 100,
    seed: int | None = None
) -> dict[str, Any]:
    """
    Run iterative load redistribution cascade simulation on graph G until steady state.

    Args:
        G: NetworkX graph with node attributes 'load', 'capacity', 'status'.
        initial_failures: Number of initial node failures or explicit list of node IDs.
        strategy: 'target_hub' or 'random' (used if initial_failures is int).
        redistribution_model: 'neighbor' (local capacity sharing) or 'shortest_path' (Motter-Lai flow re-routing).
        max_steps: Safeguard step limit to prevent infinite loops.
        seed: Random seed for 'random' initial failure selection.

    Returns:
        Dictionary containing cascade history, step count, and final statistics.
    """
    if redistribution_model not in {"neighbor", "shortest_path"}:
        raise ValueError(f"Unknown redistribution_model: {redistribution_model}. Choose 'neighbor' or 'shortest_path'.")

    graph = G.copy()

    if isinstance(initial_failures, int):
        failed_targets = select_initial_failures(graph, num_failures=initial_failures, strategy=strategy, seed=seed)
    else:
        failed_targets = list(initial_failures)

    history = []
    failed_set: set[int] = set()

    if redistribution_model == "shortest_path":
        init_bw_norm = nx.betweenness_centrality(graph, normalized=True)
        for n in graph.nodes():
            graph.nodes[n]["_init_bw_norm"] = init_bw_norm.get(n, 0.0)

    newly_failed = set(failed_targets)
    for n in newly_failed:
        graph.nodes[n]["status"] = "failed"
        failed_set.add(n)

    history.append({
        "step": 0,
        "new_failures": list(newly_failed),
        "total_failures": len(failed_set),
    })

    step = 0
    while newly_failed and step < max_steps:
        step += 1
        current_new_failures: set[int] = set()

        if redistribution_model == "neighbor":
            for f_node in newly_failed:
                shed_load = graph.nodes[f_node]["load"]
                graph.nodes[f_node]["load"] = 0.0

                healthy_neighbors = [
                    nbr for nbr in graph.neighbors(f_node)
                    if graph.nodes[nbr]["status"] == "healthy"
                ]

                if healthy_neighbors and shed_load > 0:
                    rem_capacities = {
                        nbr: max(0.0, graph.nodes[nbr]["capacity"] - graph.nodes[nbr]["load"])
                        for nbr in healthy_neighbors
                    }
                    total_rem = sum(rem_capacities.values())

                    for nbr in healthy_neighbors:
                        if total_rem > 0:
                            share = shed_load * (rem_capacities[nbr] / total_rem)
                        else:
                            share = shed_load / len(healthy_neighbors)

                        graph.nodes[nbr]["load"] += share

        elif redistribution_model == "shortest_path":
            healthy_nodes = [n for n in graph.nodes() if graph.nodes[n]["status"] == "healthy"]
            if healthy_nodes:
                subG = graph.subgraph(healthy_nodes)
                curr_bw_norm = nx.betweenness_centrality(subG, normalized=True)
                curr_bw_unnorm = nx.betweenness_centrality(subG, normalized=False)

                for n in healthy_nodes:
                    b_init = graph.nodes[n]["_init_bw_norm"]
                    l_init = graph.nodes[n]["initial_load"]
                    b_curr_n = curr_bw_norm.get(n, 0.0)

                    if b_init > 1e-6:
                        graph.nodes[n]["load"] = l_init * (b_curr_n / b_init)
                    else:
                        graph.nodes[n]["load"] = l_init + curr_bw_unnorm.get(n, 0.0)

        for node in graph.nodes():
            if graph.nodes[node]["status"] == "healthy":
                if graph.nodes[node]["load"] > graph.nodes[node]["capacity"]:
                    graph.nodes[node]["status"] = "failed"
                    if redistribution_model == "shortest_path":
                        graph.nodes[node]["load"] = 0.0
                    current_new_failures.add(node)
                    failed_set.add(node)

        newly_failed = current_new_failures

        history.append({
            "step": step,
            "new_failures": list(newly_failed),
            "total_failures": len(failed_set),
        })

    total_nodes = graph.number_of_nodes()
    failed_pct = (len(failed_set) / total_nodes) * 100.0 if total_nodes > 0 else 0.0

    return {
        "graph": graph,
        "steps": step,
        "total_failures": len(failed_set),
        "failure_percentage": failed_pct,
        "history": history,
        "initial_failed_nodes": failed_targets,
        "redistribution_model": redistribution_model,
    }
