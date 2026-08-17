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
        # Sort nodes by current load (or degree) descending
        sorted_nodes = sorted(nodes, key=lambda n: G.nodes[n]["load"], reverse=True)
        return sorted_nodes[:num_failures]
    elif strategy == "random":
        rng = random.Random(seed)
        return rng.sample(nodes, num_failures)
    else:
        raise ValueError(f"Unknown initial failure strategy: {strategy}")


def simulate_cascade(
    G: nx.Graph,
    initial_failures: list[int] | int = 1,
    strategy: str = "target_hub",
    max_steps: int = 100,
    seed: int | None = None
) -> dict[str, Any]:
    """
    Run iterative load redistribution cascade simulation on graph G until steady state.

    Args:
        G: NetworkX graph with node attributes 'load', 'capacity', 'status'.
        initial_failures: Number of initial node failures or explicit list of node IDs.
        strategy: 'target_hub' or 'random' (used if initial_failures is int).
        max_steps: Safeguard step limit to prevent infinite loops.
        seed: Random seed for 'random' initial failure selection.

    Returns:
        Dictionary containing cascade history, step count, and final statistics.
    """
    # Create a deep copy so original graph isn't mutated unpredictably
    graph = G.copy()

    # Determine initial failed nodes
    if isinstance(initial_failures, int):
        failed_targets = select_initial_failures(graph, num_failures=initial_failures, strategy=strategy, seed=seed)
    else:
        failed_targets = list(initial_failures)

    history = []
    failed_set: set[int] = set()

    # Apply initial failure attack
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

        # Redistribute load from nodes that failed in the previous step
        for f_node in newly_failed:
            shed_load = graph.nodes[f_node]["load"]
            graph.nodes[f_node]["load"] = 0.0

            # Find healthy neighbors
            healthy_neighbors = [
                nbr for nbr in graph.neighbors(f_node)
                if graph.nodes[nbr]["status"] == "healthy"
            ]

            if healthy_neighbors and shed_load > 0:
                # Compute weight per neighbor based on remaining capacity
                rem_capacities = {
                    nbr: max(0.0, graph.nodes[nbr]["capacity"] - graph.nodes[nbr]["load"])
                    for nbr in healthy_neighbors
                }
                total_rem = sum(rem_capacities.values())

                for nbr in healthy_neighbors:
                    if total_rem > 0:
                        share = shed_load * (rem_capacities[nbr] / total_rem)
                    else:
                        # Equal distribution if all remaining capacities are 0
                        share = shed_load / len(healthy_neighbors)

                    graph.nodes[nbr]["load"] += share

        # Evaluate overloaded nodes across the network
        for node in graph.nodes():
            if graph.nodes[node]["status"] == "healthy":
                if graph.nodes[node]["load"] > graph.nodes[node]["capacity"]:
                    graph.nodes[node]["status"] = "failed"
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
    }
